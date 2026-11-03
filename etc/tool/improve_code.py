import re
import sys

from os import path
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import gptc


def read_code(text):
    if match := re.search(r"```(python|py|)\n(?P<code>[\S\s]+?)\n```", text):
        return match.group("code")


path = input("Path: ")

with open(path, "r") as file:
    code = file.read()

prompt = f"""
Improve the code in this file:
```py
{code}
```
Don't remove anything.
Add typehints if possible.
Don't add any typehints to kwargs.
Don't remove license comments.
"""

print("Create code...")
response = []
for chunk in gptc.ChatCompletion.create(
    model=gptc.models.default,
    messages=[{"role": "user", "content": prompt}],
    timeout=300,
    stream=True,
):
    response.append(chunk)
    print(chunk, end="", flush=True)
print()
response = "".join(response)

if code := read_code(response):
    with open(path, "w") as file:
        file.write(code)
