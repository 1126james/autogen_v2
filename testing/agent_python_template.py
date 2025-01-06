import venv
from pathlib import Path
from copy_file import copy_file
import asyncio
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_agentchat.agents._code_executor_agent import CodeExecutorAgent

task = TextMessage(content="\n```sh\npip install pandas numpy datetime\n```\n```python\nimport pandas as pd\nimport numpy as np\nfrom datetime import datetime\n\n# Load the dataset\nfile_path = 'sheets/sample.csv'\ndf = pd.read_csv(file_path)\n\n# 1. Handle null values in merch_zipcode by imputing with 'Unknown'\ndf['merch_zipcode'].fillna('Unknown', inplace=True)\n\n# 2. Ensure is_fraud column has expected labels; check unique values\nunique_fraud_values = df['is_fraud'].unique()\n\n# 3. Convert dob to datetime format if not already done and ensure consistent date formats\nif pd.api.types.is_string_dtype(df['dob']):\n    df['dob'] = pd.to_datetime(df['dob'], errors='coerce')\n\n# 4. Check and remove duplicates based on transaction number (trans_num)\ndf.drop_duplicates(subset='trans_num', inplace=True)\n\n# 5. Verify if zip codes outside the usual range are valid\nvalid_zip_range = (df['merch_zipcode'].astype(str).str.match(r'^\d{5}(-\d{4})?$') | (df['merch_zipcode'] == 'Unknown'))\ninvalid_zips = df[~valid_zip_range]\n# Optionally, handle invalid zip codes if needed\ndf = df[valid_zip_range]\n\n# Display the first 5 rows of the cleaned data\nprint(df.head())\n```",source="agent")

async def create_code_executor() -> CodeExecutorAgent:
        work_dir = Path("coding").absolute()
        work_dir.mkdir(exist_ok=True)

        # Setup venv sheets directory
        sheets_dir = Path("coding/sheets").absolute()
        sheets_dir.mkdir(parents=True, exist_ok=True)

        # Define source and destination
        source_file = Path("sheets/sample.csv").absolute()
        destination = sheets_dir / source_file.name  # Use the filename for destination

        # Copy the file from root to venv
        copy_file(source_file, destination)

        # Setup venv for code executor
        venv_dir = work_dir / ".venv"
        venv_builder = venv.EnvBuilder(with_pip=True)
        if not venv_dir.exists():
            venv_builder.create(venv_dir)
        venv_context = venv_builder.ensure_directories(venv_dir)

        executor = LocalCommandLineCodeExecutor(
            work_dir=str(work_dir),
            virtual_env_context=venv_context
        )
        return CodeExecutorAgent("code_executor", code_executor=executor)

async def run_code_executor_agent() -> None:
    # Create a code executor agent that uses a venv container to execute code.
    code_executor_agent = await create_code_executor()
    # Run the agent with a given code snippet.
    response = await code_executor_agent.on_messages([task], CancellationToken())
    print(response.chat_message.content)


asyncio.run(run_code_executor_agent())