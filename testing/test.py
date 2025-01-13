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
from autogen_core.model_context import BufferedChatCompletionContext

# Local
from prompts import cleaning_reasoning_prompt, cleaning_checking_prompt
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

async def create_cleaning_agents(filepath: Path) -> Tuple[AssistantAgent, AssistantAgent]:
    
    # tqdm progress bar
    with tqdm(total=3,
             desc="Creating cleaning reasoning team agents",
             bar_format='{desc:>30}{postfix: <1} {bar}|{n_fmt:>4}/{total_fmt:<4}',
             colour='green') as pbar:
        
        ### 1.1 Cleaning reasoning agent - 1
        async def create_cleaning_reasoning_1():
            Data_Cleaning_Planner = AssistantAgent(
                name="Data_Cleaning_Planner",
                model_client=instruct_client_config,
                system_message=cleaning_reasoning_prompt(filepath, format='markdown'),
            )
            pbar.update(1)
            return Data_Cleaning_Planner
        
        async def create_cleaning_reasoning_2():
            Validation_Assistant = AssistantAgent(
                name="Validation_Assistant",
                model_client=instruct_client_config,
                system_message=cleaning_checking_prompt(filepath),
            )
            pbar.update(1)
            return Validation_Assistant
        
        list_of_cleaning_reasoning_agents = await asyncio.gather(
            create_cleaning_reasoning_1(),
            create_cleaning_reasoning_2(),
        )
        pbar.update(1)
        return list_of_cleaning_reasoning_agents
    

async def cleaning_reasoning_pipeline(data_dict: Dict[str, Any], filepath: Path):
    """
    Run the complete data cleaning and transformation pipeline
    """
    try:
        # cleaning_reasoning_agent, 
        cleaning_reasoning_team: Tuple[AssistantAgent] = await create_cleaning_agents(filepath, data_dict)
        # cleaning_team = [cleaning_team[0], cleaning_team[1]]
        
        # Setup termination conditions
        statusu_pass = TextMentionTermination("Overall Status: Pass")
        max_round = MaxMessageTermination(5)
        termination = statusu_pass | max_round

        # First phase: Data Cleaning (Reasoning)
        cleaning_team_chat = RoundRobinGroupChat(
            cleaning_reasoning_team,
            termination_condition=termination,
        )
        
        # Save last n messages
        context = BufferedChatCompletionContext(buffer_size=1)
        
        # A loading spinner to know if the code is frozen or not
        run_task = Spinner.async_with_spinner(
            message="Loading: ",
            style="braille",
            console_class=Console,
            # cleaning_reasoning_prompt(filepath, data_dict, format='initiate')
            coroutine=cleaning_team_chat.run_stream(task=cleaning_reasoning_prompt(filepath, data_dict), cancellation_token=None)
        )

        await run_task
        # Uncomment below to run the code without spinner
        # from autogen_agentchat.ui import Console
        # await cleaning_team_chat.run_stream(task=cleaning_reasoning_prompt(filepath, data_dict), cancellation_token=None)
        
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    with tqdm(total=3,
              desc="Preparing dataset",
              bar_format='{desc:>30}{postfix: <1} {bar}|{n_fmt:>4}/{total_fmt:<4}',
              colour='green') as pbar:
        # Edit file path
        test_file = Path("sheets/credit_card_transactions.csv")
        pbar.update(1)
        df = LoadDataset(test_file)
        pbar.update(1)
        # Custom function in utils/ to get data dict in markdown/natural language/json format
        initial_profile = GetDatasetProfile(df, output_format="json")
        pbar.update(1)

    asyncio.run(cleaning_reasoning_pipeline(initial_profile, test_file))

