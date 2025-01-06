import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Union
from tqdm import tqdm

def LoadDataset(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load various tabular data formats into a pandas DataFrame.
    Supports CSV, Excel, and other common formats.
    """
    file_path = Path(file_path)
    if file_path.suffix.lower() == '.csv':
        return pd.read_csv(file_path)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

def GetDatasetProfile(df: pd.DataFrame, output_format: str = 'markdown') -> str:
    """
    Create a comprehensive profile of the dataset including statistics, metadata, and samples.
    
    Args:
        df: Input DataFrame
        output_format: 'markdown' or 'natural_language'
    
    Returns:
        Formatted string containing dataset profile
    """
    
    profile = {}
    
    for col in tqdm(df.columns,
                    desc=f"Processing {len(df.columns)} columns",
                    bar_format="{desc:>30}{postfix: <1} {bar}|{n_fmt:>4}/{total_fmt:<4}",
                    colour="green"):
        # Get non-null sample value
        sample_value = df[col].dropna().iloc[0] if not df[col].empty else None
        if isinstance(sample_value, (np.floating, float)):
            sample_value = f"{sample_value:.2f}"
        
        col_stats = {
            'dtype': str(df[col].dtype),
            'sample': str(sample_value),
            'total_count': len(df[col]),
            'null_count': df[col].isna().sum(),
            'null_percentage': f"{(df[col].isna().sum() / len(df[col])) * 100:.1f}%",
            'unique_count': df[col].nunique()
        }
        
        # Add numerical statistics if applicable
        if pd.api.types.is_numeric_dtype(df[col]):
            col_stats.update({
                'mean': f"{df[col].mean():.2f}" if not df[col].empty else None,
                'median': f"{df[col].median():.2f}" if not df[col].empty else None,
                'std': f"{df[col].std():.2f}" if not df[col].empty else None,
                'min': f"{df[col].min():.2f}" if not df[col].empty else None,
                'max': f"{df[col].max():.2f}" if not df[col].empty else None
            })
        
        # Check for various null representations
        null_variants = ['NA', 'Na', 'na', 'NULL', 'Null', 'null', 'NAN', 'Nan', 'nan']
        if df[col].dtype == 'object':
            null_like_count = df[col].isin(null_variants).sum()
            if null_like_count > 0:
                col_stats['alternative_null_count'] = null_like_count
        
        profile[col] = col_stats
    
    if output_format == 'markdown':
        return _format_markdown(profile)
    else:
        return _format_natural_language(profile)

def _format_markdown(profile: Dict) -> str:
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
        if 'mean' in stats:
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

def _format_natural_language(profile: Dict) -> str:
    """Format profile as natural language description"""
    nl = f"This dataset contains {len(profile)} columns:\n\n"
    
    for col, stats in profile.items():
        nl += f"• {col}:\n"
        nl += f"  - Type: {stats['dtype']}\n"
        nl += f"  - Sample value: {stats['sample']}\n"
        nl += f"  - Contains {stats['total_count']} entries with {stats['null_count']} nulls ({stats['null_percentage']})\n"
        nl += f"  - Has {stats['unique_count']} unique values\n"
        
        if 'mean' in stats:
            nl += f"  - Numerical stats: mean={stats['mean']}, median={stats['median']}\n"
            nl += f"  - Range: {stats['min']} to {stats['max']}\n"
        
        if 'alternative_null_count' in stats:
            nl += f"  - Found {stats['alternative_null_count']} alternative null representations\n"
        
        nl += "\n"
    
    return nl

if __name__ == "__main__":
    df = LoadDataset(Path("../coding/outputs/modified_credit_card_transactions.csv"))
    
    while True:
        input_method = input('md (markdown) or nl (natural language): ')
        match input_method:
            case 'md':
                # Get markdown format (better for LLM comprehension)
                profile = GetDatasetProfile(df, output_format='markdown')
                break
            case 'nl':
                # Get natural language format (alternative)
                profile = GetDatasetProfile(df, output_format='natural_language')
                break
            case _:
                print("Please only select md or nl\n")
    print(profile)