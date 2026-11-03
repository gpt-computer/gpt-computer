# Public Imports

**Date**: 2026-10-28
**Phase**: Phase 2 - Freeze Public Contract
**Status**: Final - Guaranteed Public API Definition

This document defines the **finite, explicit set of supported imports** that will be maintained with backward compatibility for a minimum of 12 months. All other imports are considered internal and may break without notice.

---

## Overview

The project currently has two packages:
- `gptc` - Legacy AI client library (primary public API)
- `gpt_computer` - Agent system built on top of AI clients

**Compatibility Period**: Minimum 12 months from version 0.3.0 release
**Removal Target**: Version 1.0.0

---

## Guaranteed Public API: gptc Package

The following imports are guaranteed to work with deprecation warnings during the compatibility period. After the compatibility period, they will be removed.

### Top-Level Imports

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gptc import Client` | `from gpt_computer.ai.client import Client` | Yes | `gptc/__init__.py` |
| `from gptc import AsyncClient` | `from gpt_computer.ai.client import AsyncClient` | Yes | `gptc/__init__.py` |
| `from gptc import ChatCompletion` | `from gpt_computer.ai.chat_completion import ChatCompletionAPI` | Yes | `gptc/__init__.py` |
| `from gptc import Model` | `from gpt_computer.ai.models import Model` | Yes | `gptc/__init__.py` |

### Provider Module (Dynamic Access)

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `import gptc.Provider` | `from gpt_computer.ai.providers import <provider>` | Yes | `gptc/__init__.py` (dynamic) |
| `from gptc.Provider import GPTCSpace` | `from gpt_computer.ai.providers.local import GPTCSpace` | Yes | `gptc/Provider/__init__.py` |
| `from gptc.Provider import Copilot` | `from gpt_computer.ai.providers.copilot import Copilot` | Yes | `gptc/Provider/__init__.py` |
| `from gptc.Provider import DDG` | `from gpt_computer.ai.providers.ddg import DDG` | Yes | `gptc/Provider/__init__.py` |

**Note**: The `gptc.Provider` module uses dynamic attribute access. The compatibility shim will re-export known providers dynamically.

### Submodule Imports (Client)

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gptc.client import Client` | `from gpt_computer.ai.client import Client` | Yes | `gptc/__init__.py` |
| `from gptc.client import AsyncClient` | `from gpt_computer.ai.client import AsyncClient` | Yes | `gptc/__init__.py` |
| `from gptc.client import ChatCompletion` | `from gpt_computer.ai.client import ChatCompletion` | Yes | `gptc/__init__.py` |
| `from gptc.client import ClientFactory` | `from gpt_computer.ai.client.factory import ClientFactory` | Yes | `gptc/client/__init__.py` |

### Submodule Imports (Providers)

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gptc.providers import AnyProvider` | `from gpt_computer.ai.providers.any_provider import AnyProvider` | Yes | `gptc/providers/__init__.py` |
| `from gptc.providers.openai import OpenAIProvider` | `from gpt_computer.ai.providers.openai import OpenAIProvider` | Yes | `gptc/providers/openai.py` |
| `from gptc.providers.anthropic import AnthropicProvider` | `from gpt_computer.ai.providers.anthropic import AnthropicProvider` | Yes | `gptc/providers/anthropic.py` |
| `from gptc.providers.google import GoogleProvider` | `from gpt_computer.ai.providers.google import GoogleProvider` | Yes | `gptc/providers/google.py` |
| `from gptc.providers.groq import GroqProvider` | `from gpt_computer.ai.providers.groq import GroqProvider` | Yes | `gptc/providers/groq.py` |
| `from gptc.providers.mistral import MistralProvider` | `from gpt_computer.ai.providers.mistral import MistralProvider` | Yes | `gptc/providers/mistral.py` |
| `from gptc.providers.cohere import CohereProvider` | `from gpt_computer.ai.providers.cohere import CohereProvider` | Yes | `gptc/providers/cohere.py` |
| `from gptc.providers.local import LocalProvider` | `from gpt_computer.ai.providers.local import LocalProvider` | Yes | `gptc/providers/local.py` |

### Submodule Imports (Errors)

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gptc.errors import MissingAuthError` | `from gpt_computer.ai.errors import MissingAuthError` | Yes | `gptc/errors/__init__.py` |
| `from gptc.errors import ResponseError` | `from gpt_computer.ai.errors import ResponseError` | Yes | `gptc/errors/__init__.py` |
| `from gptc.errors import ResponseStatusError` | `from gpt_computer.ai.errors import ResponseStatusError` | Yes | `gptc/errors/__init__.py` |
| `from gptc.errors import MissingRequirementsError` | `from gpt_computer.ai.errors import MissingRequirementsError` | Yes | `gptc/errors/__init__.py` |
| `from gptc.errors import PaymentRequiredError` | `from gpt_computer.ai.errors import PaymentRequiredError` | Yes | `gptc/errors/__init__.py` |
| `from gptc.errors import VersionNotFoundError` | `from gpt_computer.ai.errors import VersionNotFoundError` | Yes | `gptc/errors/__init__.py` |

