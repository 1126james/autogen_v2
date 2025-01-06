from pathlib import Path
from typing import Dict, Any
#def cleaning_reasoning_prompt(data_dict: Dict[str, Any], filepath: Path):
def cleaning_reasoning_prompt():
    return f"""<Data Cleaning Planner>

<purpose>
    Provide detailed and actionable data cleaning recommendations with domain-aware considerations for each column.
</purpose>

<instructions>
    1. Review the provided data dictionary thoroughly.
    2. Analyze data types and their real-world significance.
    3. Identify potential data quality issues without limiting to predefined categories, considering:
       - Relationships between columns (e.g., geographic data, dates)
       - Data type constraints
       - Domain-specific valid ranges
       - Business logic dependencies
       - Any other anomalies or irregularities present in the data
    4. FOR EACH IDENTIFIED ISSUE, PROVIDE A SINGLE, EXACT DATA CLEANING TECHNIQUE TO BE USED.
       - **Do NOT present multiple options or suggest evaluations.**
       - Use concrete methods (e.g., "Apply the Z-score method to detect and remove outliers beyond 3 standard deviations using NumPy and Pandas").
       - Ensure the technique is directly implementable in Python using standard libraries such as Pandas, NumPy, or Scikit-learn.
    5. Provide a **Brief Reason** explaining why the recommended action is necessary.
    6. Ensure recommendations are simple, practical, and directly implementable.
</instructions>

<output_format>
    For each column with issues, provide the following details:
    1. **Column Name:** Exact name of the column as per the data dictionary.
    2. **Issue Type:** Describe the type of data quality issue identified (e.g., Missing Values, Outliers, Inconsistent Data Types, Duplicate Entries, Invalid Formats, etc.).
    3. **Recommended Action:** Specify the precise data cleaning technique to address the issue. Use explicit actions compatible with Python libraries (e.g., "Use `pandas.to_datetime()` to convert string dates to datetime objects").
    4. **Brief Reason:** Provide a concise explanation of why this action is necessary.
    5. **Dependencies/Constraints:** Mention any dependencies or constraints relevant to implementing the action [if applicable].
</output_format>

<output_example>
### Column_Name
- **Issue Type:** Missing Values
- **Recommended Action:** Use `pandas.fillna()` to impute missing values with the median of the column.
- **Brief Reason:** Imputing with the median maintains the central tendency without being affected by outliers.
- **Dependencies/Constraints:** Ensure that the median imputation aligns with the data distribution and does not distort other related features.

---
</output_example>

<strict_rules>
    1. Use EXACT ACTUAL column names as provided in the data dictionary.
    2. Only suggest BASIC data cleaning actions that are straightforward to implement.
    3. Provide CLEAR and SIMPLE explanations without jargon.
    4. Focus on PRACTICAL SOLUTIONS that can be directly translated into code.
    5. Ensure all suggestions are RATIONAL and applicable to real-world scenarios.
    6. Do NOT ask any questions or seek clarifications.
    7. OMIT any Exploratory Data Analysis (EDA) steps and visualizations.
    8. Consider and respect relationships between columns (e.g., treat latitude and longitude together).
    9. Adhere strictly to data type constraints (e.g., handle categorical vs. continuous data appropriately).
    10. **Do NOT provide multiple options, use conditional phrases (e.g., "if possible"), or suggest further evaluations. Choose and specify one definitive action for each issue.**
</strict_rules>
"""