"""Compatibility shim for the legacy Pydantic AI integration module."""

import warnings

warnings.warn(
    "Importing from 'gptc.integration.pydantic_ai' is deprecated and will be "
    "removed in version 1.0.0. Use 'gpt_computer.ai.integration.pydantic_ai' "
    "instead. See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.integration.pydantic_ai import (  # noqa: E402
    AIModel,
    PydanticAIIntegration,
    new_infer_model,
    patch_infer_model,
)

__all__ = [
    "AIModel",
    "PydanticAIIntegration",
    "new_infer_model",
    "patch_infer_model",
]