### Submodule Imports (MCP)

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gptc.mcp.server import MCPServer` | `from gpt_computer.interfaces.mcp.server import MCPServer` | Yes | `gptc/mcp/__init__.py` |
| `from gptc.mcp.server import MCPRequest` | `from gpt_computer.interfaces.mcp.server import MCPRequest` | Yes | `gptc/mcp/__init__.py` |

### Submodule Imports (Integration)

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gptc.integration.langchain import ChatAI` | `from gpt_computer.ai.integration.langchain import ChatAI` | Yes | `gptc/integration/langchain.py` |
| `from gptc.integration.langchain import LangChainIntegration` | `from gpt_computer.ai.integration.langchain import LangChainIntegration` | Yes | `gptc/integration/langchain.py` |
| `from gptc.integration.pydantic_ai import AIModel` | `from gpt_computer.ai.integration.pydantic_ai import AIModel` | Yes | `gptc/integration/pydantic_ai.py` |
| `from gptc.integration.pydantic_ai import PydanticAIIntegration` | `from gpt_computer.ai.integration.pydantic_ai import PydanticAIIntegration` | Yes | `gptc/integration/pydantic_ai.py` |

**Note**: `ChatAI` and `AIModel` are the implementation classes. `LangChainIntegration`
and `PydanticAIIntegration` are explicit aliases for the same objects, so both
names are supported and compare equal via `is`.

---

## Guaranteed Public API: gpt_computer Package

The following imports from `gpt_computer.core` are guaranteed to work with deprecation warnings during the compatibility period.

### Core AI Imports

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gpt_computer.core.ai import AI` | `from gpt_computer.ai.client import AI` | Yes | `gpt_computer/core/__init__.py` |
| `from gpt_computer.core.ai import Message` | `from gpt_computer.ai.client import Message` | Yes | `gpt_computer/core/__init__.py` |
| `from gpt_computer.core.ai_async import AsyncAI` | `from gpt_computer.ai.client import AsyncAI` | Yes | `gpt_computer/core/__init__.py` |
| `from gpt_computer.core.ai_async import AIResponse` | `from gpt_computer.ai.client import AIResponse` | Yes | `gpt_computer/core/__init__.py` |

### Core Agent Imports

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gpt_computer.core.base_agent import BaseAgent` | `from gpt_computer.agent import BaseAgent` | Yes | `gpt_computer/core/__init__.py` |
| `from gpt_computer.core.agent.react import ReActAgent` | `from gpt_computer.agent.react import ReActAgent` | Yes | `gpt_computer/core/__init__.py` |

### Core Memory Imports

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gpt_computer.core.default.disk_memory import DiskMemory` | `from gpt_computer.agent.memory.disk import DiskMemory` | Yes | `gpt_computer/core/default/__init__.py` |

### Core Execution Imports

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gpt_computer.core.default.disk_execution_env import DiskExecutionEnv` | `from gpt_computer.execution.local import DiskExecutionEnv` | Yes | `gpt_computer/core/default/__init__.py` |

### Core Utility Imports

| Old Import | New Import | Deprecated | Compatibility Module |
|------------|------------|------------|---------------------|
| `from gpt_computer.core.files_dict import FilesDict` | `from gpt_computer.infrastructure.files.files_dict import FilesDict` | Yes | `gpt_computer/core/__init__.py` |
| `from gpt_computer.core.prompt import Prompt` | `from gpt_computer.agent.prompts.prompt import Prompt` | Yes | `gpt_computer/core/__init__.py` |

---

## Intentionally NOT Supported

The following imports are **intentionally not supported** and will not have compatibility shims:

### gptc Internal Interfaces

| Old Import | Reason | Migration Path |
|------------|--------|----------------|
| `gptc.cli` | Internal CLI implementation | Use `gpt_computer.interfaces.cli` |
| `gptc.gui` | Internal GUI implementation | Use `gpt_computer.interfaces.gui` |
| `gptc.api` | Internal API implementation | Use `gpt_computer.interfaces.api` |
| `gptc.tray` | Internal tray implementation | Use `gpt_computer.interfaces.tray` |
| `gptc.cookies` | Internal cookie management | Use new location (TBD) |
| `gptc.config` | Internal configuration | Use `infrastructure.config.settings` |
| `gptc.debug` | Internal debugging | Not a public API |
| `gptc.image` | Internal image handling | Use new location (TBD) |
| `gptc.tools` | Internal tool implementations | Use new location (TBD) |

### gpt_computer Internal Modules

| Old Import | Reason | Migration Path |
|------------|--------|----------------|
| `gpt_computer.core.*` (not listed above) | Internal core modules | Use new layered structure |
| `gpt_computer.api` | Will be restructured to `interfaces/api` | Use `gpt_computer.interfaces.api` |
| `gpt_computer.applications` | Will be restructured to `interfaces` | Use `gpt_computer.interfaces` |

---

## Total Count

**Guaranteed Public Imports**: 30
- gptc top-level: 4
- gptc Provider: 4
- gptc client: 4
- gptc providers: 7
- gptc errors: 6
- gptc MCP: 2
- gptc integration: 2
- gpt_computer core: 5

