"""Compatibility re-exports for the AI client base classes.

The full client implementation now lives in :mod:`gpt_computer.ai.client._impl`
and :mod:`gpt_computer.ai.client.types`.
"""

from gpt_computer.ai.client.types import Client as BaseClient, Proxies

__all__ = ["BaseClient", "Proxies"]
