import asyncio
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from testing._providers import get_providers
from testing.log_time import log_time_async

import gptc


async def create_async(provider):
    try:
        response = await log_time_async(
            provider.create_async,
            model=gptc.models.default.name,
            messages=[{"role": "user", "content": "Hello, are you GPT 3.5?"}],
        )
        print(f"{provider.__name__}:", response)
    except Exception as e:
        print(f"{provider.__name__}: {e.__class__.__name__}: {e}")


async def run_async():
    responses: list = [
        create_async(provider) for provider in get_providers() if provider.working
    ]
    await asyncio.gather(*responses)


print("Total:", asyncio.run(log_time_async(run_async)))
