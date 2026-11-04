# Deprecation Policy

**Date**: 2026-10-28
**Phase**: Phase 2 - Freeze Public Contract
**Status**: Final

This document defines the deprecation policy for the gpt-computer restructure, including the version schedule, warning behavior, and removal timeline.

---

## Version Schedule

| Version | Status | Changes |
|---------|--------|---------|
| 0.1.1 | Current | Current structure (dual packages) |
| 0.2.x | (optional) | Bug fixes only, no restructure |
| 0.3.0 | Restructure Release | Compatibility shims added, new structure implemented |
| 0.3.x | Deprecation Period | Compatibility shims active, deprecation warnings |
| 0.4.x | Deprecation Period | Compatibility shims active, warnings continue |
| 0.5.x | Deprecation Period | Compatibility shims active, warnings continue |
| 1.0.0 | Removal | Compatibility shims removed, legacy imports/commands break |

**Minimum Deprecation Period**: 12 months (from 0.3.0 to 1.0.0)

---

## Deprecation Policy

### Import Deprecation

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

### CLI Command Deprecation

Legacy CLI commands will emit deprecation warnings to stderr:

```bash
$ gpt-computer my-project
WARNING: The 'gpt-computer' command is deprecated and will be removed in version 1.0.0.
Use 'gptc init my-project' instead. See MIGRATION_GUIDE.md for details.
```

### Warning Behavior

**Python Imports**:
- Use `DeprecationWarning` (standard Python warning type)
- Set `stacklevel=2` to point to user code, not shim code
- Warnings are hidden by default in Python (use `-W` flag to see)

**CLI Commands**:
- Print to stderr before executing command
- Include version number when removal will occur
- Reference migration guide

---

## Enabling Warnings

### For Python Imports

To see deprecation warnings:

```python
import warnings
warnings.simplefilter("always")
```

Or via command line:

```bash
python -W always your_script.py
python -W default::DeprecationWarning your_script.py
```

### For CLI Commands

Warnings are always printed to stderr (no flags needed).

---

## Removal Policy

### Minimum Notice Period

**Minimum**: 12 months from stable release (0.3.0)
**Target**: Version 1.0.0

### Removal Schedule

1. **Announcement**: Deprecation announced in 0.3.0 release notes
2. **Deprecation Period**: 0.3.x → 0.4.x → 0.5.x (minimum 12 months)
3. **Final Warning**: 0.5.x release notes announce removal in 1.0.0
4. **Removal**: 1.0.0 removes compatibility shims

### Removal Process

1. **Update Documentation**:
   - Remove legacy import examples from docs
   - Update all examples to use new structure
   - Update README and guides

2. **Remove Compatibility Shims**:
   - Delete `gptc/` compatibility directory
   - Delete `gpt_computer/core/` compatibility directory
   - Update pyproject.toml to remove legacy entry points

3. **Update pyproject.toml**:
   ```toml
   # Remove legacy entry points
   # gpt-computer = "gpt_computer.applications.cli.main:app"
   # ge = "gpt_computer.applications.cli.main:app"
   # gptc-mcp = "gptc.mcp.server:main"
   # gptc-tray = "gptc.tray:_tray_main"
   # bench = "gpt_computer.benchmark.__main__:app"
   ```

4. **Release 1.0.0**:
   - Breaking release
   - All legacy imports/commands break
   - Only new structure supported

---

## Communication

### Release Notes

Each release during deprecation period will include:

```
## Deprecation Notices

The following imports/commands are deprecated and will be removed in version 1.0.0:

- `from gptc import Client` → Use `from gpt_computer.ai.client import Client`
- `gpt-computer` command → Use `gptc init` or `gptc improve`
- `gptc-mcp` command → Use `gptc mcp`

See MIGRATION_GUIDE.md for migration instructions.
```

### Documentation Updates

1. **README.md**:
   - Add deprecation notice section
   - Link to migration guide
   - Update all examples to use new structure

2. **API Documentation**:
   - Mark deprecated APIs with "Deprecated since 0.3.0"
   - Provide migration examples
   - Link to migration guide

3. **Migration Guide**:
   - Create comprehensive MIGRATION_GUIDE.md
   - Include before/after examples
   - Include troubleshooting section
   - Include timeline

---

## Testing Deprecation

### Test Coverage

All compatibility shims must have tests verifying:

1. **Import Works**: Old import successfully imports
2. **Warning Emitted**: Deprecation warning is emitted
3. **API Identity**: Imported object is same as new import
4. **Functionality**: Imported object works correctly

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

### CLI Tests

All legacy CLI commands must have tests verifying:

1. **Command Executes**: Command runs successfully
2. **Warning Emitted**: Deprecation warning printed to stderr
3. **Functionality Preserved**: Command works as expected

---

## Exceptions

### Emergency Removal

In extreme cases (security vulnerabilities, critical bugs), compatibility shims may be removed earlier than 1.0.0.

**Process**:
1. Document security/critical issue
2. Announce in release notes with 3-month minimum notice
3. Provide alternative migration path
4. Remove after notice period

### Extended Deprecation

If significant user feedback indicates need for longer deprecation period, deprecation may be extended beyond 1.0.0.

**Process**:
1. Gather user feedback via issues and surveys
2. Assess impact of breaking change
3. Propose extension in RFC
4. Get maintainer approval
5. Update version schedule in DEPRECATION_POLICY.md

---

## References

- **PUBLIC_IMPORTS.md**: List of all guaranteed public imports
- **CLI_ENTRY_POINTS.md**: List of all guaranteed CLI commands
- **MIGRATION_GUIDE.md**: User-facing migration guide (to be created)
- **RESTRUCTURE_PLAN.md**: Overall restructure plan

---

**Last Updated**: 2026-10-28
**Phase**: Phase 2 - Freeze Public Contract
**Status**: Final
