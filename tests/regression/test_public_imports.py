"""
Public Import Compatibility Tests

Verifies that all guaranteed public imports from PUBLIC_IMPORTS.md work correctly
with deprecation warnings where applicable.
"""

import subprocess
import sys

import pytest

# New structure imports (should work without warnings)
NEW_IMPORTS = [
    ("gpt_computer.ai.client", "Client"),
    ("gpt_computer.ai.client", "AsyncClient"),
    ("gpt_computer.ai.client", "ClientFactory"),
    ("gpt_computer.ai.models", "Model"),
    ("gpt_computer.ai.providers.base", "BaseProvider"),
    ("gpt_computer.ai.providers.base", "ProviderType"),
    ("gpt_computer.ai.errors", "GPTCError"),
    ("gpt_computer.execution", "BaseExecutionEnv"),
    ("gpt_computer.execution", "DiskExecutionEnv"),
    ("gpt_computer.agent", "BaseAgent"),
    ("gpt_computer.agent", "Prompt"),
    ("gpt_computer.agent.memory", "BaseMemory"),
    ("gpt_computer.agent.memory", "DiskMemory"),
    ("gpt_computer.infrastructure.config", "get_settings"),
    ("gpt_computer.infrastructure.files", "FilesDict"),
    ("gpt_computer.infrastructure.git", "is_git_installed"),
    ("gpt_computer.infrastructure.diff", "is_similar"),
    ("gpt_computer.infrastructure.linting", "Linting"),
    ("gpt_computer.infrastructure.logging", "get_logger"),
    ("gpt_computer.infrastructure.tracing", "setup_tracing"),
    ("gpt_computer.analysis.codemap", "PythonAnalyzer"),
    ("gpt_computer.analysis.repository", "TreeSitterAnalyzer"),
    ("gpt_computer.analysis.context", "ContextManager"),
    ("gpt_computer.interfaces.api", "app"),
    ("gpt_computer.interfaces.cli", "CliAgent"),
]


@pytest.mark.parametrize("module_name, attr_name", NEW_IMPORTS)
def test_new_imports_work(module_name, attr_name):
    """Verify all new structure imports work."""
    import importlib

    mod = importlib.import_module(module_name)
    assert hasattr(mod, attr_name), f"{module_name} has no attribute {attr_name}"
    assert getattr(mod, attr_name) is not None


# Legacy imports that should work with deprecation warnings
LEGACY_IMPORTS = [
    ("gptc", "Client"),
    ("gptc", "AsyncClient"),
    ("gptc", "ChatCompletion"),
    ("gptc", "Model"),
    ("gptc.providers", "BaseProvider"),
    ("gptc.providers", "ProviderType"),
    ("gpt_computer.core", "BaseAgent"),
    ("gpt_computer.core.ai", "AI"),
    ("gpt_computer.core.base_agent", "BaseAgent"),
    ("gpt_computer.core.files_dict", "FilesDict"),
    ("gpt_computer.core.git", "is_git_installed"),
    ("gpt_computer.core.diff", "is_similar"),
    ("gpt_computer.core.linting", "Linting"),
    ("gpt_computer.core.config", "get_settings"),
    ("gpt_computer.core.prompt", "Prompt"),
    ("gpt_computer.core.base_memory", "BaseMemory"),
    ("gpt_computer.core.base_execution_env", "BaseExecutionEnv"),
    ("gpt_computer.core.default.disk_execution_env", "DiskExecutionEnv"),
    ("gpt_computer.core.default.disk_memory", "DiskMemory"),
    ("gpt_computer.core.default.paths", "PREPROMPTS_PATH"),
    ("gpt_computer.core.default.constants", "MAX_EDIT_REFINEMENT_STEPS"),
    ("gpt_computer.core.default.steps", "gen_code"),
    ("gpt_computer.core.chat_to_files", "chat_to_files_dict"),
    ("gpt_computer.core.logging_config", "setup_logging"),
    ("gpt_computer.core.structured_logging", "get_logger"),
    ("gpt_computer.core.tracing", "setup_tracing"),
    ("gpt_computer.codemap", "PythonAnalyzer"),
    ("gpt_computer.repository_intelligence", "TreeSitterAnalyzer"),
    ("gpt_computer.context_os", "ContextManager"),
    ("gpt_computer.api", "app"),
    ("gpt_computer.applications.cli", "CliAgent"),
]


@pytest.mark.parametrize("module_name, attr_name", LEGACY_IMPORTS)
def test_legacy_imports_work(module_name, attr_name):
    """Verify all legacy imports work with deprecation warnings (subprocess)."""
    script = f"""
import warnings
warnings.simplefilter("always")
from {module_name} import {attr_name}
print("SUCCESS")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    assert (
        result.returncode == 0
    ), f"Import failed for {module_name}.{attr_name}: {result.stderr[:200]}"
    assert "SUCCESS" in result.stdout


def test_ai_client_api_identity():
    """Verify migrated client, facade, and response-model identities."""
    from gpt_computer.ai.chat_completion import ChatCompletionAPI
    from gpt_computer.ai.client import (
        AsyncClient as NewAsyncClient,
        ChatCompletion as NewChatCompletion,
        ChatCompletion as NewCompletionModel,
        Client as NewClient,
    )
    from gptc import (
        AsyncClient as LegacyAsyncClient,
        ChatCompletion as LegacyCompletionAPI,
        Client as LegacyClient,
    )
    from gptc.client import ChatCompletion as LegacyChatCompletion

    assert LegacyCompletionAPI is ChatCompletionAPI
    assert LegacyCompletionAPI is not NewCompletionModel
    assert LegacyClient is NewClient
    assert LegacyAsyncClient is NewAsyncClient
    assert LegacyChatCompletion is NewChatCompletion


def test_api_identity_all():
    """Verify identity for other migrated public imports."""
    from gpt_computer.ai.models import Model as NewModel
    from gptc import Model as LegacyModel

    assert LegacyModel is NewModel

    from gpt_computer.agent import BaseAgent as NewBA
    from gpt_computer.core.base_agent import BaseAgent as LegacyBA

    assert LegacyBA is NewBA

    from gpt_computer.core.files_dict import FilesDict as LegacyFD
    from gpt_computer.infrastructure.files import FilesDict as NewFD

    assert LegacyFD is NewFD

    from gpt_computer.api import app as LegacyApp
    from gpt_computer.interfaces.api import app as NewApp

    assert LegacyApp is NewApp


def test_legacy_errors_import_warns_and_preserves_identity():
    """gptc.errors is a shim over gpt_computer.ai.errors."""
    script = """
import warnings
warnings.simplefilter("always")
from gptc.errors import MissingAuthError
from gpt_computer.ai.errors import MissingAuthError as NewMissingAuthError
assert MissingAuthError is NewMissingAuthError
print("SUCCESS")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr[:500]
    assert "SUCCESS" in result.stdout
    assert "gptc.errors" in result.stderr
    assert "deprecated" in result.stderr.lower()


def test_legacy_errors_exports_all_public_names():
    """Every documented gptc.errors name resolves to the canonical class."""
    import gpt_computer.ai.errors as canonical
    import gptc.errors as legacy

    for name in legacy.__all__:
        assert getattr(legacy, name) is getattr(canonical, name)


def test_provider_package_exports_base_types():
    """gpt_computer.ai.providers exposes the canonical base provider types."""
    import gpt_computer.ai.providers as providers
    import gpt_computer.ai.providers.base as base

    for name in ("BaseProvider", "BaseRetryProvider", "ProviderType", "Streaming"):
        assert getattr(providers, name) is getattr(base, name)
        assert name in providers.__all__
