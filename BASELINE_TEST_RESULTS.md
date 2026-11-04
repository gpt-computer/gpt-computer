# Baseline Test Results

**Date**: 2026-10-29
**Phase**: Phase 0 - Baseline and Inventory (refreshed)
**Status**: Current collection is clean; focused suites verified. A full-suite re-run after the latest changes is pending.

This document records the observed test-suite state for the restructure branch.
It is evidence-based: every number below comes from a command that was actually
run in this checkout.

---

## Test Environment

- **Python**: 3.9.6 (`.venv`)
- **pytest**: 8.4.2
- **Platform**: macOS (Darwin 22.6.0), Intel
- **Installation**: project installed in `.venv`
- **Collect command**: `.venv/bin/python -m pytest tests/ -q --collect-only`

> Note: prefer invoking `.venv/bin/python -m pytest` directly. `uv run` may
> re-resolve the environment or block on network access in this checkout.

---

## Collection

```
380 tests collected in 22.23s
```

No collection errors. This supersedes the earlier draft note that reported
14 collection errors caused by Python 3.9 parsing `X | None` annotations; those
annotations have since been made compatible with Python 3.9.

---

## Verified Runs

| Date | Scope | Result | Command |
|------|-------|--------|---------|
| 2026-10-29 | Full suite (before workflow-resume and error-shim tests) | **353 passed, 20 skipped** in 279.83s | `uv run pytest tests/ -q` |
| 2026-10-29 | Orchestration package | **95 passed** in 1.76s | `uv run pytest tests/core/orchestration/ -q` |
| 2026-10-29 | Workflow engine (incl. resume tests) | **29 passed** in 1.23s | `uv run pytest tests/core/orchestration/test_workflow_engine.py -q` |
| 2026-10-29 | Public imports + provider retry | **61 passed** in 96.00s | `uv run pytest tests/regression/test_public_imports.py tests/regression/test_provider_retry.py -q` |
| 2026-10-29 | Collection | **380 collected, 0 errors** | `.venv/bin/python -m pytest tests/ -q --collect-only` |

A full-suite re-run including the newest tests was attempted but exceeded the
10-minute command budget while inside `tests/regression/test_cli_smoke.py`.
That module spawns the installed console scripts in subprocesses; in this
environment cold imports plus network-dependent startup made individual
invocations exceed the test's own 60s timeout. This is recorded as an
environment/performance limitation, not a functional failure. Re-run that module
on a warm cache or in CI before claiming full-suite verification.

---

## Skips

The 20 skips observed in the full run are environment-dependent, not failures:

- `tests/test_async_ai.py` - 15 skips (async AI paths gated on optional/runtime
  availability in this environment).
- `tests/test_install.py` - 3 skips (installation checks gated on environment).
- Remaining skips are platform/optional-dependency gates.

---

## Known Environment Limitations

- Python 3.9 is end-of-life; Google auth/api_core emit `FutureWarning`s.
- urllib3 emits `NotOpenSSLWarning` because the interpreter links LibreSSL.
- The Intel macOS host cannot import `gpt4all` (its platform probe treats the
  missing `sysctl.proc_translated` key as fatal). This blocks the `local` extra
  import smoke check here but does not establish behavior on Linux/Apple Silicon.
- `tests/regression/test_cli_smoke.py` is slow when console-script imports are
  cold and can time out under constrained network conditions.

---

## Current Assessment

- No known functional regressions in the verified scopes.
- Static import-cycle and dependency-direction tests pass.
- Compatibility imports verified by `tests/regression/test_public_imports.py`.
- Full-suite verification after the latest changes remains **NOT_RUN**.

See `docs/implementation/RESTRUCTURE_PROGRESS.md` for phase-level status.
