### BASIC TEMPLATE OF AUTOGEN !!! DO NOT EDIT!!!

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio
import math

# Basic Configurations
model = "qwen2.5:7b-instruct-q4_0"
model_url = "http://127.0.0.1:11434/v1"
api_key = "YOUR_API_KEY"
model_capabilities = {
                "vision": False,
                "function_calling": True,
                "json_output": False
            }

# Define Tools
async def calculator(expression: str) -> str:
    try:
        safe_dict = {
            'abs': abs,
            'round': round,
            'pi': math.pi,
            'e': math.e,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10
        }
        
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        if isinstance(result, (int, float)):
            if result.is_integer():
                return str(int(result))
            return f"{result:.6f}".rstrip('0').rstrip('.')
        
        return str(result)
        
    except Exception as e:
        return f"Error: {str(e)}"

# Create Agents
math_agent = AssistantAgent(
        name="math_agent",
        reflect_on_tool_use= True,
        model_client=OpenAIChatCompletionClient(
            model=model,
            base_url=model_url,
            api_key=api_key,
            model_capabilities=model_capabilities
        ),
        tools=[calculator],
        system_message="Use the appropriate tools to solve tasks. If no appropriate tools are available, use your common sense. When the task has been completed, Reply with TERMINATE."
    )

# Define workflow
async def main() -> None:
    # Define termination condition
    termination_approve = TextMentionTermination("TERMINATE")
    termination_max = MaxMessageTermination(max_messages=10)
    # 1. user message(str)
    # 2. FunctionCall(id, arg, name)
    # 3. FunctionExecutionResult(content, call_id) id==call_id
    # 4. result response
    termination = termination_approve | termination_max

    # Define a team
    agent_team = RoundRobinGroupChat(
        [math_agent], 
        termination_condition=termination
    )

    # Run the team and stream messages to the console
    stream = agent_team.run_stream(
        task="Write a python code to greet a user named James"
    )
    await Console(stream)

if __name__ == "__main__":
    asyncio.run(main())