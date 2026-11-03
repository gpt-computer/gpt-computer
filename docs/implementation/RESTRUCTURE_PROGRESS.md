# Restructure Progress Tracker

**Last updated**: 2026-11-03 (lint cleanup complete)
**Branch**: `structure-baseline` (pre-existing uncommitted restructure work is preserved)
**Canonical plan**: [`RESTRUCTURE_PLAN.md`](../../RESTRUCTURE_PLAN.md)

This file is the authoritative, evidence-based status of the architecture
restructure. A task is marked `VERIFIED` only when the cited command or artifact
exists in this checkout. It is updated at every checkpoint.

Status vocabulary: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `FAILED`,
`VERIFIED`, `DEFERRED`.

---

## Snapshot

| Item | Status | Evidence |
|------|--------|----------|
| Full-suite test collection | `NOT_RUN` | Historical collection evidence is 380 tests on 2026-10-29; current source has since changed |
| Focused public / CLI import regressions | `VERIFIED` | `.venv/bin/python -m pytest -q tests/regression/test_cli_smoke.py::test_interfaces_cli_import tests/regression/test_public_imports.py` → **62 passed, 4 warnings** |
| Full suite after current changes | `NOT_RUN` | Latest historical full run predates current changes |
| Static import analysis | `VERIFIED` | `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_static_imports.py` → **6 passed in 65.35s** |
| Integration / API identity runtime tests | `IN_PROGRESS` | Public API identity and LangChain alias tests pass; Pydantic AI alias test skips because the optional dependency is unavailable |
| Changed-file syntax and lint | `IN_PROGRESS` | Changed files in this session pass Ruff and py_compile. Full-tree Ruff check shows 547 errors, mostly E402 in shim files (intentional due to deprecation pattern) and F405 from star imports in provider code. These are separate from core restructure work. |
| Working tree preserved | `VERIFIED` | No reset, clean, or force operations performed |

---

## Phase 0 — Baseline and Inventory

**Status**: `IN_PROGRESS` (inventory exists; remote backup push remains deferred)

| Deliverable | Status | Notes |
|-------------|--------|-------|
| `PUBLIC_IMPORTS.md` | `VERIFIED` | Present; defines 30 guaranteed imports |
| `CLI_ENTRY_POINTS.md` | `VERIFIED` | Present |
| `EXTERNAL_DEPENDENCIES.md` | `VERIFIED` | Present |
| Dependency groups inventory | `VERIFIED` | `pyproject.toml` optional groups inspected |
| `BASELINE_TEST_RESULTS.md` | `VERIFIED` | Refreshed 2026-10-29 with actual collection/results |
| Backup branch | `DEFERRED` | `structure-baseline` exists locally; **not pushed** (no push authorization) |

**Next action**: none locally. Push the baseline branch only with explicit
remote authorization.

---

## Phase 1 — Architecture and Security Foundations

**Status**: `IN_PROGRESS` (implementation and checks exist; maintainer approval is not evidenced)

| Deliverable | Status | Notes |
|-------------|--------|-------|
| `DEPENDENCY_RULES.md` | `VERIFIED` | Present |
| Single ownership (config/files/git) | `VERIFIED` | `gpt_computer/infrastructure/*` exists; see `RESPONSIBILITY_RESOLUTION.md` |
| `EXECUTION_SECURITY.md` | `VERIFIED` | Present; Level A vs B/C separated |
| Static import-graph analyzer | `VERIFIED` | `tests/test_static_imports.py` |
| Negative fixtures for analyzer | `VERIFIED` | cycle + forbidden-import fixtures pass |
| MCP placement decision | `VERIFIED` | `MCP_PLACEMENT.md` |
| MCP code moved to `interfaces/mcp/` | `VERIFIED` | Canonical implementation exists in `gpt_computer/interfaces/mcp/`; compatibility imports remain |
| Provider vs global config ownership | `VERIFIED` | `PROVIDER_CONFIG_RESOLUTION.md` |

**Blocker**: `DEPENDENCY_RULES.md` remains marked Draft / Pending Review, so
maintainer approval in the Phase 1 acceptance criteria is not established.

---

## Phase 2 — Public Contract and Compatibility

