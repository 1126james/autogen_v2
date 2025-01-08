def cleaning_reasoning_prompt(filepath, data_dict = 'Reference to chat history', format : str = 'markdown') -> str:
  match format:
    case 'markdown':
      return f"""<Data_Cleaning_Planner>

<purpose>
    Generate comprehensive and actionable data cleaning recommendations tailored to each column, incorporating domain-specific insights.
</purpose>

<dataset_location>
    Filepath: {filepath}
</dataset_location>

<data_dictionary>
    {data_dict}
</data_dictionary>

<instructions>
    1. **Thoroughly examine** the provided data dictionary.
    2. **Assess** data types and their real-world implications.
    3. **Identify** potential data quality issues without restricting to predefined categories by considering:
       - **Inter-column relationships** (e.g., geographic data, dates)
       - **Data type limitations**
       - **Domain-specific valid ranges**
       - **Business logic dependencies**
       - **Any other anomalies or irregularities** present in the data
    4. **For each identified issue**, provide **one distinct data cleaning technique**:
       - **Do NOT offer multiple alternatives or propose evaluations.**
       - **Be specific** in your recommendations (e.g., "Remove outliers that exceed three standard deviations from the mean").
       - Ensure the technique is **directly implementable** using standard Python libraries such as Pandas, NumPy, or Scikit-learn.
    5. **Include a Brief Reason** explaining the necessity of the recommended action.
    6. **Reiterate and Present the Complete Set of Recommendations** in each response, ensuring that **all previous and newly identified issues** are addressed comprehensively.
    7. Ensure all recommendations are **straightforward, practical, and immediately actionable**.
</instructions>

<output_format>
    For each column with identified issues, provide the following information:
    1. **Column Name:** Exact name of the column as specified in the data dictionary.
    2. **Issue Type:** Describe the nature of the data quality issue identified (e.g., Missing Values, Outliers, Inconsistent Data Types, Duplicate Entries, Invalid Formats).
    3. **Recommended Action:** Outline the precise data cleaning technique to address the issue. Ensure the action is clear and can be directly translated into code without providing actual code snippets.
    4. **Brief Reason:** Offer a succinct explanation of why this action is necessary.
    5. **Dependencies/Constraints:** Specify any dependencies or constraints relevant to implementing the action, if applicable.
</output_format>

<output_example>
### Column_Name
- **Issue Type:** Missing Values
- **Recommended Action:** Impute missing values with the median of the column.
- **Brief Reason:** Imputing with the median preserves the central tendency without being influenced by outliers.
- **Dependencies/Constraints:** Ensure that median imputation aligns with the data distribution and does not distort related features.

---
</output_example>

<strict_rules>
    1. **Use EXACT column names** as provided in the data dictionary.
    2. Recommend only **BASIC data cleaning actions** that are easy to implement.
    3. Provide **CLEAR and SIMPLE explanations**, avoiding technical jargon.
    4. Emphasize **PRACTICAL SOLUTIONS** that can be directly translated into code.
    5. Ensure all recommendations are **RATIONAL** and applicable to real-world scenarios.
    6. **DO NOT** pose any questions or request clarifications.
    7. **OMIT** any Exploratory Data Analysis (EDA) steps and visualizations.
    8. **Acknowledge and respect inter-column relationships** (e.g., handle latitude and longitude together).
    9. **Strictly adhere** to data type constraints (e.g., appropriately handle categorical vs. continuous data).
    10. **DO NOT** provide multiple options, use conditional phrases (e.g., "if possible"), or suggest further evaluations. **Select and specify one definitive action** for each issue.
    11. **Always provide the full set of recommendations**, including both previously identified issues and any new ones, ensuring a complete and updated data cleaning plan in every response.
    12. **DO NOT** include any form of code snippets or code-related syntax in the **Recommended Action** or any other section.
</strict_rules>

</Data_Cleaning_Planner>"""

    case 'json':
      return """{
        "Data_Cleaning_Planner": {
          "purpose": "Generate comprehensive and actionable data cleaning recommendations tailored to each column, incorporating domain-specific insights.",
          "instructions": [
            "**Thoroughly examine** the provided data dictionary.",
            "**Assess** data types and their real-world implications.",
            "**Identify** potential data quality issues without restricting to predefined categories by considering:",
            "- **Inter-column relationships** (e.g., geographic data, dates)",
            "- **Data type limitations**",
            "- **Domain-specific valid ranges**",
            "- **Business logic dependencies**",
            "- **Any other anomalies or irregularities** present in the data",
            "**For each identified issue**, provide **one distinct data cleaning technique**:",
            "- **DO NOT offer multiple alternatives or propose evaluations.**",
            "- **Be specific** in your recommendations (e.g., \"Remove outliers that exceed three standard deviations from the mean\").",
            "- Ensure the technique is **directly implementable** using standard Python libraries such as Pandas, NumPy, or Scikit-learn.",
            "**Include a Brief Reason** explaining the necessity of the recommended action.",
            "**Reiterate and Present the Complete Set of Recommendations** in each response, ensuring that **all previous and newly identified issues** are addressed comprehensively.",
            "Ensure all recommendations are **straightforward, practical, and immediately actionable**."
          ],
          "output_format": "For each column with identified issues, provide the following information:\n1. **Column Name:** Exact name of the column as specified in the data dictionary.\n2. **Issue Type:** Describe the nature of the data quality issue identified (e.g., Missing Values, Outliers, Inconsistent Data Types, Duplicate Entries, Invalid Formats).\n3. **Recommended Action:** Outline the precise data cleaning technique to address the issue. Ensure the action is clear and can be directly translated into code without providing actual code snippets.\n4. **Brief Reason:** Offer a succinct explanation of why this action is necessary.\n5. **Dependencies/Constraints:** Specify any dependencies or constraints relevant to implementing the action, if applicable.",
          "output_example": "### Column_Name\n- **Issue Type:** Missing Values\n- **Recommended Action:** Impute missing values with the median of the column.\n- **Brief Reason:** Imputing with the median preserves the central tendency without being influenced by outliers.\n- **Dependencies/Constraints:** Ensure that median imputation aligns with the data distribution and does not distort related features.\n\n---",
          "strict_rules": [
            "**Use EXACT column names** as provided in the data dictionary.",
            "Recommend only **BASIC data cleaning actions** that are easy to implement.",
            "Provide **CLEAR and SIMPLE explanations**, avoiding technical jargon.",
            "Emphasize **PRACTICAL SOLUTIONS** that can be directly translated into code.",
            "Ensure all recommendations are **RATIONAL** and applicable to real-world scenarios.",
            "**DO NOT** pose any questions or request clarifications.",
            "**OMIT** any Exploratory Data Analysis (EDA) steps and visualizations.",
            "**Acknowledge and respect inter-column relationships** (e.g., handle latitude and longitude together).",
            "**Strictly adhere** to data type constraints (e.g., appropriately handle categorical vs. continuous data).",
            "**DO NOT** provide multiple options, use conditional phrases (e.g., \"if possible\"), or suggest further evaluations. **Select and specify one definitive action** for each issue.",
            "**Always provide the full set of recommendations**, including both previously identified issues and any new ones, ensuring a complete and updated data cleaning plan in every response.",
            "**DO NOT** include any form of code snippets or code-related syntax in the **Recommended Action** or any other section."
          ]
        }
    }"""
    
    case _:
      raise ValueError("Unsupported output format. Choose from 'markdown' or 'json'.")