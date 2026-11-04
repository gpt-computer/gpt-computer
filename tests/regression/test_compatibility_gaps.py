"""Regression tests for compatibility gaps found during the restructure audit."""

import subprocess
import sys
import warnings


def test_gptc_providers_declares_any_provider():
    """The documented lazy export works without network access at import time."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        import gptc.providers

        from gpt_computer.ai.providers.any_provider import (
            AnyProvider as CanonicalAnyProvider,
        )
        from gptc.providers import AnyProvider

    assert "AnyProvider" in gptc.providers.__all__
    assert AnyProvider is CanonicalAnyProvider

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            gptc.providers.__getattr__("DefinitelyNotAProvider")
        except AttributeError:
            pass
        else:  # pragma: no cover - defensive
            raise AssertionError("unknown attribute should raise AttributeError")


def test_core_default_package_reexports_migrated_classes():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from gpt_computer.agent.default.simple_agent import (
            SimpleAgent as NewSimpleAgent,
        )
        from gpt_computer.agent.memory.disk import DiskMemory as NewDiskMemory
        from gpt_computer.core.default import DiskExecutionEnv, DiskMemory, SimpleAgent
        from gpt_computer.execution.local import DiskExecutionEnv as NewDiskExecutionEnv

    assert DiskMemory is NewDiskMemory
    assert DiskExecutionEnv is NewDiskExecutionEnv
    assert SimpleAgent is NewSimpleAgent


def test_interfaces_mcp_reexports_legacy_implementation():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from gpt_computer.interfaces.mcp import MCPServer, MCPServer as LegacyMCPServer

    assert MCPServer is LegacyMCPServer


def test_legacy_mcp_import_warns_in_fresh_process():
    script = """
import warnings
warnings.simplefilter("always")
import gptc.mcp
print("SUCCESS")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr[-800:]
    assert "SUCCESS" in result.stdout
    assert "gptc.mcp" in result.stderr
    assert "deprecated" in result.stderr.lower()


def test_integration_aliases_are_canonical_objects():
    pytest = __import__("pytest")
    pytest.importorskip("langchain_community")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from gpt_computer.ai.integration.langchain import ChatAI, LangChainIntegration
        from gptc.integration.langchain import ChatAI as LegacyChatAI

    assert ChatAI is LangChainIntegration
    assert ChatAI is LegacyChatAI


def test_pydantic_integration_alias_is_canonical_object():
    pytest = __import__("pytest")
    pytest.importorskip("pydantic_ai")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from gpt_computer.ai.integration.pydantic_ai import (
            AIModel,
            PydanticAIIntegration,
        )
        from gptc.integration.pydantic_ai import AIModel as LegacyAIModel

    assert AIModel is PydanticAIIntegration
    assert AIModel is LegacyAIModel
