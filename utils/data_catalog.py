import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Union
from tqdm import tqdm
import json

def LoadDataset(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load various tabular data formats into a pandas DataFrame.
    Supports CSV, Excel, and other common formats.
    
    Args:
        file_path (str or Path): Path to the dataset file.
    
    Returns:
        pd.DataFrame: Loaded DataFrame.
        
    Raises:
        ValueError: If the file format is unsupported.
    """
    file_path = Path(file_path)
    if file_path.suffix.lower() == '.csv':
        return pd.read_csv(file_path)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

def GetDatasetProfile(df: pd.DataFrame, output_format: str = 'markdown') -> Union[str, Dict[str, Any]]:
    """
    Create a comprehensive profile of the dataset including statistics, metadata, and samples.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        output_format (str): 'markdown', 'natural_language', or 'json'.
    
    Returns:
        Union[str, Dict[str, Any]]: Formatted string containing dataset profile in the specified format
                                    or a dictionary if 'json' is selected.
    
    Raises:
        ValueError: If an unsupported output format is specified.
    """
    
    profile = {}
    
    for col in tqdm(df.columns,
                   desc=f"Processing {len(df.columns)} columns",
                   bar_format="{desc:>30}{postfix: <1} {bar}|{n_fmt:>4}/{total_fmt:<4}",
                   colour="green"):
        # Get non-null sample value
        sample_series = df[col].dropna()
        sample_value = sample_series.iloc[0] if not sample_series.empty else None
        
        # Convert sample_value to appropriate type for JSON compatibility
        if isinstance(sample_value, (np.floating, float)):
            sample_value = float(f"{sample_value:.2f}")
        elif isinstance(sample_value, (np.integer, int)):
            sample_value = int(sample_value)
        elif isinstance(sample_value, pd.Timestamp):
            sample_value = sample_value.isoformat()
        else:
            sample_value = str(sample_value) if sample_value is not None else None
        
        col_stats = {
            'dtype': str(df[col].dtype),
            'sample': sample_value,
            'total_count': int(len(df[col])),
            'null_count': int(df[col].isna().sum()),
            'null_percentage': f"{(df[col].isna().sum() / len(df[col])) * 100:.1f}%",
            'unique_count': int(df[col].nunique(dropna=True))
        }
        
        # Add numerical statistics if applicable
        if pd.api.types.is_numeric_dtype(df[col]):
            col_stats.update({
                'mean': round(df[col].mean(), 2) if not df[col].dropna().empty else None,
                'median': round(df[col].median(), 2) if not df[col].dropna().empty else None,
                'std': round(df[col].std(), 2) if not df[col].dropna().empty else None,
                'min': round(df[col].min(), 2) if not df[col].dropna().empty else None,
                'max': round(df[col].max(), 2) if not df[col].dropna().empty else None
            })
        
        # Check for various null representations
        null_variants = ['NA', 'Na', 'na', 'NULL', 'Null', 'null', 'NAN', 'Nan', 'nan']
        if df[col].dtype == 'object':
            null_like_count = df[col].isin(null_variants).sum()
            if null_like_count > 0:
                col_stats['alternative_null_count'] = int(null_like_count)
        
        profile[col] = col_stats
    
    if output_format == 'markdown':
        return _format_markdown(profile)
    elif output_format == 'natural_language':
        return _format_natural_language(profile)
    elif output_format == 'json':
        return profile  # Returning the dictionary directly
    else:
        raise ValueError("Unsupported output format. Choose from 'markdown', 'natural_language', or 'json'.")

def _format_markdown(profile: Dict[str, Any]) -> str:
    """Format profile as markdown table"""
    # Header section
    md = f"""
# Dataset Profile
Total columns: {len(profile)}

## Column Details
"""
    
    # Main table
    md += "| Column Name | Data Type | Sample Value | Stats | Additional Info |\n"
    md += "|------------|-----------|--------------|-------|------------------|\n"
    
    for col, stats in profile.items():
        # Basic stats for all columns
        basic_stats = (f"Total: {stats['total_count']}, "
                      f"Nulls: {stats['null_count']} ({stats['null_percentage']}), "
                      f"Unique: {stats['unique_count']}")
        
        # Additional info for numeric columns
        add_info = []
        if 'mean' in stats and stats['mean'] is not None:
            add_info.extend([
                f"Mean: {stats['mean']}",
                f"Median: {stats['median']}",
                f"Range: [{stats['min']}, {stats['max']}]"
            ])
        
        if 'alternative_null_count' in stats:
            add_info.append(f"Alternative nulls: {stats['alternative_null_count']}")
        
        add_info_str = "<br>".join(add_info) if add_info else "-"
        
        md += f"| {col} | {stats['dtype']} | {stats['sample']} | {basic_stats} | {add_info_str} |\n"
    
    return md

def _format_natural_language(profile: Dict[str, Any]) -> str:
    """Format profile as natural language description"""
    nl = f"This dataset contains {len(profile)} columns:\n\n"
    
    for col, stats in profile.items():
        nl += f"• **{col}**:\n"
        nl += f"  - **Type**: {stats['dtype']}\n"
        nl += f"  - **Sample value**: {stats['sample']}\n"
        nl += f"  - **Total entries**: {stats['total_count']} with {stats['null_count']} nulls ({stats['null_percentage']})\n"
        nl += f"  - **Unique values**: {stats['unique_count']}\n"
        
        if 'mean' in stats and stats['mean'] is not None:
            nl += f"  - **Numerical statistics**: mean={stats['mean']}, median={stats['median']}\n"
            nl += f"  - **Range**: {stats['min']} to {stats['max']}\n"
        
        if 'alternative_null_count' in stats:
            nl += f"  - **Alternative null representations**: {stats['alternative_null_count']}\n"
        
        nl += "\n"
    
    return nl

def convert_to_standard_types(obj):
    if isinstance(obj, dict):
        return {k: convert_to_standard_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_standard_types(i) for i in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    else:
        return obj

if __name__ == "__main__":
    # Update the file path as needed
    df = LoadDataset(Path("sheets/credit_card_transactions.csv"))
    
    while True:
        input_method = input('Select output format - md (markdown), nl (natural language), or json (JSON): ').strip().lower()
        if input_method in ['md', 'markdown', 'nl', 'natural language', 'json']:
            break
        else:
            print("Please select a valid option: md, nl, or json.\n")
    
    try:
        if input_method in ['md', 'markdown']:
            profile = GetDatasetProfile(df, output_format='markdown')
        elif input_method in ['nl', 'natural language']:
            profile = GetDatasetProfile(df, output_format='natural_language')
        elif input_method == 'json':
            profile = GetDatasetProfile(df, output_format='json')  # Dictionary
        print(profile)
    except ValueError as ve:
        error_message = {"error": str(ve)}
        print(json.dumps(error_message, indent=4, ensure_ascii=False))
    except Exception as e:
        error_message = {"error": "An unexpected error occurred.", "details": str(e)}
        print(json.dumps(error_message, indent=4, ensure_ascii=False))