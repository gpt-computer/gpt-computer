"""
CLI Data Collection Module

Provides functionality to collect and send user feedback/learning data.
"""

from __future__ import annotations

from typing import Tuple

from gpt_computer.agent.memory.disk import DiskMemory
from gpt_computer.agent.prompt import Prompt
from gpt_computer.interfaces.cli.learning import (
    Learning,
    Review,
    extract_learning,
    human_review_input,
)


def send_learning(learning: Learning):
    import rudderstack.analytics as rudder_analytics

    rudder_analytics.write_key = "2Re4kqwL61GDp7S8ewe6K5dbogG"
    rudder_analytics.dataPlaneUrl = "https://gptcomputerezm.dataplane.rudderstack.com"

    rudder_analytics.track(
        user_id=learning.session,
        event="learning",
        properties=learning.to_dict(),
    )


def collect_learnings(
    prompt: Prompt,
    model: str,
    temperature: float,
    config: any,
    memory: DiskMemory,
    review: Review,
):
    learnings = extract_learning(prompt, model, temperature, config, memory, review)
    try:
        send_learning(learnings)
    except RuntimeError:
        max_size = 32 << 10
        current_size = len(learnings.to_json().encode("utf-8"))
        overflow = current_size - max_size
        remove_length = overflow + len(f"[REMOVED {overflow} CHARACTERS]") + 100
        learnings.logs = (
            learnings.logs[:-remove_length]
            + f"\n\n[REMOVED {remove_length} CHARACTERS]"
        )
        print("WARNING: learning too big, removing some parts.")
        try:
            send_learning(learnings)
        except RuntimeError:
            print("Sending learnings crashed despite truncation.")


def collect_and_send_human_review(
    prompt: Prompt,
    model: str,
    temperature: float,
    config: Tuple[str, ...],
    memory: DiskMemory,
):
    review = human_review_input()
    if review:
        collect_learnings(prompt, model, temperature, config, memory, review)
