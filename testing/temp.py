import asyncio
from pathlib import Path
from typing import Dict, Any, Tuple

# Autogen-0.4
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# LLMs
reasoning_model = "qwen2.5:32b-instruct-q8_0"
coding_model = "qwen2.5-coder:32b-instruct-q8_0"

# Common config
llm_base_url = "http://.../v1"
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
        system_message='some prompt here' # This would somehow be overwritten by the initial task prompt on the first iteration of RobinRoundGroupChat
        )
    return cleaning_reasoning_agent

async def create_cleaning_checker():
    cleaning_checker = AssistantAgent(
        name="cleaning_checker",
        model_client=instruct_client_config,
        system_message='some prompt here' # This is good
        )
    return cleaning_checker

list_of_cleaning_agents = await asyncio.gather(
    create_cleaning_reasoning_agent(),
    create_cleaning_checker()
    )

async def run_cleaning_pipeline(data_dict: Dict[str, Any], filepath: Path):
    try:
        cleaning_team = await create_cleaning_agents()
        
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
    data_dict = 'something in markdown format'
    filepath = Path("sheets\credit_card_transactions.csv")
    asyncio.run(run_cleaning_pipeline(data_dict, filepath))