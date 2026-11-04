# Changelog: Repository Restructure

## Version 0.4.0 (Upcoming)

### Breaking Changes

#### Package Restructure
The repository has been restructured to establish a canonical package layout under `gpt_computer/`. Legacy import paths are deprecated but remain functional with warnings.

**New Canonical Imports:**
```python
# Old (deprecated)
from gptc import Client, Model, BaseProvider
from gpt_computer.core import BaseAgent
from gpt_computer.core.default import DiskMemory

# New (canonical)
from gpt_computer.ai.client import Client, AsyncClient
from gpt_computer.ai.models import Model
from gpt_computer.ai.providers.base import BaseProvider
from gpt_computer.agent import BaseAgent
from gpt_computer.agent.memory import DiskMemory
```

**Package Migration:**
- `gptc/` → `gpt_computer/ai/` (AI client, providers, integrations)
- `gpt_computer.core/` → `gpt_computer/agent/`, `gpt_computer/execution/`, `gpt_computer/infrastructure/`
- `gptc.codemap/` → `gpt_computer/analysis/codemap/`
- `gptc.context_os/` → `gpt_computer/analysis/context/`
- `gptc.repository_intelligence/` → `gpt_computer/analysis/repository/`
- `gpt_computer.api/` → `gpt_computer/interfaces/api/`
- `gpt_computer.applications.cli/` → `gpt_computer/interfaces/cli/`
- `gptc.mcp/` → `gpt_computer/interfaces/mcp/`

**ChatCompletion API:**
- Legacy `gptc.ChatCompletion` facade is now `gpt_computer.ai.chat_completion.ChatCompletionAPI`
- Response model remains `gpt_computer.ai.client.ChatCompletion`
- Import mapping updated to distinguish facade from response model

### Added

- Canonical package structure: `gpt_computer/ai/`, `agent/`, `execution/`, `infrastructure/`, `interfaces/`, `analysis/`
- Comprehensive migration guide (`MIGRATION_GUIDE.md`)
- Deprecation policy documentation (`DEPRECATION_POLICY.md`)
- Compatibility structure documentation (`COMPATIBILITY_STRUCTURE.md`)
- Public imports documentation (`PUBLIC_IMPORTS.md`)
- CLI entry points documentation (`CLI_ENTRY_POINTS.md`)
- Dependency rules documentation (`DEPENDENCY_RULES.md`)
- Execution security documentation (`EXECUTION_SECURITY.md`)
- MCP placement documentation (`MCP_PLACEMENT.md`)
- Provider config resolution documentation (`PROVIDER_CONFIG_RESOLUTION.md`)
- Responsibility resolution documentation (`RESPONSIBILITY_RESOLUTION.md`)
- Implementation progress tracker (`docs/implementation/RESTRUCTURE_PROGRESS.md`)
- Testing instructions for restructure review (`RESTRUCTURE_TESTING_INSTRUCTIONS.md`)

### Changed

- All legacy package shims now emit `DeprecationWarning` with migration guidance
- CLI imports are now lazy - no longer eagerly load OpenAI or legacy AI runtime
- Public import API identity preserved between canonical and legacy paths
- Static import analysis added to prevent import cycles and enforce dependency directions
- Lint cleanup across all restructure areas (0 errors in legacy `gptc` and canonical packages)

### Deprecated

**The following import paths are deprecated and will be removed in version 1.0.0:**

```
gptc.*
gpt_computer.core.*
gpt_computer.api.*
gpt_computer.applications.cli.*
gpt_computer.codemap.*
gpt_computer.context_os.*
gpt_computer.repository_intelligence.*
```

Users should update their imports following the `MIGRATION_GUIDE.md`. Legacy imports will continue to work with deprecation warnings until version 1.0.0.

### Fixed

- CLI import timeout issue - resolved by deferring heavy imports
- F821 undefined name errors in legacy compatibility package
- F811 redefinition errors in API endpoints
- E402 import ordering errors in deprecation shims
- F401 unused import errors
- E741 ambiguous variable names
- F405 star import warnings

### Migration Guide

See `MIGRATION_GUIDE.md` for detailed migration instructions and examples.

### Testing

All tests pass (83 total):
- Public import regressions: 61 passed
- E2E tests with fake provider: 16 passed
- Static architecture checks: 6 passed

### Upgrade Instructions

1. Update your code to use canonical imports (see `MIGRATION_GUIDE.md`)
2. Run your test suite - deprecation warnings will guide you to remaining updates
3. Update your dependencies if you were importing from internal modules
4. No action required if you only use public documented APIs - they remain compatible

### Questions?

Refer to:
- `MIGRATION_GUIDE.md` - Step-by-step migration instructions
- `DEPRECATION_POLICY.md` - Deprecation timeline and policy
- `RESTRUCTURE_TESTING_INSTRUCTIONS.md` - Testing after upgrade