**Compatibility Modules to Create**: 8
- `gptc/__init__.py`
- `gptc/Provider/__init__.py`
- `gptc/client/__init__.py`
- `gptc/providers/__init__.py`
- `gptc/providers/*.py` (individual provider shims)
- `gptc/errors/__init__.py`
- `gptc/mcp/__init__.py`
- `gptc/integration/__init__.py`
- `gpt_computer/core/__init__.py`
- `gpt_computer/core/default/__init__.py`

---

## Deprecation Policy

### Warning Behavior

All compatibility shims will emit `DeprecationWarning` with `stacklevel=2`:

```python
import warnings
warnings.warn(
    "Importing from 'gptc' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.client import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2
)
```

### Version Schedule

- **Current**: 0.1.1
- **Restructure release**: 0.3.0 (compatibility shims added)
- **Deprecation period**: 0.3.x → 0.4.x → 0.5.x (minimum 12 months)
- **Removal scheduled**: 1.0.0

### Enabling Warnings

To see deprecation warnings:

```python
import warnings
warnings.simplefilter("always")
```

Or via command line:

```bash
python -W always your_script.py
```

---

## Testing Requirements

For each guaranteed import, a test must verify:

1. **Import Works**: The old import successfully imports the class/function
2. **Warning Emitted**: A deprecation warning is emitted
3. **API Identity**: The imported object is the same as the new import (using `is` operator)
4. **Functionality**: The imported object works correctly

Example test:

```python
def test_legacy_client_import():
    """Test that legacy Client import works with deprecation warning."""
    import warnings
    import subprocess
    import sys
    
    test_script = """
import warnings
warnings.simplefilter("always")
from gptc import Client
print("SUCCESS")
"""
    result = subprocess.run([sys.executable, "-c", test_script], capture_output=True, text=True)
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout
    assert "deprecated" in result.stderr.lower()
```

---

## Migration Guide Reference

See **MIGRATION_GUIDE.md** (to be created) for:
- Step-by-step migration instructions
- Before/after code examples
- Troubleshooting common issues
- Timeline and deprecation schedule

---

**Last Updated**: 2026-10-28
**Phase**: Phase 2 - Freeze Public Contract
**Status**: Final - Guaranteed Public API Definition

### Top-Level Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc import version` | `gptc.version` | etc/tool/update.py, etc/unittest/main.py | Candidate for public API |
| `import gptc` | `gptc` | etc/tool/copilot.py, etc/unittest/asyncio.py | Package-level access |

### Client Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.client import Client` | `gptc.client` | etc/examples/video.py, etc/unittest/asyncio.py, etc/unittest/integration.py | **Guaranteed Public API** |
| `from gptc.client import AsyncClient` | `gptc.client` | gptc/api/__init__.py, gptc/integration/langchain.py, etc/unittest/integration.py | **Guaranteed Public API** |
| `from gptc.client import ChatCompletion` | `gptc.client` | gptc/api/__init__.py, etc/unittest/asyncio.py, etc/unittest/integration.py | **Guaranteed Public API** |
| `from gptc.client import ClientFactory` | `gptc.client` | projects/discord-bot/bot.py | **Guaranteed Public API** |
| `from gptc.client import ImagesResponse` | `gptc.client` | gptc/api/__init__.py | Candidate for public API |
| `from gptc.client.helper import filter_none` | `gptc.client.helper` | gptc/api/__init__.py | Internal utility |
| `from gptc.client.stubs import ChatCompletionMessage` | `gptc.client.stubs` | gptc/integration/langchain.py | Internal type stubs |

### Provider Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.providers.any_provider import AnyProvider` | `gptc.providers.any_provider` | gptc/api/__init__.py, projects/discord-bot/bot.py | **Guaranteed Public API** |
| `from gptc.providers.base_provider import BaseProvider` | `gptc.providers.base_provider` | etc/unittest/models.py, etc/unittest/mocks.py | Base class, internal use |
| `from gptc.providers.base_provider import ProviderModelMixin` | `gptc.providers.base_provider` | etc/unittest/models.py, gptc/Provider/needs_auth/DeepSeek.py | Mixin, internal use |
| `from gptc.providers.base_provider import AsyncAuthedProvider` | `gptc.providers.base_provider` | gptc/Provider/needs_auth/DeepSeek.py | Internal base class |
| `from gptc.providers.base_provider import AsyncGeneratorProvider` | `gptc/providers.base_provider` | etc/unittest/test_tool_support_enhanced.py, etc/unittest/tool_support_provider.py | Internal base class |
| `from gptc.providers.base_provider import wait_for` | `gptc.providers.base_provider` | etc/unittest/test_provider_asyncio.py | Internal utility |
| `from gptc.providers.response import BaseConversation` | `gptc.providers.response` | gptc/api/__init__.py | Internal data structure |
| `from gptc.providers.response import JsonConversation` | `gptc.providers.response` | gptc/api/__init__.py, gptc/Provider/needs_auth/deepseek/stream.py | Internal data structure |
| `from gptc.providers.response import Reasoning` | `gptc.providers.response` | gptc/Provider/needs_auth/deepseek/stream.py, etc/unittest/thinking.py | Internal data structure |
| `from gptc.providers.response import AuthResult` | `gptc.providers.response` | etc/unittest/mocks.py | Internal data structure |
| `from gptc.providers.response import ImageResponse` | `gptc.providers.response` | etc/unittest/mocks.py | Internal data structure |
| `from gptc.providers.response import AudioResponse` | `gptc.providers.response` | gptc/api/__init__.py | Internal data structure |
| `from gptc.providers.response import FinishReason` | `gptc.providers.response` | etc/unittest/test_tool_support_enhanced.py, etc/unittest/tool_support_provider.py | Internal enum |
| `from gptc.providers.response import ToolCalls` | `gptc.providers.response` | etc/unittest/test_tool_support_enhanced.py, etc/unittest/tool_support_provider.py | Internal data structure |
| `from gptc.providers.types import ProviderType` | `gptc.providers.types` | gptc/api/__init__.py | Internal enum |
| `from gptc.providers.config_provider import ...` | `gptc.providers.config_provider` | etc/unittest/config_provider.py | Internal provider |
| `from gptc.providers.retry_provider import IterListProvider` | `gptc.providers.retry_provider` | etc/unittest/retry_provider.py | Internal provider |
| `from gptc.providers.tool_support import ToolSupportProvider` | `gptc.providers.tool_support` | etc/unittest/test_tool_support_enhanced.py, etc/unittest/tool_support_provider.py | Internal provider |
| `from gptc.providers.any_model_map import model_map` | `gptc.providers.any_model_map` | etc/unittest/test_gemini.py | Internal mapping |
| `from gptc.providers.any_model_map import ...` | `gptc.providers.any_model_map` | gptc/api/__init__.py | Internal mapping |
| `from gptc.providers.helper import get_last_user_message` | `gptc.providers.helper` | gptc/Provider/needs_auth/DeepSeek.py | Internal utility |

