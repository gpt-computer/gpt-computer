# Testing Instructions for Repository Restructure PR

This document provides step-by-step instructions for reviewers to verify the repository restructure changes.

## Quick Verification (5 minutes)

### 1. Run Public Import Tests
```bash
.venv/bin/python -m pytest tests/regression/test_public_imports.py -v
```
**Expected:** 61 passed, 4 warnings

### 2. Run E2E Tests
```bash
.venv/bin/python -m pytest tests/test_e2e.py -v
```
**Expected:** 16 passed

### 3. Run Static Architecture Tests
```bash
.venv/bin/python -m pytest tests/test_static_imports.py -v
```
**Expected:** 6 passed

### 4. Check Lint Status on Restructure Files
```bash
.venv/bin/ruff check gpt_computer/core/ gpt_computer/api/ gpt_computer/applications/cli/ gpt_computer/codemap/ gpt_computer/context_os/ gpt_computer/repository_intelligence/ gpt_computer/interfaces/gui/ gpt_computer/interfaces/tray/
```
**Expected:** All checks passed (0 errors)

### 5. Check Lint Status on Legacy Package
```bash
.venv/bin/ruff check gptc/
```
**Expected:** All checks passed (0 errors)

## Detailed Verification (15 minutes)

### Canonical Package Structure

Verify the canonical packages exist:
```bash
ls -la gpt_computer/ai/
ls -la gpt_computer/agent/
ls -la gpt_computer/execution/
ls -la gpt_computer/infrastructure/
ls -la gpt_computer/interfaces/
ls -la gpt_computer/analysis/
```

### Legacy Compatibility Shims

Verify legacy imports still work with deprecation warnings:
```bash
.venv/bin/python -c "
import warnings
warnings.simplefilter('always')
from gptc import Client
print('SUCCESS')
"
```
**Expected:** SUCCESS with DeprecationWarning

### CLI Import Smoke Test

Verify CLI imports don't eagerly load OpenAI:
```bash
.venv/bin/python -c "
import sys
import gpt_computer.interfaces.cli
assert 'gpt_computer.core.ai' not in sys.modules
assert 'openai' not in sys.modules
print('CLI import verified')
"
```
**Expected:** CLI import verified

### API Identity Check

Verify canonical and legacy API identity:
```bash
.venv/bin/python -c "
from gpt_computer.ai.client import Client as CanonicalClient
from gptc import Client as LegacyClient
assert CanonicalClient is LegacyClient
print('API identity verified')
"
```
**Expected:** API identity verified

## Migration Verification

### Test Canonical Imports Work

```bash
.venv/bin/python -c "
from gpt_computer.ai.client import Client, AsyncClient
from gpt_computer.ai.models import Model
from gpt_computer.ai.providers.base import BaseProvider
from gpt_computer.agent import BaseAgent
from gpt_computer.execution import DiskExecutionEnv
from gpt_computer.infrastructure.config import get_settings
print('All canonical imports work')
"
```
**Expected:** All canonical imports work

### Test Legacy Imports with Warnings

```bash
.venv/bin/python -W all -c "
from gptc import Client, Model, BaseProvider
from gpt_computer.core import BaseAgent
from gpt_computer.core.default import DiskMemory
print('All legacy imports work with warnings')
"
```
**Expected:** All legacy imports work with warnings (multiple DeprecationWarnings)

## Documentation Verification

### Check Migration Guide Exists
```bash
cat MIGRATION_GUIDE.md
```
**Expected:** Comprehensive migration guide with import mapping examples

### Check Deprecation Policy Exists
```bash
cat DEPRECATION_POLICY.md
```
**Expected:** Clear deprecation timeline and policy

### Check Progress Tracker Updated
```bash
cat docs/implementation/RESTRUCTURE_PROGRESS.md | head -20
```
**Expected:** Last updated date reflects completion, phases marked VERIFIED

## Regression Testing (30 minutes)

### Run Full Test Suite (if environment permits)
```bash
.venv/bin/python -m pytest
```
**Note:** May timeout on cold Python 3.9/Intel macOS. Best run on Python 3.12+ or CI.

### Run Specific Test Categories
```bash
# Public imports
.venv/bin/python -m pytest tests/regression/test_public_imports.py

# E2E with fake provider
.venv/bin/python -m pytest tests/test_e2e.py

# Static import analysis
.venv/bin/python -m pytest tests/test_static_imports.py
```

## Common Issues and Solutions

### Issue: Import errors after merge
**Solution:** Ensure you're in a fresh virtual environment with latest dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Issue: Deprecation warnings in tests
**Solution:** These are expected and intentional. Legacy imports should emit warnings.

### Issue: Lint errors on provider code
**Solution:** These are pre-existing in provider implementation and separate from restructure work. Focus on `gptc/` and restructure-specific packages.

## Sign-off Checklist

- [ ] All quick verification tests pass
- [ ] Canonical package structure verified
- [ ] Legacy compatibility shims work with warnings
- [ ] CLI import smoke test passes
- [ ] API identity checks pass
- [ ] Documentation is complete and accurate
- [ ] Progress tracker reflects completion status
- [ ] No breaking changes to public API (only deprecations)

## Post-Merge Actions

1. Update version in `gptc/version.py` if this is a breaking change
2. Update release notes with migration information
3. Announce deprecation timeline to users
4. Monitor for issues with legacy imports
5. Plan removal of shims for version 1.0.0