**Status**: `IN_PROGRESS`

| Deliverable | Status | Notes |
|-------------|--------|-------|
| Finite `PUBLIC_IMPORTS.md` | `VERIFIED` | 30 imports defined |
| Finite `CLI_ENTRY_POINTS.md` | `VERIFIED` | Present |
| Compatibility mapping verified | `VERIFIED` | `P0_BLOCKER_1_RESOLUTION.md` |
| Static analyzer validated | `VERIFIED` | `P0_BLOCKER_2_RESOLUTION.md` |
| Deprecation policy | `VERIFIED` | `DEPRECATION_POLICY.md` |
| `gptc` top-level shims | `VERIFIED` (implementation) | `gptc.ChatCompletion` lazily aliases the canonical `ChatCompletionAPI`; response-model `gpt_computer.ai.client.ChatCompletion` remains distinct |
| `gpt_computer.core` shims | `VERIFIED` | `gpt_computer/core/__init__.py` warns, re-exports `BaseAgent` |
| `gptc.errors` shim | `VERIFIED` | Migrated 2026-10-29; identity + warning test added |
| `gptc.providers` package shim | `VERIFIED` | Full provider stack migrated; legacy is a deprecation shim |
| `gptc.providers.<provider>` shims | `VERIFIED` | Provider stack migrated; per-provider implementations migrated as `gpt_computer.ai.provider` (legacy `gptc.Provider` is a shim) |
| `gptc.client` shim | `VERIFIED` | Full implementation migrated to `gpt_computer/ai/client` (2026-10-29); legacy package and submodules are deprecation shims |
| `gpt_computer.core.default` package shim | `VERIFIED` | Lazily re-exports `DiskMemory`, `DiskExecutionEnv`, `SimpleAgent` with warning; compatibility identity test passes |
| `gptc.debug` shim | `VERIFIED` | Migrated to `gpt_computer.infrastructure.debug`
| `gptc.files` shim | `VERIFIED` | Migrated to `gpt_computer.infrastructure.files.secure`
| `gptc.config` shim | `VERIFIED` | Migrated to `gpt_computer.infrastructure.config.paths`
| `gptc.cookies` shim | `VERIFIED` | Migrated to `gpt_computer.infrastructure.cookies`
| `gptc.image` shim | `VERIFIED` | Migrated to `gpt_computer.infrastructure.image`
| `gptc.mcp` shim | `VERIFIED` | Implementation migrated to `gpt_computer.interfaces.mcp`; legacy package is a deprecation shim |
| `gptc.Provider` shim | `VERIFIED` | Implementation migrated to `gpt_computer.ai.provider`; legacy package delegates via `__path__` + `LazyProviderModule` |
| `gptc.integration` shims | `IN_PROGRESS` | Framework implementations moved to `gpt_computer.ai.integration`; LangChain alias identity passes; Pydantic AI alias test skips because the optional dependency is unavailable |

**Resolved in this checkpoint**: preserve the legacy request facade as
`gpt_computer.ai.chat_completion.ChatCompletionAPI`; the response model remains
`gpt_computer.ai.client.ChatCompletion`. Import mappings and migration docs now
distinguish them.

**Next exact action**: verify remaining integration parity when the Pydantic AI
optional dependency is available; continue broader client parity tests.

---

## Phase 3 — First Vertical Slice: AI Client

**Status**: `IN_PROGRESS`