### Provider Module (Legacy)

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `import gptc.Provider` | `gptc.Provider` | etc/examples/video.py, etc/unittest/models.py, etc/unittest/integration.py, etc/unittest/test_api_quota.py | **Guaranteed Public API** (dynamic access) |
| `from gptc.Provider import __getattr__` | `gptc.Provider` | etc/unittest/models.py | Internal mechanism |
| `from gptc.Provider import GPTCSpace` | `gptc.Provider` | projects/discord-bot/bot.py | **Guaranteed Public API** |
| `from gptc.Provider import ProviderUtils` | `gptc.Provider` | gptc/api/__init__.py | Internal utility |
| `from gptc.Provider import ProviderLoader` | `gptc.Provider` | gptc/api/__init__.py | Internal utility |
| `from gptc.Provider import Copilot` | `gptc.Provider` | etc/unittest/integration.py | **Guaranteed Public API** |
| `from gptc.Provider import DDG` | `gptc.Provider` | etc/unittest/integration.py | **Guaranteed Public API** |
| `from gptc.Provider.needs_auth.Gemini import ...` | `gptc.Provider.needs_auth.Gemini` | etc/unittest/test_gemini.py | Internal provider implementation |
| `from gptc.Provider.needs_auth.DeepSeek import ...` | `gptc.Provider.needs_auth.DeepSeek` | gptc/Provider/needs_auth/DeepSeek.py | Internal provider implementation |
| `from gptc.Provider.needs_auth.mini_max.MiniMax import MiniMax` | `gptc.Provider.needs_auth.mini_max.MiniMax` | etc/unittest/test_minimax.py | Internal provider implementation |
| `from gptc.Provider.needs_auth.LMArena import ...` | `gptc.Provider.needs_auth.LMArena` | gptc/Provider/needs_auth/LMArena.py | Internal provider implementation |

### Error Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.errors import MissingAuthError` | `gptc.errors` | gptc/Provider/needs_auth/DeepSeek.py, etc/unittest/models.py, etc/unittest/mocks.py, etc/unittest/test_gemini.py, etc/unittest/test_auth_retry.py | **Guaranteed Public API** |
| `from gptc.errors import ResponseError` | `gptc.errors` | gptc/Provider/needs_auth/DeepSeek.py, etc/unittest/test_gemini.py | **Guaranteed Public API** |
| `from gptc.errors import ResponseStatusError` | `gptc.errors` | etc/unittest/test_gemini.py | **Guaranteed Public API** |
| `from gptc.errors import MissingRequirementsError` | `gptc.errors` | etc/unittest/backend.py, etc/unittest/web_search.py | **Guaranteed Public API** |
| `from gptc.errors import PaymentRequiredError` | `gptc.errors` | etc/unittest/models.py | **Guaranteed Public API** |
| `from gptc.errors import VersionNotFoundError` | `gptc.errors` | etc/unittest/main.py | **Guaranteed Public API** |
| `from gptc.errors import ...` | `gptc.errors` | gptc/api/__init__.py | Multiple error types |

