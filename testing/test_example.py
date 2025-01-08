from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio
import logging
from autogen_core.logging import LLMCallEvent
from utils import Spinner
import os

task = """
<dataset_location>
    sheets\credit_card_transactions.csv
</dataset_location>

<data_dictionary>
    
# Dataset Profile
Total columns: 24

## Column Details
| Column Name | Data Type | Sample Value | Stats | Additional Info |
|------------|-----------|--------------|-------|------------------|
| Unnamed: 0 | int64 | 0 | Total: 1296675, Nulls: 0 (0.0%), Unique: 1296675 | Mean: 648337.00<br>Median: 648337.00<br>Range: [0.00, 1296674.00] |
| trans_date_trans_time | object | 2019-01-01 00:00:18 | Total: 1296675, Nulls: 0 (0.0%), Unique: 1274791 | - |
| cc_num | int64 | 2703186189652095 | Total: 1296675, Nulls: 0 (0.0%), Unique: 983 | Mean: 417192042079726656.00<br>Median: 3521417320836166.00<br>Range: [60416207185.00, 4992346398065154048.00] |
| merchant | object | fraud_Rippin, Kub and Mann | Total: 1296675, Nulls: 0 (0.0%), Unique: 693 | - |
| category | object | misc_net | Total: 1296675, Nulls: 0 (0.0%), Unique: 14 | - |
| amt | float64 | 4.97 | Total: 1296675, Nulls: 0 (0.0%), Unique: 52928 | Mean: 70.35<br>Median: 47.52<br>Range: [1.00, 28948.90] |
| first | object | Jennifer | Total: 1296675, Nulls: 0 (0.0%), Unique: 352 | - |
| last | object | Banks | Total: 1296675, Nulls: 0 (0.0%), Unique: 481 | - |
| gender | object | F | Total: 1296675, Nulls: 0 (0.0%), Unique: 2 | - |
| street | object | 561 Perry Cove | Total: 1296675, Nulls: 0 (0.0%), Unique: 983 | - |
| city | object | Moravian Falls | Total: 1296675, Nulls: 0 (0.0%), Unique: 894 | - |
| state | object | NC | Total: 1296675, Nulls: 0 (0.0%), Unique: 51 | - |
| zip | int64 | 28654 | Total: 1296675, Nulls: 0 (0.0%), Unique: 970 | Mean: 48800.67<br>Median: 48174.00<br>Range: [1257.00, 99783.00] |
| lat | float64 | 36.08 | Total: 1296675, Nulls: 0 (0.0%), Unique: 968 | Mean: 38.54<br>Median: 39.35<br>Range: [20.03, 66.69] |
| long | float64 | -81.18 | Total: 1296675, Nulls: 0 (0.0%), Unique: 969 | Mean: -90.23<br>Median: -87.48<br>Range: [-165.67, -67.95] |
| city_pop | int64 | 3495 | Total: 1296675, Nulls: 0 (0.0%), Unique: 879 | Mean: 88824.44<br>Median: 2456.00<br>Range: [23.00, 2906700.00] |
| job | object | Psychologist, counselling | Total: 1296675, Nulls: 0 (0.0%), Unique: 494 | - |
| dob | object | 1988-03-09 | Total: 1296675, Nulls: 0 (0.0%), Unique: 968 | - |
| trans_num | object | 0b242abb623afc578575680df30655b9 | Total: 1296675, Nulls: 0 (0.0%), Unique: 1296675 | - |
| unix_time | int64 | 1325376018 | Total: 1296675, Nulls: 0 (0.0%), Unique: 1274823 | Mean: 1349243636.73<br>Median: 1349249747.00<br>Range: [1325376018.00, 1371816817.00] |
| merch_lat | float64 | 36.01 | Total: 1296675, Nulls: 0 (0.0%), Unique: 1247805 | Mean: 38.54<br>Median: 39.37<br>Range: [19.03, 67.51] |
| merch_long | float64 | -82.05 | Total: 1296675, Nulls: 0 (0.0%), Unique: 1275745 | Mean: -90.23<br>Median: -87.44<br>Range: [-166.67, -66.95] |
| is_fraud | int64 | 0 | Total: 1296675, Nulls: 0 (0.0%), Unique: 2 | Mean: 0.01<br>Median: 0.00<br>Range: [0.00, 1.00] |
| merch_zipcode | float64 | 28705.00 | Total: 1296675, Nulls: 195973 (15.1%), Unique: 28336 | Mean: 46825.75<br>Median: 45860.00<br>Range: [1001.00, 99403.00] |

</data_dictionary>"""

reasoning_prompt = """<Data Cleaning Planner>

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
</strict_rules>"""

checking_prompt = """<Validation Assistant>

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
"""

# OpenAI model client configuration
reasoning_model = "qwen2.5:32b-instruct-q8_0"
llm_base_url = os.getenv("AWS_API")
api_key = "none"
capabilities =  {
        "vision": False,
        "function_calling": False,
        "json_output": False
    }

# Initialize OpenAI model client
openai_model_client = OpenAIChatCompletionClient(
    model=reasoning_model,
    base_url=llm_base_url,
    api_key=api_key,
    model_capabilities=capabilities,
)

# Initialize agents
from autogen_agentchat.agents import AssistantAgent

# Replace system_message with pre-defined prompts or exmaples
# Prompt use: reasoning_prompt, checking_prompt
# Interviewee Example: You must answer in json format, and must answer with wrong answer only. If the interviewer asks you to review your answer, correct your answer.
# Interviewer Example: You must review the answer by the interviewee. If the answer is correct, you must say 'Correct'. If the answer is incorrect, ask the interviewee to review the answer.
Interviewee = AssistantAgent(name='Interviewee',
                             model_client=openai_model_client,
                             system_message="You must answer in json format, and must answer with wrong answer only. If the interviewer asks you to review your answer, correct your answer.")
Interviewer = AssistantAgent(name='Interviewer',
                             model_client=openai_model_client,
                             system_message="You must review the answer by the interviewee. If the answer is correct, you must say 'Correct'. If the answer is incorrect, you must say 'Incorrect' and ask the interviewee to review the answer.")

# Groupchat Termination conditions
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
text_term = TextMentionTermination("Correct")
round_term = MaxMessageTermination(5) #n
termination = text_term | round_term

# Initialize groupchat
from autogen_agentchat.teams import RoundRobinGroupChat
team_chat = RoundRobinGroupChat(
    [Interviewee, Interviewer],
    termination_condition=termination,
)

# Run groupchat in console UI
from autogen_agentchat.ui import Console
async def qa():
    # Promp use: task
    # Example: Whats the capital of France?
    await Console(team_chat.run_stream(task="Whats the capital of France?", cancellation_token=None))

if __name__ == "__main__":
    asyncio.run(qa())