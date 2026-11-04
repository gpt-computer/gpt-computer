"""
CLI Learning Module

Facilitates the collection and storage of user feedback on generated code outputs.
"""

from __future__ import annotations

import json
import random
import tempfile

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from dataclasses_json import dataclass_json
from termcolor import colored

from gpt_computer.agent.memory.disk import DiskMemory
from gpt_computer.agent.prompt import Prompt


@dataclass_json
@dataclass
class Review:
    ran: Optional[bool]
    perfect: Optional[bool]
    works: Optional[bool]
    comments: str
    raw: str


@dataclass_json
@dataclass
class Learning:
    prompt: str
    model: str
    temperature: float
    config: str
    logs: str
    session: str
    review: Optional[Review]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "0.3"


TERM_CHOICES = (
    colored("y", "green")
    + "/"
    + colored("n", "red")
    + "/"
    + colored("u", "yellow")
    + "(ncertain): "
)


def human_review_input() -> Optional[Review]:
    print()
    from gpt_computer.interfaces.cli.learning import check_collection_consent

    if not check_collection_consent():
        return None
    print()
    print(
        colored("To help gpt-computer learn, please answer 3 questions:", "light_green")
    )
    print()

    ran = input("Did the generated code run at all? " + TERM_CHOICES)
    ran = ask_for_valid_input(ran)

    if ran == "y":
        perfect = input(
            "Did the generated code do everything you wanted? " + TERM_CHOICES
        )
        perfect = ask_for_valid_input(perfect)

        if perfect != "y":
            useful = input("Did the generated code do anything useful? " + TERM_CHOICES)
            useful = ask_for_valid_input(useful)
        else:
            useful = ""
    else:
        perfect = ""
        useful = ""

    if perfect != "y":
        comments = input(
            "If you have time, please explain what was not working "
            + colored("(ok to leave blank)\n", "light_green")
        )
    else:
        comments = ""

    return Review(
        raw=", ".join([ran, perfect, useful]),
        ran={"y": True, "n": False, "u": None, "": None}[ran],
        works={"y": True, "n": False, "u": None, "": None}[useful],
        perfect={"y": True, "n": False, "u": None, "": None}[perfect],
        comments=comments,
    )


def ask_for_valid_input(ran):
    while ran not in ("y", "n", "u"):
        ran = input("Invalid input. Please enter y, n, or u: ")
    return ran


def check_collection_consent() -> bool:
    path = Path(".gptc_consent")
    if path.exists() and path.read_text() == "true":
        return True
    else:
        return ask_collection_consent()


def ask_collection_consent() -> bool:
    answer = input(
        "Is it ok if we store your prompts to help improve GPT Computer? (y/n)"
    )
    while answer.lower() not in ("y", "n"):
        answer = input("Invalid input. Please enter y or n: ")

    if answer.lower() == "y":
        path = Path(".gptc_consent")
        path.write_text("true")
        print(colored("Thank you️", "light_green"))
        print()
        print(
            "(If you no longer wish to participate in data collection, delete the file .gptc_consent)"
        )
        return True
    else:
        print(
            colored(
                "No worries! GPT Computer will not collect your prompts. ❤️",
                "light_green",
            )
        )
        return False


def extract_learning(
    prompt: Prompt,
    model: str,
    temperature: float,
    config: Tuple[str, ...],
    memory: DiskMemory,
    review: Review,
) -> Learning:
    return Learning(
        prompt=prompt.to_json(),
        model=model,
        temperature=temperature,
        config=json.dumps(config),
        session=get_session(),
        logs=memory.to_json(),
        review=review,
    )


def get_session() -> str:
    path = Path(tempfile.gettempdir()) / "gpt_computer_user_id.txt"

    try:
        if path.exists():
            user_id = path.read_text()
        else:
            user_id = str(random.randint(0, 2**32))
            path.write_text(user_id)
        return user_id
    except IOError:
        return "ephemeral_" + str(random.randint(0, 2**32))