### Image Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.image import to_bytes` | `gptc.image` | gptc/Provider/needs_auth/DeepSeek.py, gptc/Provider/needs_auth/LMArena.py | Internal utility |
| `from gptc.image import detect_file_type` | `gptc.image` | gptc/Provider/needs_auth/DeepSeek.py, gptc/Provider/needs_auth/LMArena.py | Internal utility |
| `from gptc.image import EXTENSIONS_MAP` | `gptc.image` | gptc/api/__init__.py | Internal constant |
| `from gptc.image import is_data_an_media` | `gptc.image` | gptc/api/__init__.py | Internal utility |
| `from gptc.image import process_image` | `gptc.image` | gptc/api/__init__.py | Internal utility |
| `from gptc.image import is_safe_url` | `gptc.image` | gptc/api/__init__.py | Internal utility |
| `from gptc.image.copy_images import get_media_dir` | `gptc.image.copy_images` | gptc/api/__init__.py | Internal utility |
| `from gptc.image.copy_images import copy_media` | `gptc.image.copy_images` | gptc/api/__init__.py | Internal utility |
| `from gptc.image.copy_images import get_source_url` | `gptc.image.copy_images` | gptc/api/__init__.py | Internal utility |
| `from gptc.image.copy_images import secure_filename` | `gptc.image.copy_images` | gptc/api/__init__.py | Internal utility |

### Cookie Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.cookies import read_cookie_files` | `gptc.cookies` | gptc/api/__init__.py | Internal utility |
| `from gptc.cookies import get_cookies_dir` | `gptc.cookies` | gptc/api/__init__.py | Internal utility |
| `import gptc.cookies` | `gptc.cookies` | gptc/gui/run.py, etc/unittest/test_cli.py | Internal module |

### Config Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.config import CONFIG_DIR` | `gptc.config` | gptc/cli/client.py | Internal constant |
| `from gptc.config import COOKIES_DIR` | `gptc.config` | gptc/cli/client.py | Internal constant |
| `from gptc.config import DEFAULT_PORT` | `gptc.config` | gptc/api/__init__.py | Internal constant |
| `from gptc.config import DEFAULT_TIMEOUT` | `gptc.config` | gptc/api/__init__.py | Internal constant |
| `from gptc.config import DEFAULT_STREAM_TIMEOUT` | `gptc.config` | gptc/api/__init__.py | Internal constant |
| `from gptc.config import AppConfig` | `gptc.config` | gptc/api/__init__.py | Internal class |

### Debug Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc import debug` | `gptc.debug` | gptc/Provider/needs_auth/DeepSeek.py, gptc/cli/client.py, gptc/Provider/qwen/cookie_generator.py, gptc/Provider/needs_auth/deepseek/stream.py, gptc/gui/run.py, gptc/api/__init__.py, etc/unittest/__main__.py | Internal debugging utility |
| `import gptc.debug` | `gptc.debug` | gptc/api/__init__.py | Internal debugging utility |

### Requests Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.requests import has_cdp` | `gptc.requests` | gptc/api/__init__.py | Internal utility |
| `from gptc.requests import StreamSession` | `gptc.requests` | gptc/Provider/needs_auth/DeepSeek.py | Internal utility |
| `from gptc.requests import raise_for_status` | `gptc.requests` | gptc/Provider/needs_auth/DeepSeek.py | Internal utility |
| `from gptc.requests import FormData` | `gptc.requests` | gptc/Provider/needs_auth/DeepSeek.py | Internal utility |
| `from gptc.requests import DEFAULT_HEADERS` | `gptc.requests` | gptc/Provider/needs_auth/DeepSeek.py | Internal constant |
| `from gptc.requests.cdp import ...` | `gptc.requests.cdp` | etc/unittest/test_cdp_parallel.py | Internal CDP support |

### Typing Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.typing import AsyncResult` | `gptc.typing` | gptc/Provider/needs_auth/DeepSeek.py | Internal type |
| `from gptc.typing import Messages` | `gptc.typing` | gptc/Provider/needs_auth/DeepSeek.py | Internal type |

### Tools Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.tools.tool_support import ...` | `gptc.tools.tool_support` | etc/unittest/test_tool_support_enhanced.py | Internal tool support |
| `from gptc.tools.run_tools import async_iter_run_tools` | `gptc.tools.run_tools` | etc/unittest/tool_support_provider.py | Internal tool execution |
| `from gptc.tools.run_tools import ThinkingProcessor` | `gptc.tools.run_tools` | etc/unittest/thinking.py | Internal tool execution |
| `from gptc.tools.run_tools import Reasoning` | `gptc.tools.run_tools` | etc/unittest/thinking.py | Internal type |

### MCP Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.mcp.server import MCPServer` | `gptc.mcp.server` | projects/discord-bot/mcp_tools.py, etc/unittest/mcp.py | **Candidate for public API** |
| `from gptc.mcp.server import MCPRequest` | `gptc.mcp.server` | projects/discord-bot/mcp_tools.py, etc/unittest/mcp.py | **Candidate for public API** |
| `from gptc.mcp.tools import ...` | `gptc.mcp.tools` | etc/unittest/mcp.py | Internal tool definitions |
| `from gptc.mcp.pa_provider import execute_safe_code` | `gptc.mcp.pa_provider` | etc/unittest/mcp.py | Internal provider |
| `from gptc.mcp.pa_provider import get_workspace_dir` | `gptc.mcp.pa_provider` | etc/unittest/mcp.py | Internal utility |
| `from gptc.mcp.pa_provider import SAFE_MODULES` | `gptc.mcp.pa_provider` | etc/unittest/mcp.py | Internal constant |

