# Python lib
import asyncio
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from typing import Dict, Any, Tuple
import venv

# Autogen-0.4
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.agents._code_executor_agent import CodeExecutorAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Local
from prompts import cleaning_reasoning_prompt, cleaning_coding_prompt, code_checking_prompt
from utils import CopyFile, LoadDataset, GetDatasetProfile, Spinner

# Only edit here AND filepath under if __name__ == "__main__":
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

#######################################################################
#   !!! DONT EDIT BELOW EXCEPT FOR if __name__ == "__main__":   !!!   #
#######################################################################

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

### setup agents - cleaning team (1)
# Progress bar wrapper for create_agents
async def create_cleaning_agents(filepath: Path) -> Tuple[AssistantAgent, AssistantAgent, CodeExecutorAgent, AssistantAgent]:
    
    # tqdm progress bar
    with tqdm(total=4,
             desc="Creating cleaning team agents",
             bar_format='{desc:>30}{postfix: <1} {bar}|{n_fmt:>4}/{total_fmt:<4}',
             colour='green') as pbar:
        
        ### 1.1 Cleaning reasoning agent
        async def create_cleaning_reasoning_agent():
            cleaning_reasoning_agent = AssistantAgent(
                name="cleaning_reasoning_agent",
                model_client=instruct_client_config,
                # Somehow the first prompt would be overwritten by the initial task prompt (under run_cleaning_pipeline())
                # So this prompt has little to no impact
                system_message=cleaning_reasoning_prompt()
            )
            pbar.update(1)
            return cleaning_reasoning_agent

        ### 1.2 Cleaning code generator agent
        async def create_cleaning_coding_agent() -> AssistantAgent:
            cleaning_coding_agent = AssistantAgent(
                name="cleaning_coding_agent",
                model_client=code_client_config,
                # Testing XML format for consistent format.
                # Tested: plain text
                # To-test: md, json
                system_message=cleaning_coding_prompt(filepath))
            pbar.update(1)
            return cleaning_coding_agent

        ### 1.3 Code executor
        async def create_code_executor() -> CodeExecutorAgent:
            # Setup working directory
            work_dir = Path("coding").absolute()
            work_dir.mkdir(exist_ok=True)
            sheets_dir = Path("coding/sheets").absolute()   # Setup venv .sheets/ directory
            sheets_dir.mkdir(parents=True, exist_ok=True)
            outputs_dir = Path("coding/outputs").absolute() # Setup venv .output/ directory
            outputs_dir.mkdir(parents=True, exist_ok=True)

            # Copy uploaded file to venv
            source_file = filepath.absolute()               # Define source and destination
            destination = sheets_dir / source_file.name     # Use the filename for destination
            CopyFile(source_file, destination)
            tqdm.write(f"File successfully copied to {destination}")

            # Setup venv for code executor
            venv_dir = work_dir / ".venv"
            venv_builder = venv.EnvBuilder(with_pip=True)
            if not venv_dir.exists():
                venv_builder.create(venv_dir)
            venv_context = venv_builder.ensure_directories(venv_dir)

            # Final config on code executor class
            executor = LocalCommandLineCodeExecutor(
                work_dir=str(work_dir),
                virtual_env_context=venv_context
            )
            pbar.update(1)
            return CodeExecutorAgent("code_executor", code_executor=executor)

        ### 1.4 code checker agent
        async def create_code_checker() -> AssistantAgent:
            code_checker = AssistantAgent(
                name="code_checker",
                model_client=instruct_client_config,
                system_message=code_checking_prompt(filepath) # To-do
            )
            pbar.update(1)
            return code_checker

        list_of_cleaning_agents = await asyncio.gather(
            create_cleaning_reasoning_agent(),
            create_cleaning_coding_agent(),
            create_code_executor(),
            create_code_checker()
        )
        return list_of_cleaning_agents


# transformation_assistant = AssistantAgent(
#     name="transformation_assistant",
#     model_client=instruct_client_config,
#     system_message=transformation_prompt # To-do
# )

async def run_cleaning_pipeline(df: pd.DataFrame, data_dict: Dict[str, Any], filepath: Path) -> pd.DataFrame:
    """
    Run the complete data cleaning and transformation pipeline
    """
    try:
        # cleaning_reasoning, cleaning_coding, code_executor, code_checker
        cleaning_team = await create_cleaning_agents(filepath=filepath)

        # Setup termination conditions
        text_term = TextMentionTermination("TERMINATE") # If the text "TERMINATE" is mentioned - text
        round_term = MaxMessageTermination(12) #n          # If max message reaches n round - round
        termination = text_term | round_term            # text OR n round is met

        # First phase: Data Cleaning
        cleaning_team_chat = RoundRobinGroupChat(
            cleaning_team,
            termination_condition=termination,
        )

        # Setup initial prompt
        cleaning_task = f"""<Data Cleaning Planner>

<purpose>
    Provide detailed and actionable data cleaning recommendations with domain-aware considerations for each column.
</purpose>

<dataset_location>
    {str(filepath)}
</dataset_location>

<data_dictionary>
    {data_dict}
</data_dictionary>

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
        
        # A loading spinner to know if the code is frozen or not
        # equal to await Console(cleaning_team_chat.run_stream(task=cleaning_task))
        await Spinner.async_with_spinner(
            message="Loading: ",
            style="braille",
            console_class=Console,
            coroutine=cleaning_team_chat.run_stream(task=cleaning_task)
        )
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")
        # Get cleaned dataframe and updated profile
        # cleaned_df = df  # This should be updated based on code_executor's output
        # cleaned_profile = GetDatasetProfile(cleaned_df)

        # # Second phase: Data Transformation
        # transformation_team = RoundRobinGroupChat(
        #     [transformation_assistant, code_executor, code_checker],
        #     termination_condition=termination
        # )

        # transform_task = f"Suggest and apply transformations based on this profile:\n{cleaned_profile}"
        # await Console(transformation_team.run_stream(task=transform_task))

        # # Return the final processed dataframe
        # return cleaned_df  # This should be the transformed version from code_executor

if __name__ == "__main__":

    # tqdm progress bar
    with tqdm(total=3,
              desc="Preparing dataset",
              bar_format='{desc:>30}{postfix: <1} {bar}|{n_fmt:>4}/{total_fmt:<4}',
              colour='green') as pbar:

        # Edit file path
        test_file = Path("sheets/credit_card_transactions.csv")
        pbar.update(1)

        df = LoadDataset(test_file)
        pbar.update(1)

        # Custom function in utils/ to get data dict in md format
        initial_profile = GetDatasetProfile(df, output_format="markdown")
        pbar.update(1)

    asyncio.run(run_cleaning_pipeline(df, initial_profile, test_file))