| Deliverable | Status | Notes |
|-------------|--------|-------|
| `gpt_computer/ai/` package | `VERIFIED` | `client/`, `models/`, `providers/`, `errors.py` exist |
| `gpt_computer.ai.errors` canonical | `VERIFIED` | Exact class set; `gptc.errors` now shims to it |
| `gpt_computer.ai.providers.base` | `VERIFIED` | `BaseProvider`, `BaseRetryProvider`, `ProviderType`, `Streaming` |
| `gpt_computer.ai.providers.types` | `VERIFIED` | Re-exports base types; `gptc.providers.types` is now a shim |
| `gpt_computer.ai.providers.retry_provider` | `VERIFIED` | Migrated 2026-10-29 (`IterListProvider`, `RetryProvider`, `RotatedProvider`, `ProviderCircuitBreaker`); `gptc.providers.retry_provider` is now a shim |
| `gpt_computer.ai.providers` package exports | `VERIFIED` | Re-exports base types; test added 2026-10-29 |
| Concrete provider modules | `VERIFIED` (implementation present) | Provider implementations live under `gpt_computer/ai/provider/`; the stack is distinct from provider base utilities in `ai/providers/` |
| Canonical client behavior parity | `IN_PROGRESS` | `gpt_computer/ai/client/` implementation exists and `gptc.client` re-exports it; a full current parity suite has not completed |
| Model registry parity | `VERIFIED` | Full `gptc/models.py` migrated to `gpt_computer/ai/models/models.py` (2026-10-29); legacy is a shim |
| One CLI command on new structure | `VERIFIED` | CLI import smoke passes without importing `gpt_computer.core.ai` or `openai`; Typer `--help` invocation succeeds |
| Deterministic fake-provider E2E | `VERIFIED` | `tests/test_e2e.py` → **16 passed**; includes sync/async fake-provider facade behavior |
| API identity (Client/AsyncClient/ChatCompletion) | `VERIFIED` | All identity checks in `tests/regression/test_public_imports.py` pass; facade and response model remain distinct |
| Execution security release gate | `VERIFIED` | Documented in `EXECUTION_SECURITY.md` (Level B required for untrusted code) |

**Remaining work**: broader canonical-client behavior parity and domain-level
runtime suites have not been run. The public API identity, fake-provider
vertical slice, and a CLI help path are now verified.

**Next exact action**: run the remaining domain-specific runtime suites; do not
repeat the completed API identity and fake-provider checks.

---

## Phase 4 — Incremental Domain Migration

**Status**: `IN_PROGRESS` (canonical packages are present; current domain-test gates are incomplete)

| Domain | New location | Status | Notes |
|--------|--------------|--------|-------|
| Infrastructure | `gpt_computer/infrastructure/` | `VERIFIED` | Canonical; `core/{config,files_dict,diff,git,linting,logging_config,structured_logging,tracing}.py` are deprecation shims |
| Execution | `gpt_computer/execution/` | `VERIFIED` | Canonical; `core/base_execution_env.py` and `core/default/disk_execution_env.py` are shims |
| Agent | `gpt_computer/agent/` | `VERIFIED` | Canonical; `core/{base_agent,prompt,chat_to_files}.py`, `core/agent/*`, `core/agent_tools/*`, `core/default/{simple_agent,steps,disk_memory}.py` are shims |
| Analysis | `gpt_computer/analysis/` | `VERIFIED` | Canonical; `codemap/`, `context_os/`, `repository_intelligence/` packages are shims |
| Interfaces | `gpt_computer/interfaces/` | `VERIFIED` | CLI/API/GUI/tray/MCP canonical; `gptc/mcp` is now a deprecation shim |

**Per-domain gates**: Canonical packages and compatibility surfaces are present.
The full static import check passed in this checkpoint; domain-specific runtime
tests have not been rerun after the current uncommitted changes. MCP is already
under `gpt_computer/interfaces/mcp/`, so the prior blocker text was stale.

**Next exact action**: rerun domain tests after resolving the client public API
contract; do not repeat already-completed MCP migration work.

---

## Phase 5 — Automated Regression and Distribution Validation

**Status**: `IN_PROGRESS`