### Integration Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.integration.langchain import ...` | `gptc.integration.langchain` | gptc/integration/langchain.py, docs/examples/open_llms/langchain_interface.py | **Candidate for public API** |
| `from gptc.integration.pydantic_ai import ...` | `gptc.integration.pydantic_ai` | gptc/integration/pydantic_ai.py | **Candidate for public API** |

### API Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `import gptc.api` | `gptc.api` | gptc/api/run.py, etc/unittest/test_api_quota.py | Internal API module |
| `from gptc.api.tool_loop_detection import detect_tool_loop` | `gptc.api.tool_loop_detection` | etc/unittest/test_tool_loop_detection.py | Internal utility |
| `from gptc.api.tool_loop_detection import ToolLoopError` | `gptc.api.tool_loop_detection` | etc/unittest/test_tool_loop_detection.py | Internal error |

### GUI Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.gui import get_gui_app` | `gptc.gui` | gptc/api/__init__.py | Internal GUI module |

### CLI Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.cli import main` | `gptc.cli` | gptc/__main__.py | Internal CLI entry point |
| `from gptc.cli import get_api_parser` | `gptc.cli` | etc/unittest/test_cli.py | Internal CLI parser |
| `from gptc.cli import run_api_args` | `gptc.cli` | etc/unittest/test_cli.py | Internal CLI parser |
| `import gptc.cli` | `gptc.cli` | etc/unittest/test_cli.py | Internal CLI module |

### Models Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gptc.models import __models__` | `gptc.models` | etc/unittest/models.py | Internal model registry |
| `from gptc.models import ModelRegistry` | `gptc.models` | etc/unittest/test_gemini.py | Internal model registry |

---

## gpt_computer Package Imports

### Core AI Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.core.ai import AI` | `gpt_computer.core.ai` | tests/core/test_ai.py, tests/core/agent/test_react.py, gpt_computer/tools/custom_steps.py, gpt_computer/test/async_test_utils.py, projects/bench-template/benchmark_agent.py | **Guaranteed Public API** |
| `from gpt_computer.core.ai import Message` | `gpt_computer.core.ai` | gpt_computer/test/async_test_utils.py | **Guaranteed Public API** |
| `from gpt_computer.core.ai_async import AsyncAI` | `gpt_computer.core.ai_async` | tests/test_async_ai.py | **Guaranteed Public API** |
| `from gpt_computer.core.ai_async import AIResponse` | `gpt_computer.core.ai_async` | tests/test_async_ai.py | **Guaranteed Public API** |

### Core Agent Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.core.base_agent import BaseAgent` | `gpt_computer.core.base_agent` | gpt_computer/test/async_test_utils.py | **Guaranteed Public API** |
| `from gpt_computer.core.agent.react import ReActAgent` | `gpt_computer.core.agent.react` | tests/core/agent/test_react.py, tests/api/test_api.py | **Guaranteed Public API** |

### Core Default Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.core.default.disk_memory import DiskMemory` | `gpt_computer.core.default.disk_memory` | tests/core/test_logging.py, tests/core/default/test_steps.py, tests/core/default/test_simple_agent.py, tests/core/default/test_disk_file_repository.py, tests/applications/cli/test_main.py, tests/applications/cli/test_learning.py, tests/applications/cli/test_cli_agent.py, projects/bench-template/benchmark_agent.py, gpt_computer/tools/custom_steps.py | **Guaranteed Public API** |
| `from gpt_computer.core.default.disk_execution_env import DiskExecutionEnv` | `gpt_computer.core.default.disk_execution_env` | tests/core/default/test_disk_execution_env.py, tests/core/default/test_simple_agent.py, tests/applications/cli/test_cli_agent.py, projects/bench-template/benchmark_agent.py, gpt_computer/tools/custom_steps.py | **Guaranteed Public API** |
| `from gpt_computer.core.default.simple_agent import SimpleAgent` | `gpt_computer.core.default.simple_agent` | tests/core/default/test_simple_agent.py | **Guaranteed Public API** |
| `from gpt_computer.core.default.paths import ENTRYPOINT_FILE` | `gpt_computer.core.default.paths` | tests/core/default/test_steps.py, tests/core/default/test_simple_agent.py, tests/core/default/test_disk_execution_env.py, tests/applications/cli/test_cli_agent.py, projects/bench-template/benchmark_agent.py, gpt_computer/tools/custom_steps.py | Internal constant |
| `from gpt_computer.core.default.paths import PREPROMPTS_PATH` | `gpt_computer.core.default.paths` | tests/core/default/test_steps.py, projects/bench-template/benchmark_agent.py | Internal constant |
| `from gpt_computer.core.default.paths import memory_path` | `gpt_computer.core.default.paths` | tests/core/default/test_disk_memory.py, tests/applications/cli/test_cli_agent.py | Internal utility |
| `from gpt_computer.core.default.steps import improve_fn` | `gpt_computer.core.default.steps` | projects/bench-template/benchmark_agent.py, gpt_computer/tools/custom_steps.py | Internal function |
| `from gpt_computer.core.default.steps import curr_fn` | `gpt_computer.core.default.steps` | gpt_computer/tools/custom_steps.py | Internal function |
| `from gpt_computer.core.default.steps import setup_sys_prompt` | `gpt_computer.core.default.steps` | gpt_computer/tools/custom_steps.py | Internal function |
| `from gpt_computer.core.default.steps import salvage_correct_hunks` | `gpt_computer.core.default.steps` | tests/core/test_salvage_correct_hunks.py | Internal function |

