
from . import _fix_file_name
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from prompts import data_dict_generator_prompt

async def initialize_individual_chat(filename: str, metadata, data_dict_generator_client):
    
    file_name_fixed = await _fix_file_name(filename)
    
    # Initialize agents dynamically
    file_handler = AssistantAgent(
        name=f"File_handler_{file_name_fixed}",
        description=f"A file handling agent specific for the file {filename}.",
        model_client=data_dict_generator_client,
        system_message=data_dict_generator_prompt(filename),
    )
    
    response = await file_handler.on_messages(
        [TextMessage(content=f"You are a file handling agent for the file {filename}. The file metadata is as follow: {str(metadata)}.", source="user")], cancellation_token=None,
    )
    return response