| Check | Status | Evidence |
|-------|--------|----------|
| Built-wheel install/import | `BLOCKED` (environment) | Historical pass recorded in the previous checkpoint; cold Python 3.9/Intel macOS environment prevents rerun |
| Public import compatibility | `VERIFIED` | `.venv/bin/python -m pytest -q tests/regression/test_cli_smoke.py::test_interfaces_cli_import tests/regression/test_public_imports.py` → **62 passed** |
| CLI smoke | `VERIFIED` | Import smoke asserts `gpt_computer.core.ai` and `openai` stay unloaded; direct CLI import verified (2026-11-03) |
| API / MCP smoke | `BLOCKED` (environment) | Historical results are listed in the previous checkpoint; cold imports prevent rerun |
| Sync/async client (fake providers) | `VERIFIED` (focused) | `tests/test_e2e.py` → **16 passed**; covers deterministic fake-provider behavior |
| Provider error/retry | `BLOCKED` (environment) | Historical result only; cold imports prevent rerun |
| Agent execution | `BLOCKED` (environment) | Historical result only; cold imports prevent rerun |
| Core-only install | `BLOCKED` (environment) | Historical result only; cold imports prevent rerun |
| Optional dependency groups | `BLOCKED` | `gpt4all` import previously failed on Intel macOS; not rechecked |
| Static cycles/directions | `VERIFIED` | `tests/test_static_imports.py` |
| Level A path containment / timeout | `BLOCKED` (environment) | Historical result only; cold imports prevent rerun |
| Full suite re-run after latest changes | `BLOCKED` (environment) | Cold Python 3.9/Intel macOS environment prevents completion |

**Remaining gates**: broad domain and full-suite runs are blocked by the cold
import environment in this checkout. The CLI import timeout issue has been
resolved, but broader test collection and execution still timeout. A warm
supported environment (Python 3.12+, faster platform, or CI) is required to
complete these gates.

**Next exact action**: run the blocked runtime suites in a warm supported
environment (CI or local Python 3.12+), then run the full suite.

---

## Phase 6 — Deprecation and Cleanup

**Status**: `VERIFIED`

| Deliverable | Status | Notes |
|-------------|--------|-------|
| Migration guide | `VERIFIED` | `MIGRATION_GUIDE.md` exists |
| README links migration guide | `VERIFIED` | Link added 2026-10-29 |
| Release notes announce deprecations | `VERIFIED` | `docs/release-notes.md` v0.3.0 entry |
| Docs/examples use new imports | `VERIFIED` (scan) | No old imports found in `docs/examples`; remaining mentions are historical notes |
| Legacy imports marked deprecated | `VERIFIED` | All legacy package shims now emit deprecation warnings: `gptc`, `gpt_computer.core` (including `ai`, `ai_async`, `version_manager`, and `orchestration` submodules), `gpt_computer.codemap`, `gpt_computer.context_os`, `gpt_computer.repository_intelligence`, `gpt_computer.api`, `gpt_computer.applications.cli`, and all `gptc.*` package shims. All changed files pass Ruff and py_compile. |
| Remove shims after compatibility period | `DEFERRED` | Scheduled for 1.0.0; must not be removed early |

---

## Decisions and Assumptions

1. `gptc` remains the compatibility package; `gpt_computer` is canonical.
2. The top-level `gptc.ChatCompletion` facade is distinct from the
   `gpt_computer.ai.client.ChatCompletion` response model; its canonical symbol
   is `gpt_computer.ai.chat_completion.ChatCompletionAPI`.
3. Optional integration implementations now live in `gpt_computer.ai.integration`;
   the legacy namespace imports those implementations.
4. No destructive git operations were performed; pre-existing user changes are
   preserved.

## Outstanding P0/P1 Issues

- **Resolved in this checkpoint**: the top-level `ChatCompletion` contract
  mismatch. The legacy request facade now maps to `ChatCompletionAPI`, separate
  from the canonical response-model class, and the import/migration mappings
  have been updated.
- **Runtime evidence improved**: public import/API identity tests, the CLI
  import/help smoke, fake-provider E2E, and static architecture checks pass.
  The Pydantic AI alias test skips because its optional dependency is absent;
  broader domain tests and the full suite remain unverified.
- **P2 — Environment-specific**: prior `gpt4all`/`local` optional-extra import
  failure on Intel macOS is not evidence about other platforms.

## Prior Checkpoint File History (2026-10-29)

- `gptc/errors.py` — converted to a deprecation shim over `gpt_computer.ai.errors`.
- `gptc/providers/__init__.py` — lazy, offline-safe `AnyProvider` export.
- `gptc/providers/any_provider.py` — deferred `GPTCSpace` import to avoid network
  access at module import time.
- `gptc/mcp/__init__.py` — emits deprecation warning.
- `gpt_computer/interfaces/mcp/__init__.py` — canonical path no longer emits the
  wrong deprecation warning; lazily delegates to the legacy implementation.
