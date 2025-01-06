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


# ONLY EDIT HERE
reasoning_model = "qwen2.5:32b-instruct-q8_0"
coding_model = "qwen2.5-coder:32b-instruct-q8_0"
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
### setup agents - cleaning team (1)
# Progress bar wrapper for create_agents
async def create_cleaning_agents(filepath: Path) -> Tuple[AssistantAgent, AssistantAgent, CodeExecutorAgent, AssistantAgent]:
    with tqdm(total=4,
             desc="Creating cleaning team agents",
             bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}',
             colour='green') as pbar:
        
        ### 1.1 Cleaning reasoning agent
        async def create_cleaning_reasoning_agent():
            cleaning_reasoning_agent = AssistantAgent(
                name="cleaning_reasoning_agent",
                model_client=instruct_client_config,
                # Somehow the first prompt would be overwritten by the initial task prompt (under run_cleaning_pipeline())
                # So this prompt has little to no impact
                system_message=f"""You are the first agent in the data cleaning pipeline."""
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

        ### 2. Code executor
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

        ### 3. code checker agent
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
        round_term = MaxMessageTermination(12)          # If max message reaches 12 round - round
        termination = text_term | round_term            # text OR 12 round is met

        # First phase: Data Cleaning
        cleaning_team_chat = RoundRobinGroupChat(
            cleaning_team,
            termination_condition=termination,
        )

        # prompt imported from .prompts/
        cleaning_task = cleaning_reasoning_prompt(data_dict, filepath)
        
        # await Console(cleaning_team_chat.run_stream(task=cleaning_task))
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
    # First progress bar for data loading and profiling
    with tqdm(total=3,
              desc="Preparing dataset",
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}',
              colour='green') as pbar:

        test_file = Path("../sheets/sample2.csv")
        pbar.update(1)

        df = LoadDataset(test_file)
        pbar.update(1)

        initial_profile = GetDatasetProfile(df)
        pbar.update(1)

    # Run the async operation (create_agents has its own progress bar)
    asyncio.run(run_cleaning_pipeline(df, initial_profile, test_file))