### Core Orchestration Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.core.orchestration.models import ...` | `gpt_computer.core.orchestration.models` | tests/core/orchestration/test_workflow_engine.py, tests/core/orchestration/test_models.py, tests/core/orchestration/test_messaging.py, tests/core/orchestration/test_human_in_the_loop.py, tests/core/orchestration/test_agent_coordinator.py | Internal orchestration models |
| `from gpt_computer.core.orchestration.workflow_engine import ...` | `gpt_computer.core.orchestration.workflow_engine` | tests/core/orchestration/test_workflow_engine.py | Internal workflow engine |
| `from gpt_computer.core.orchestration.agent_coordinator import ...` | `gpt_computer.core.orchestration.agent_coordinator` | tests/core/orchestration/test_workflow_engine.py, tests/core/orchestration/test_agent_coordinator.py | Internal coordinator |
| `from gpt_computer.core.orchestration.messaging import ...` | `gpt_computer.core.orchestration.messaging` | tests/core/orchestration/test_messaging.py | Internal messaging |
| `from gpt_computer.core.orchestration.human_in_the_loop import ...` | `gpt_computer.core.orchestration.human_in_the_loop` | tests/core/orchestration/test_human_in_the_loop.py | Internal HIL module |

### Core Agent Tools Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.core.agent_tools.registry import ToolRegistry` | `gpt_computer.core.agent_tools.registry` | tests/core/agent/test_react.py | Internal registry |

### Core Utility Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.core.files_dict import FilesDict` | `gpt_computer.core.files_dict` | tests/core/test_salvage_correct_hunks.py, tests/core/default/test_steps.py, tests/core/default/test_simple_agent.py, tests/core/default/test_disk_execution_env.py, tests/core/test_chat_to_files.py, tests/applications/cli/test_main.py, tests/applications/cli/test_cli_agent.py, projects/bench-template/benchmark_agent.py, gpt_computer/tools/custom_steps.py, gpt_computer/test/async_test_utils.py | **Guaranteed Public API** |
| `from gpt_computer.core.chat_to_files import parse_diffs` | `gpt_computer.core.chat_to_files` | tests/core/test_chat_to_files.py, tests/core/test_chat_to_files_enhanced.py | Internal utility |
| `from gpt_computer.core.diff import is_similar` | `gpt_computer.core.diff` | tests/core/test_chat_to_files.py | Internal utility |
| `from gpt_computer.core.git import ...` | `gpt_computer.core.git` | tests/core/test_git.py | Internal git wrapper |
| `from gpt_computer.core.linting import Linting` | `gpt_computer.core.linting` | tests/core/default/test_steps.py | Internal linting |
| `from gpt_computer.core.preprompts_holder import PrepromptsHolder` | `gpt_computer.core.preprompts_holder` | tests/core/default/test_steps.py, projects/bench-template/benchmark_agent.py, gpt_computer/tools/custom_steps.py | Internal holder |
| `from gpt_computer.core.prompt import Prompt` | `gpt_computer.core.prompt` | tests/core/default/test_steps.py, tests/core/default/test_simple_agent.py, tests/applications/cli/test_main.py, tests/applications/cli/test_learning.py, tests/applications/cli/test_cli_agent.py, projects/bench-template/benchmark_agent.py, gpt_computer/tools/custom_steps.py | **Guaranteed Public API** |
| `from gpt_computer.core.token_usage import Tokenizer` | `gpt_computer.core.token_usage` | tests/core/test_token_usage.py | Internal tokenizer |
| `from gpt_computer.core.token_usage import TokenUsageLog` | `gpt_computer.core.token_usage` | tests/core/test_token_usage.py, tests/core/test_token_usage_enhanced.py | Internal logging |
| `from gpt_computer.core.structured_logging import get_logger` | `gpt_computer.core.structured_logging` | tests/test_async_ai.py | Internal logging |
| `from gpt_computer.core.structured_logging import setup_structured_logging` | `gpt_computer.core.structured_logging` | tests/test_async_ai.py | Internal logging |
| `from gpt_computer.core.tracing import setup_tracing` | `gpt_computer.core.tracing` | tests/test_async_ai.py | Internal tracing |
| `from gpt_computer.core.base_memory import BaseMemory` | `gpt_computer.core.base_memory` | projects/bench-template/benchmark_agent.py, gpt_computer/tools/custom_steps.py | Base class, internal use |
| `from gpt_computer.core.base_execution_env import BaseExecutionEnv` | `gpt_computer.core.base_execution_env` | projects/bench-template/benchmark_agent.py, gpt_computer/tools/custom_steps.py | Base class, internal use |

