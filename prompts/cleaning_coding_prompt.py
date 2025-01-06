from pathlib import Path

def cleaning_coding_prompt(filepath: Path):
  return f"""
<DATA_CLEANING_CODE_GENERATOR>

<purpose>
    Generate data cleaning code based on data dictionary metadata.
</purpose>

<INPUT>
    FILE_PATH: {str(filepath)}
</INPUT>

<instructions>
    - Explicitly output necessary installation commands (sh) and cleaning code (python)
    - No analysis or insights included
    - Instead of using `inplace=True` directly on a chained assignment, assign the result back to the column to avoid potential issues in future versions of pandas.
    - The argument 'infer_datetime_format' is deprecated and is removed. A strict version of it is now the default
    - Code only in two distinct blocks:
    1. sh command for library installation
    2. Python cleaning code
</instructions>

<REQUIREMENTS>
    1. Generate Python code to clean dataset using pandas or other NECESSARY lib
    2. Use EXACT column names and file paths
    3. Handle common data issues:
        - Missing values
        - Incorrect data types
        - Outliers
        - Inconsistent formats
        - Duplicates
</REQUIREMENTS>

<OUTPUT_FORMAT>
```sh
pip install
```
```python
# import necessary lib
import pandas as pd
# MUST IMPORT Path
from pathlib import Path

# Load actual dataset
df = pd.read_csv("{str(filepath)}")

# Cleaning operations here...


# Save cleaned dataset
output_path = Path("outputs/modified_{str(filepath.name)}")
# SAVE ACCORDING TO SPECIFIC FILE TYPE
df.to_csv(output_path, index=False)
print(f"Saved cleaned dataset to {{output_path}}")
```
</OUTPUT_FORMAT>

<STRICT_RULES>
    1. NO explanatory text or comments outside code blocks
    2. NO placeholder code - use actual column names
    3. NO data analysis or visualization code
    4. ONLY two code blocks: pip install and Python code
    5. MUST include final save operations
    6. Save using the CORRESPONDING file type
</STRICT_RULES>
"""