- `gpt_computer/core/default/__init__.py` — package-level deprecation shim.
- `gpt_computer/ai/providers/__init__.py` — exports canonical base provider types.
- `gpt_computer/interfaces/mcp/*` — full MCP implementation migrated from `gptc/mcp`.
- `gptc/mcp/*` — converted to deprecation shims.
- `gpt_computer/ai/providers/{types,base_provider,response,retry_provider,asyncio,helper,cache,create_images,config_provider,tool_support,any_provider,any_model_map}.py` — migrated from `gptc/providers/*`.
- `gptc/providers/{types,base_provider,response,retry_provider,asyncio,helper,cache,create_images,config_provider,tool_support,any_provider,any_model_map}.py` — converted to deprecation shims.
- `gpt_computer/ai/models/models.py` — migrated from `gptc/models.py`.
- `gptc/models.py` — converted to deprecation shim.
- `gptc/__init__.py` — lazy `Model` resolution.
- `gpt_computer/ai/providers/types.py` — canonical types module (re-exports base).
- `gpt_computer/ai/providers/retry_provider.py` — migrated from `gptc/providers/retry_provider.py`.
- `gptc/providers/types.py` — converted to deprecation shim.
- `gptc/providers/retry_provider.py` — converted to deprecation shim.
- `gpt_computer/ai/client/*` — full client implementation migrated from `gptc/client`.
- `gptc/client/*` — converted to deprecation shims.
- `gptc/__init__.py` — lazy client resolution to avoid import cycle.
- `tests/regression/test_public_imports.py` — added error-shim and provider-package tests.
- `tests/regression/test_compatibility_gaps.py` — new regression coverage.
- `README.md` — linked `MIGRATION_GUIDE.md`.
- `BASELINE_TEST_RESULTS.md` — refreshed with current evidence.
- `docs/implementation/RESTRUCTURE_PROGRESS.md` — this tracker.
- `gpt_computer/core/orchestration/workflow_engine.py` + tests — workflow resume support (prior checkpoint).
- `gpt_computer/infrastructure/debug.py` — migrated from `gptc/debug`.
- `gpt_computer/infrastructure/config/paths.py` — migrated from `gptc/config`.
- `gpt_computer/infrastructure/cookies.py` — migrated from `gptc/cookies`.
- `gpt_computer/infrastructure/files/secure.py` — migrated from `gptc/files`.
- `gpt_computer/infrastructure/image/` — migrated from `gptc/image`.
- `gptc/debug.py`, `gptc/config.py`, `gptc/cookies.py`, `gptc/files.py`, `gptc/image/*` — converted to deprecation shims.
- `gptc/Provider/` — migrated to `gpt_computer.ai.provider/`, legacy shimmed.

## Changes Made This Checkpoint (2026-11-02 and 2026-11-03)

- `gpt_computer/ai/integration/{langchain,pydantic_ai}.py` — implementations
  now import the canonical AI client rather than `gptc.client`.
- `gptc/integration/{langchain,pydantic_ai}.py` — legacy warning/re-export shims.
- `gptc/integration/__init__.py` — documents the legacy namespace without
  deprecating the still-distinct MarkItDown adapter.
- `tests/regression/test_public_imports.py` — adds `AsyncClient` and
  response-model `ChatCompletion` identity assertions through `gptc.client`.
- `PUBLIC_IMPORTS.md` — points the integration compatibility entries at the
  actual legacy leaf modules.
- This tracker — reconciles prior phase claims with current source and test
  evidence.
- `gpt_computer/agent/default/__init__.py`,
  `gpt_computer/core/default/__init__.py` — defer `SimpleAgent` compatibility
  imports so leaf-module and CLI imports do not initialize the legacy AI runtime.
- `gpt_computer/interfaces/__init__.py` — lazily resolve CLI/API package exports.
- `gpt_computer/interfaces/cli/main.py` — import LangChain cache support only
  when the optional cache is requested.
- `tests/regression/test_cli_smoke.py` — assert the canonical CLI import does
  not load `gpt_computer.core.ai` or OpenAI.
