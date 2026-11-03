import requests

import gptc

from gptc.client import Client

client = Client()

# Processing remote image
remote_image = requests.get(
    "https://raw.githubusercontent.com/gpt-computer/gpt-computer/refs/heads/main/docs/images/cat.jpeg",
    stream=True,
).content
response_remote = client.chat.completions.create(
    model=gptc.models.default_vision,
    messages=[{"role": "user", "content": "What are on this image?"}],
    image=remote_image,
)
print("Response for remote image:")
if (
    not response_remote.choices
    or response_remote.choices[0].message is None
    or response_remote.choices[0].message.content is None
):
    raise ValueError("LLM returned empty or filtered response")
print(response_remote.choices[0].message.content)

print("\n" + "-" * 50 + "\n")  # Separator

# Processing local image
local_image = open("docs/images/cat.jpeg", "rb")
response_local = client.chat.completions.create(
    model=gptc.models.default_vision,
    messages=[{"role": "user", "content": "What are on this image?"}],
    image=local_image,
)
print("Response for local image:")
if (
    not response_local.choices
    or response_local.choices[0].message is None
    or response_local.choices[0].message.content is None
):
    raise ValueError("LLM returned empty or filtered response")
print(response_local.choices[0].message.content)
local_image.close()  # Close file after use