### Applications CLI Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.applications.cli.main import app` | `gpt_computer.applications.cli.main` | tests/applications/cli/test_list_command.py | Internal CLI app |
| `from gpt_computer.applications.cli.main import load_prompt` | `gpt_computer.applications.cli.main` | tests/applications/cli/test_main.py | Internal CLI utility |
| `import gpt_computer.applications.cli.main as main` | `gpt_computer.applications.cli.main` | tests/applications/cli/test_main.py | Internal CLI module |
| `from gpt_computer.applications.cli.cli_agent import CliAgent` | `gpt_computer.applications.cli.cli_agent` | tests/applications/cli/test_cli_agent.py | Internal CLI agent |
| `from gpt_computer.applications.cli import learning` | `gpt_computer.applications.cli.learning` | tests/applications/cli/test_learning.py | Internal learning module |
| `from gpt_computer.applications.cli.learning import Learning` | `gpt_computer.applications.cli.learning` | tests/applications/cli/test_learning.py, tests/applications/cli/test_collection_consent.py | Internal learning class |
| `from gpt_computer.applications.cli.file_selector import FileSelector` | `gpt_computer.applications.cli.file_selector` | tests/core/test_file_selector_enhancements.py | Internal file selector |

### API Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.api.main import app` | `gpt_computer.api.main` | tests/api/test_api.py | Internal API app |

### Tools Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.tools.custom_steps import clarified_gen` | `gpt_computer.tools.custom_steps` | tests/applications/cli/test_cli_agent.py | Internal step function |
| `from gpt_computer.tools.custom_steps import lite_gen` | `gpt_computer.tools.custom_steps` | tests/applications/cli/test_cli_agent.py | Internal step function |

### Repository Intelligence Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.repository_intelligence.models import ...` | `gpt_computer.repository_intelligence.models` | gpt_computer/repository_intelligence/*.py | Internal models |
| `from gpt_computer.codemap.models import CodemapConfig` | `gpt_computer.codemap.models` | gpt_computer/repository_intelligence/tree_sitter_analyzer.py | Internal config |

### Benchmark Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.benchmark.bench_config import ...` | `gpt_computer.benchmark.bench_config` | tests/benchmark/test_BenchConfig.py | Internal config |

### Test Imports

| Import Path | Module | Used In | Status |
|-------------|--------|---------|--------|
| `from gpt_computer.test.async_test_utils import ...` | `gpt_computer.test.async_test_utils` | tests/test_async_ai.py | Internal test utilities |

---

## Analysis Summary

### Confirmed Public APIs (High Priority for Compatibility)

**gptc Package**:
1. `gptc.client.Client` - Synchronous AI client
2. `gptc.client.AsyncClient` - Asynchronous AI client
3. `gptc.client.ChatCompletion` - Chat completion interface
4. `gptc.client.ClientFactory` - Client factory
5. `gptc.providers.any_provider.AnyProvider` - Universal provider
6. `gptc.Provider` - Dynamic provider access (module-level)
7. `gptc.Provider.GPTCSpace` - Hugging Face space provider
8. `gptc.Provider.Copilot` - Copilot provider
9. `gptc.Provider.DDG` - DuckDuckGo provider
10. `gptc.errors.MissingAuthError` - Authentication error
11. `gptc.errors.ResponseError` - Response error
12. `gptc.errors.ResponseStatusError` - HTTP status error
13. `gptc.errors.MissingRequirementsError` - Missing dependency error
14. `gptc.errors.PaymentRequiredError` - Payment error
15. `gptc.errors.VersionNotFoundError` - Version error
16. `gptc.version` - Version information
17. `gptc.mcp.server.MCPServer` - MCP server
18. `gptc.mcp.server.MCPRequest` - MCP request
19. `gptc.integration.langchain` - LangChain integration
20. `gptc.integration.pydantic_ai` - Pydantic AI integration

**gpt_computer Package**:
1. `gpt_computer.core.ai.AI` - Synchronous AI interface
2. `gpt_computer.core.ai.Message` - Message type
3. `gpt_computer.core.ai_async.AsyncAI` - Asynchronous AI interface
4. `gpt_computer.core.ai_async.AIResponse` - AI response type
5. `gpt_computer.core.base_agent.BaseAgent` - Base agent class
6. `gpt_computer.core.agent.react.ReActAgent` - ReAct agent implementation
7. `gpt_computer.core.default.disk_memory.DiskMemory` - Disk-based memory
8. `gpt_computer.core.default.disk_execution_env.DiskExecutionEnv` - Disk execution environment
9. `gpt_computer.core.default.simple_agent.SimpleAgent` - Simple agent implementation
10. `gpt_computer.core.files_dict.FilesDict` - File dictionary utility
11. `gpt_computer.core.prompt.Prompt` - Prompt class

### Internal APIs (Not Guaranteed for Compatibility)

Most imports are internal implementation details used by:
- Tests
- Internal modules
- Example code
- Utility functions

These should **not** be part of the guaranteed public API unless there's evidence of external usage.

### External Dependencies to Investigate

1. **projects/discord-bot/** - External project using gptc
2. **etc/examples/** - Example code that users may reference
3. **docs/examples/** - Documentation examples

These should be checked for actual external usage patterns.

---

## Next Steps

1. Review this inventory with maintainers to confirm public API
2. Check external projects (discord-bot, etc.) for additional usage patterns
3. Prioritize compatibility shims for confirmed public APIs
4. Document deprecation warnings for internal APIs that should not be used
5. Create compatibility module structure based on this inventory

---

**Last Updated**: 2026-10-28
**Phase**: Phase 0 - Baseline and Inventory
