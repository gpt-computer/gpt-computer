"""
Prompt Module

Defines the Prompt class used to structure requests to the AI model.

Classes:
    Prompt: Represents a prompt with text, optional image URLs, and entrypoint prompt.
"""

from __future__ import annotations

import json

from typing import Dict, Optional


class Prompt:
    """
    Represents a prompt with text, optional image URLs, and entrypoint prompt.
    """

    def __init__(
        self,
        text: str,
        image_urls: Optional[Dict[str, str]] = None,
        entrypoint_prompt: str = "",
    ):
        self.text = text
        self.image_urls = image_urls
        self.entrypoint_prompt = entrypoint_prompt

    def __repr__(self):
        return f"Prompt(text={self.text!r}, image_urls={self.image_urls!r})"

    def to_langchain_content(self):
        content = [{"type": "text", "text": f"Request: {self.text}"}]

        if self.image_urls:
            for name, url in self.image_urls.items():
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": url, "detail": "low"},
                }
                content.append(image_content)

        return content

    def to_dict(self):
        return {
            "text": self.text,
            "image_urls": self.image_urls,
            "entrypoint_prompt": self.entrypoint_prompt,
        }

    def to_json(self):
        return json.dumps(self.to_dict())
