import sys

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import asyncio

import gptc

print("create:", end=" ", flush=True)
for response in gptc.ChatCompletion.create(
    model=gptc.models.default,
    # provider=gptc.Provider.Bing,
    messages=[{"role": "user", "content": "write a poem about a tree"}],
    stream=True,
):
    print(response, end="", flush=True)
print()


async def run_async():
    response = await gptc.ChatCompletion.create_async(
        model=gptc.models.default,
        # provider=gptc.Provider.Bing,
        messages=[{"role": "user", "content": "hello!"}],
    )
    print("create_async:", response)


asyncio.run(run_async())
