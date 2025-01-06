import venv
from pathlib import Path
import asyncio
from autogen_core import CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

async def example():
    work_dir = Path("coding")
    work_dir.mkdir(exist_ok=True)
    venv_dir = work_dir / ".venv"
    venv_builder = venv.EnvBuilder(with_pip=True)
    venv_builder.create(venv_dir)
    venv_context = venv_builder.ensure_directories(venv_dir)
    local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir, virtual_env_context=venv_context)
    result = await local_executor.execute_code_blocks(
        code_blocks=[
            CodeBlock(language="shell", code="pip install matplotlib"),
        ],
        cancellation_token=CancellationToken(),)
    print(result)

asyncio.run(example())