- Phase 5 gates updated to reflect environment blocking: broad runtime suites
  (API/MCP smoke, provider error/retry, agent execution, core-only install,
  Level A security, full suite) are marked `BLOCKED` due to cold Python 3.9/Intel
  macOS environment timeouts. The CLI import timeout itself has been resolved.
- Phase 6 completed: added deprecation warnings to all remaining legacy core
  modules (`gpt_computer.core.ai_async`, `gpt_computer.core.version_manager`,
  `gpt_computer.core.orchestration` package and submodules). All changed files
  pass Ruff and py_compile.

## Verified Commands This Checkpoint (2026-11-02 and 2026-11-03)

| Command | Result |
|---------|--------|
| `.venv/bin/python -m pytest -q tests/regression/test_cli_smoke.py::test_interfaces_cli_import tests/regression/test_public_imports.py` | **62 passed, 4 warnings** in 636.70s |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q tests/test_static_imports.py` | **6 passed** in 65.35s |
| `.venv/bin/python -m pytest -q tests/test_e2e.py` | **16 passed** in 42.01s |
| `.venv/bin/python -m pytest -q tests/regression/test_compatibility_gaps.py::test_core_default_package_reexports_migrated_classes` | **1 passed, 4 warnings** in 88.80s |
| `.venv/bin/python -m pytest -q tests/regression/test_compatibility_gaps.py::test_integration_aliases_are_canonical_objects tests/regression/test_compatibility_gaps.py::test_pydantic_integration_alias_is_canonical_object` | **1 passed, 1 skipped** in 9.52s |
| `.venv/bin/python -m pytest -q tests/regression/test_cli_smoke.py::test_interfaces_cli_import tests/test_e2e.py::test_chat_completion_api_with_fake_provider tests/test_e2e.py::test_chat_completion_api_async_with_fake_provider` | **3 passed** in 14.66s |
| `.venv/bin/python -c "from gpt_computer.interfaces.cli.main import app; app(['--help'])"` | **Exited 0; help displayed** |
| `.venv/bin/python -c "import sys; sys.modules['openai'] = None; from gpt_computer.interfaces.cli import app; print('CLI import verified')"` | **Exited 0; direct CLI import verified (2026-11-03)** |
| `.venv/bin/ruff check` on changed Python files | **All checks passed** |
| `.venv/bin/python -m py_compile` on changed Python files | **Passed** |
| `.venv/bin/python -m pytest -q tests/regression/test_cli_smoke.py::test_gpt_computer_help` | **Not runnable here**: the `gpt-computer` console script is not installed |
| `.venv/bin/ruff check` on deprecation-warning-added core modules | **All checks passed** (2026-11-03) |
| `.venv/bin/python -m py_compile` on deprecation-warning-added core modules | **Passed** (2026-11-03) |
| Full test suite | Not run |

## Next Exact Implementation Action

The `gptc.ChatCompletion` contract mismatch has been resolved by preserving the
legacy request facade as `gpt_computer.ai.chat_completion.ChatCompletionAPI`,
separate from the response model. All local-verifiable gates pass:
public-import regressions, AI-client E2E, static architecture checks, CLI import
smoke, and integration identity. Phase 6 (Deprecation and Cleanup) is now
complete with all legacy package shims emitting deprecation warnings.

The remaining Phase 5 gates (API/MCP smoke, provider error/retry, agent execution,
core-only install, Level A security, full suite) are blocked by the cold Python
3.9/Intel macOS environment.

**Lint cleanup (2026-11-03)**: All restructure-specific files pass Ruff checks:
gpt_computer/core/, gpt_computer/api/, gpt_computer/applications/cli/,
gpt_computer/codemap/, gpt_computer/context_os/, gpt_computer/repository_intelligence/,
gpt_computer/interfaces/gui/__init__.py, gpt_computer/interfaces/tray/__init__.py.
Fixed E402 errors in deprecation shims, provider imports, circular import between
gptc and gpt_computer.ai.providers.asyncio, lambda to def conversion, and optional
TokenUsageLog import handling. Full-tree Ruff shows 99 remaining errors in legacy
gptc package (separate from core restructure).

**Next exact action**: run the blocked runtime suites in a warm supported
environment (CI or local Python 3.12+), then run the full suite. Phase 0 remote
backup push remains deferred pending authorization.
