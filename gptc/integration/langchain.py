"""Compatibility shim for the legacy LangChain integration module."""

import warnings

warnings.warn(
    "Importing from 'gptc.integration.langchain' is deprecated and will be "
    "removed in version 1.0.0. Use 'gpt_computer.ai.integration.langchain' "
    "instead. See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.integration.langchain import (  # noqa: E402
    ChatAI,
    LangChainIntegration,
    new_convert_message_to_dict,
)

__all__ = ["ChatAI", "LangChainIntegration", "new_convert_message_to_dict"]
