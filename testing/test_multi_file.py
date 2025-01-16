# Python lib
import asyncio
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from typing import Dict, Any, Tuple, List
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
    model_info=capabilities
)

# Coding Model Configuration
code_client_config = OpenAIChatCompletionClient(
    model=coding_model,
    base_url=llm_base_url,
    api_key=api_key,
    model_info=capabilities
)

async def create_file_handling_agents(number_of_agents: int = None) -> List[AssistantAgent]:
    if number_of_agents is None:
        raise ValueError("Please provide the number of agents to be created")
    
    # Initialize the progress bar with the total number of agents to be created
    with tqdm(total=number_of_agents,
              desc=f"Creating {number_of_agents} agents",
              bar_format='{desc:>30}{postfix: <1} {bar}|{n_fmt:>4}/{total_fmt:<4}',
              colour='green') as pbar:
        
        agents = []

        # Define an asynchronous function to create a single File_handler agent
        async def create_agent(index: int) -> AssistantAgent:
            file_handler = AssistantAgent(
                name=f"File_handler_{index}",
                model_client=instruct_client_config,
            )
            pbar.update(1)
            return file_handler

        # Create a list of tasks for all agents
        tasks = [create_agent(i) for i in range(1, number_of_agents + 1)]
        
        # Execute all agent creation tasks concurrently
        agents = await asyncio.gather(*tasks)
    
    return agents

# Example usage
agents = asyncio.run(create_file_handling_agents(10))
print(agents)
print(len(agents))

# async def cleaning_reasoning_pipeline(data_dict: Dict[str, Any], filepath: Path):
#     """
#     Run the complete data cleaning and transformation pipeline
#     """
#     try:
#         # cleaning_reasoning_agent, 
#         cleaning_reasoning_team = await create_cleaning_agents(filepath)
#         # cleaning_team = [cleaning_team[0], cleaning_team[1]]
        
#         # Setup termination conditions
#         statusu_pass = TextMentionTermination("Overall Status: Pass")
#         max_round = MaxMessageTermination(5)
#         termination = statusu_pass | max_round

#         # First phase: Data Cleaning (Reasoning)
#         cleaning_team_chat = RoundRobinGroupChat(
#             cleaning_reasoning_team,
#             termination_condition=termination,
#         )
        
#         # Save last n messages
#         context = BufferedChatCompletionContext(buffer_size=1)
        
#         # A loading spinner to know if the code is frozen or not
#         run_task = Spinner.async_with_spinner(
#             message="Loading: ",
#             style="braille",
#             console_class=Console,
#             coroutine=cleaning_team_chat.run_stream(task=cleaning_reasoning_prompt(filepath, data_dict), cancellation_token=None)
#         )

#         await run_task
        
#         # Uncomment below to run the code without spinner
#         # from autogen_agentchat.ui import Console
#         # await cleaning_team_chat.run_stream(task=cleaning_reasoning_prompt(filepath, data_dict), cancellation_token=None)
        
#     except Exception as e:
#         raise Exception(f"An error occurred: {str(e)}")

# if __name__ == "__main__":
#     with tqdm(total=3,
#               desc="Preparing dataset",
#               bar_format='{desc:>30}{postfix: <1} {bar}|{n_fmt:>4}/{total_fmt:<4}',
#               colour='green') as pbar:
#         # Edit file path
#         test_file = Path("sheets/sample2.csv")
#         pbar.update(1)
#         df = LoadDataset(test_file)
#         pbar.update(1)
#         # Custom function in utils/ to get data dict in markdown/natural language/json format
#         initial_profile = GetDatasetProfile(df, output_format="json")
#         pbar.update(1)

#     asyncio.run(cleaning_reasoning_pipeline(initial_profile, test_file))

