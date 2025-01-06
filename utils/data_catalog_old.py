import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Union

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

def GetDatasetProfile(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Create a comprehensive profile of the dataset including statistics and metadata.
    """
    profile = {}
    
    for col in df.columns:
        col_stats = {
            'dtype': str(df[col].dtype),
            'total_count': len(df[col]),
            'null_count': df[col].isna().sum(),
            'null_percentage': (df[col].isna().sum() / len(df[col])) * 100,
            'unique_count': df[col].nunique()
        }
        
        # Add numerical statistics if applicable
        if pd.api.types.is_numeric_dtype(df[col]):
            col_stats.update({
                'mean': df[col].mean() if not df[col].empty else None,
                'median': df[col].median() if not df[col].empty else None,
                'std': df[col].std() if not df[col].empty else None,
                'min': df[col].min() if not df[col].empty else None,
                'max': df[col].max() if not df[col].empty else None
            })
        
        # Check for various null representations
        null_variants = ['NA', 'Na', 'na', 'NULL', 'Null', 'null', 'NAN', 'Nan', 'nan']
        if df[col].dtype == 'object':
            null_like_count = df[col].isin(null_variants).sum()
            col_stats['alternative_null_count'] = null_like_count
        
        profile[col] = col_stats
    
    return profile