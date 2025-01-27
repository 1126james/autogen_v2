import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Union, List, Optional
from tqdm import tqdm
import json
import asyncio

class UnsupportedFileTypeError(Exception):
    """Custom exception for unsupported file types"""
    pass

async def _LoadDataset(file_path: Union[str, Path], read_header_only: bool = False) -> pd.DataFrame:
    """
    Load various tabular data formats into a pandas DataFrame.
    
    Args:
        file_path (str or Path): Path to the dataset file.
        read_header_only (bool): If True, only reads the header row (default: False)
    
    Returns:
        pd.DataFrame: Loaded DataFrame.
        
    Raises:
        UnsupportedFileTypeError: If the file format is unsupported.
        ValueError: If there are issues reading the file.
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    
    try:
        if ext == '.csv':
            if read_header_only:
                return pd.read_csv(file_path, nrows=0)
            return pd.read_csv(file_path)
            
        elif ext in ['.xlsx', '.xls']:
            if read_header_only:
                return pd.read_excel(file_path, nrows=0)
            return pd.read_excel(file_path)
            
        elif ext == '.parquet':
            if read_header_only:
                return pd.read_parquet(file_path, columns=None)
            return pd.read_parquet(file_path)
            
        elif ext == '.json':
            if read_header_only:
                return pd.read_json(file_path, nrows=0)
            return pd.read_json(file_path)
            
        else:
            raise UnsupportedFileTypeError(
                f"Extension '{ext}' is not yet supported. "
                "Supported formats: .csv, .xlsx, .xls, .parquet, .json"
            )
            
    except UnsupportedFileTypeError:
        raise
    except Exception as e:
        raise ValueError(f"Error reading {file_path.name}: {str(e)}") from e

async def get_columns_sample(folder_path: str, file_name: str) -> Dict[str, List[Optional[str]]]:
    """
    Asynchronously get columns and sample values from a specified file.
    Returns a dictionary with column names as keys and lists of sample values as values.
    
    Args:
        folder_path (str): Path to the folder containing the dataset.
        file_name (str): Name of the file to analyze.
        
    Returns:
        Dict[str, List[Optional[str]]]: A dictionary in the format {
            "column1": ["sample1", "sample2", "sample3"],
            "column2": ["sample1", "sample2", "sample3"],
            ...
        }
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        UnsupportedFileTypeError: If the file extension is not supported.
    """
    
    async def _read_file_columns(file_path: Path) -> Dict[str, List[Optional[str]]]:
        """Helper function to read columns and sample values from a single file."""
        try:
            # First read with header only to check if file is valid
            await _LoadDataset(file_path, read_header_only=True)
            
            # Then read actual data for samples
            df = await _LoadDataset(file_path, read_header_only=False)
            
            # Create dictionary with column names and sample values
            columns_dict: Dict[str, List[Optional[str]]] = {}
            for column in df.columns:
                # Get first 3 non-null values if possible
                samples = (
                    df[column]
                    .dropna()
                    .head(3)
                    .map(lambda x: str(x))  # Convert all values to strings
                    .tolist()
                )
                
                # Pad with None if less than 3 samples
                while len(samples) < 3:
                    samples.append(None)
                    
                columns_dict[column] = samples
                
            return columns_dict
                
        except UnsupportedFileTypeError as e:
            print(f"Error with {file_path.name}: {str(e)}")
            raise
        except ValueError as e:
            print(f"Error reading {file_path.name}: {str(e)}")
            return {}
        except Exception as e:
            print(f"Unexpected error with {file_path.name}: {str(e)}")
            return {}
    
    # Construct full file path and check if file exists
    file_path = Path(folder_path) / file_name
    if not file_path.is_file():
        raise FileNotFoundError(f"File '{file_name}' not found in '{folder_path}'")
    
    # Check if file type is supported
    supported_extensions = {'.csv', '.xlsx', '.xls', '.parquet', '.json'}
    if file_path.suffix.lower() not in supported_extensions:
        raise UnsupportedFileTypeError(
            f"Extension '{file_path.suffix}' is not yet supported. "
            "Supported formats: .csv, .xlsx, .xls, .parquet, .json"
        )
    
    # Create and execute task for the file
    task = asyncio.create_task(_read_file_columns(file_path))
    columns_dict = await task
    
    return columns_dict

async def get_dataset_profile(root, file_name: str, output_format: str = 'json') -> Union[str, Dict[str, Any]]:
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
    
    df = await(_LoadDataset(file_path=root+file_name))
    profile = {}
    
    for col in tqdm(df.columns,
                desc=f"Processing {len(df.columns)} columns ({file_name})",
                bar_format="{desc:<70} {bar:30}|{n_fmt:>4}/{total_fmt:<4}",
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
        return await _format_markdown(profile)
    elif output_format == 'natural_language':
        return await _format_natural_language(profile)
    elif output_format == 'json':
        return profile  # Returning the dictionary directly
    else:
        raise ValueError("Unsupported output format. Choose from 'markdown', 'natural_language', or 'json'.")

async def _format_markdown(profile: Dict[str, Any]) -> str:
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

async def _format_natural_language(profile: Dict[str, Any]) -> str:
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

async def convert_to_standard_types(obj):
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
    filepath = Path("sheets/mysql/products.csv")
    
    while True:
        input_method = input('Select output format - md (markdown), nl (natural language), or json (JSON): ').strip().lower()
        if input_method in ['md', 'markdown', 'nl', 'natural language', 'json']:
            break
        else:
            print("Please select a valid option: md, nl, or json.\n")
    
    try:
        if input_method in ['md', 'markdown']:
            profile = asyncio.run(get_dataset_profile(filepath, output_format='markdown'))
        elif input_method in ['nl', 'natural language']:
            profile = asyncio.run(get_dataset_profile(filepath, output_format='natural_language'))
        elif input_method == 'json':
            profile = asyncio.run(get_dataset_profile(filepath, output_format='json'))  # Dictionary
        print(profile)
    except ValueError as ve:
        error_message = {"error": str(ve)}
        print(json.dumps(error_message, indent=4, ensure_ascii=False))
    except Exception as e:
        error_message = {"error": "An unexpected error occurred.", "details": str(e)}
        print(json.dumps(error_message, indent=4, ensure_ascii=False))