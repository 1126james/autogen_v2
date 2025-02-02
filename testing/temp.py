import asyncio
from pathlib import Path
from typing import Dict, Any, Tuple

# Autogen-0.4
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Local
from utils import LoadDataset, GetDatasetProfile

# LLMs
reasoning_model = "qwen2.5:32b-instruct-q8_0"
coding_model = "qwen2.5-coder:32b-instruct-q8_0"

# Common config
llm_base_url = "http://34.204.63.234:11434/v1"
api_key = "none"
capabilities =  {
        "vision": False,
        "function_calling": False,
        "json_output": False
    }


# Reasoning Model Configuration
instruct_client_config = OpenAIChatCompletionClient(
    model=reasoning_model,
    base_url=llm_base_url,
    api_key=api_key,
    model_capabilities=capabilities
)

# Coding Model Configuration
code_client_config = OpenAIChatCompletionClient(
    model=coding_model,
    base_url=llm_base_url,
    api_key=api_key,
    model_capabilities=capabilities
)

async def create_cleaning_reasoning_agent():
    cleaning_reasoning_agent = AssistantAgent(
        name="cleaning_reasoning_agent",
        model_client=instruct_client_config,
        system_message="""<Data Cleaning Planner>

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
""" # This would somehow be overwritten by the initial task prompt on the first iteration of RobinRoundGroupChat
        )
    return cleaning_reasoning_agent

async def create_cleaning_checker():
    cleaning_checker = AssistantAgent(
        name="cleaning_checker",
        model_client=instruct_client_config,
        system_message="""<Validation Assistant>

<purpose>
    Automatically validate the output from the Data Cleaning Reasoning Agent to ensure compliance with the predefined format and guidelines.
</purpose>

<instructions>
    1. Receive the generated data cleaning recommendations.
    2. For each issue entry, perform the following checks:
       a. **Structure and Fields:**
          - Confirm that each entry includes:
            - **Column Name**
            - **Issue Type**
            - **Recommended Action**
            - **Brief Reason**
            - **Dependencies/Constraints** (if applicable)
       b. **Recommended Action:**
          - Ensure that only one **Recommended Action** is provided per issue.
          - Verify that the action is a clear, definitive directive without multiple options or conditional phrases.
          - Check that the action references specific Python functions or methods (e.g., `pandas.to_datetime()`, `pandas.drop()`).
       c. **Terminology Consistency:**
          - Confirm that the field names match exactly with the required output format (e.g., "Brief Reason" instead of "Rationale").
       d. **Avoidance of Ambiguity:**
          - Detect and flag any conditional phrases such as "if possible," "based on business logic," or offering multiple solutions.
       e. **Dependencies/Constraints:**
          - If provided, ensure that dependencies or constraints are relevant and clearly articulated.
       f. **Duplication:**
          - Identify and flag any duplicate entries or redundant issues for the same column.
    3. Compile a validation report detailing:
       - **Pass/Fail Status** for each issue entry.
       - **Specific Errors or Warnings** identified during validation.
       - **Suggestions for Correction** where applicable.
    4. Output the validation report in a clear, structured format (e.g., JSON, Markdown).
</instructions>

<output_format>
    The validation report should include:
    - **Overall Status:** Pass or Fail
    - **Detailed Findings:** For each issue entry, provide:
        - **Column Name**
        - **Issue Type**
        - **Status:** Pass or Fail
        - **Errors/Warnings:** Description of any issues found
        - **Suggestions:** Recommendations for correcting the identified issues
</output_format>

<validation_rules>
    1. **Mandatory Fields Presence:**
       - Each issue must contain all required fields as specified in the output format.
    2. **Single Recommended Action:**
       - Only one **Recommended Action** should be present per issue.
    3. **No Conditional Phrases:**
       - The **Recommended Action** must not contain phrases like "if possible," "based on business logic," etc.
    4. **Specific Python Functions/Methods:**
       - The **Recommended Action** should reference exact Python functions or methods compatible with standard libraries (e.g., Pandas, NumPy, Scikit-learn).
    5. **Terminology Consistency:**
       - Use "Brief Reason" and other field names exactly as specified.
    6. **Avoidance of Multiple Options:**
       - Recommendations should not offer multiple solutions or alternatives.
    7. **Dependency/Constraint Relevance:**
       - Dependencies or constraints should be directly related to the recommended action.
    8. **No Duplications:**
       - Prevent multiple entries for the same issue under a single column unless they represent distinct, non-overlapping issues.
</validation_rules>

<strict_compliance>
    Ensure strict adherence to all validation rules. Any deviation should be flagged with clear, actionable feedback to facilitate corrections.
</strict_compliance>
""" # This is good
        )
    return cleaning_checker

async def run_cleaning_pipeline(data_dict: Dict[str, Any], filepath: Path):
    try:
        cleaning_team = await asyncio.gather(
            create_cleaning_reasoning_agent(),
            create_cleaning_checker()
            )
        
        # Setup termination conditions
        text_term = TextMentionTermination("TERMINATE")
        round_term = MaxMessageTermination(5)
        termination = text_term | round_term

        # Setup team chat
        cleaning_team_chat = RoundRobinGroupChat(
            cleaning_team,
            termination_condition=termination,
        )
        
        # Define cleaning task
        # filepath is relative path to a dataset
        # data_dict is a dictionary containing the dataset metadata in markdown format
        # when LLM/AI Agent first receives the task, it will overwrite the first agent's system_prompt with the below task
        cleaning_task = f"""
<dataset_location>
    {str(filepath)}
</dataset_location>

<data_dictionary>
    {data_dict}
</data_dictionary>
"""

        await Console(cleaning_team_chat.run_stream(task=cleaning_task))
        
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    filepath = Path("sheets\credit_card_transactions.csv")
    df = LoadDataset(filepath)
    initial_profile = GetDatasetProfile(df, output_format="markdown")
    asyncio.run(run_cleaning_pipeline(initial_profile, filepath))