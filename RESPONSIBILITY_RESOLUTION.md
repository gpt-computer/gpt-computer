# Responsibility Resolution

**Date**: 2026-10-28
**Phase**: Phase 1 - Architecture and Security Rules
**Status**: Draft - Current State Analysis

This document identifies duplicate responsibilities across the codebase and proposes how to resolve them during the restructure according to the architectural decisions in RESTRUCTURE_PLAN.md.

---

## Overview

The current codebase has duplicate responsibilities for:
1. **File operations** - Multiple modules doing file I/O
2. **Git operations** - Git wrappers in different places
3. **Configuration** - Multiple config systems with overlapping concerns

These duplicates create maintenance overhead and unclear ownership. The restructure will consolidate these into single owners in the `infrastructure/` layer.

---

## File Operations

### Current State

| Location | Purpose | Key Functions |
|----------|---------|--------------|
| `gptc/tools/files.py` | File reading, downloading, caching for AI context | `stream_read_files()`, `download_urls()`, `read_bucket()` |
| `gptc/files.py` | File utilities (referenced but not analyzed) | Unknown |
| `gpt_computer/core/git.py` | Git-related file operations (imports FilesDict) | Git operations on files |
| `gpt_computer/core/files_dict.py` | File dictionary abstraction for code generation | `FilesDict` class |

### Issues

1. **Scattered File I/O**: File operations are spread across multiple modules
2. **Inconsistent Abstractions**: Some use `FilesDict`, others use direct `Path` operations
3. **No Central Owner**: No single module responsible for file operations
4. **Context-Specific Code**: `gptc/tools/files.py` is designed for AI context ingestion, not general file operations

### Proposed Resolution

**Owner**: `infrastructure/files/operations.py`

**New Structure**:
```
infrastructure/files/
├── operations.py           # Core file operations (read, write, delete, list)
├── security.py             # Path validation, symlink resolution, containment checks
└── paths.py                # Path utilities (join, resolve, normalize)
```

**Migration Strategy**:

1. **Create `infrastructure/files/operations.py`**:
   - Extract common file operations from existing modules
   - Implement secure file operations with path validation
   - Provide both sync and async variants

2. **Migrate `gpt_computer/core/files_dict.py`**:
   - Keep `FilesDict` as a higher-level abstraction
   - Have `FilesDict` use `infrastructure/files/operations.py` internally
   - Move to `agent/tools/` or keep in core depending on usage

3. **Migrate `gptc/tools/files.py`**:
   - This is context-specific code for AI ingestion
   - Move to `agent/tools/context_ingestion.py` or similar
   - Keep as a specialized tool, not general file operations

4. **Update All Callers**:
   - Replace direct file I/O with calls to `infrastructure/files/operations.py`
   - Ensure security checks are applied consistently

**API Design**:
```python
# infrastructure/files/operations.py
class FileOperations:
    @staticmethod
    def read(path: Path, allowed_dirs: List[Path]) -> str:
        """Read file with security checks."""
        pass

    @staticmethod
    def write(path: Path, content: str, allowed_dirs: List[Path]) -> None:
        """Write file with security checks."""
        pass

    @staticmethod
    def delete(path: Path, allowed_dirs: List[Path]) -> None:
        """Delete file with security checks."""
        pass

    @staticmethod
    def list(dir: Path, allowed_dirs: List[Path]) -> List[Path]:
        """List directory with security checks."""
        pass
```

---

## Git Operations

### Current State

| Location | Purpose | Key Functions |
|----------|---------|--------------|
| `gpt_computer/core/git.py` | Git command wrappers for staging, diffing | `stage_files()`, `filter_files_with_uncommitted_changes()`, `init_git_repo()` |

### Issues

1. **Single Location (Good)**: Git operations are already centralized in one module
2. **Wrong Layer**: Currently in `core/`, should be in `infrastructure/`
3. **Limited Functionality**: Only covers basic operations needed for code generation
4. **No Async Support**: All operations are synchronous

### Proposed Resolution

**Owner**: `infrastructure/git/operations.py`

**New Structure**:
```
infrastructure/git/
├── operations.py           # Git command wrappers (sync)
├── async_operations.py     # Async git operations (future)
└── repository.py           # Repository abstraction (status, history, branches)
```

**Migration Strategy**:

1. **Move `gpt_computer/core/git.py`**:
   - Move to `infrastructure/git/operations.py`
   - Keep existing function signatures for compatibility
   - Add type hints and error handling

2. **Add Async Support** (Optional):
   - Create `infrastructure/git/async_operations.py`
   - Use `asyncio.subprocess` for async git operations
   - Useful for concurrent operations

3. **Update Imports**:
   - Update all imports from `gpt_computer.core.git` to `infrastructure.git.operations`
   - Add compatibility shim in `gpt_computer/core/git.py` during deprecation period

**API Design**:
```python
# infrastructure/git/operations.py
class GitOperations:
    @staticmethod
    def is_installed() -> bool:
        """Check if git is installed."""
        pass

    @staticmethod
    def is_repo(path: Path) -> bool:
        """Check if path is a git repository."""
        pass

    @staticmethod
    def init(path: Path) -> None:
        """Initialize git repository."""
        pass

    @staticmethod
    def stage(path: Path, files: List[str]) -> None:
        """Stage files for commit."""
        pass

    @staticmethod
    def get_uncommitted(path: Path) -> List[str]:
        """Get list of uncommitted files."""
        pass

    @staticmethod
    def diff(path: Path, files: List[str] = None) -> str:
        """Get git diff."""
        pass
```

---

## Configuration

### Current State

| Location | Purpose | Type |
|----------|---------|------|
| `gpt_computer/core/config.py` | Application settings (API keys, model defaults) | Pydantic Settings |
| `gptc/config.py` | gptc-specific config (paths, constants, AppConfig) | Simple class + constants |
| `gptc/providers/config_provider.py` | Provider-specific configuration handling | ConfigProvider class |
| `gpt_computer/core/project_config.py` | Project-specific configuration | Pydantic models |

### Issues

1. **Multiple Config Systems**: Three different config systems with overlapping concerns
2. **No Clear Precedence**: Unclear which config takes precedence when values conflict
3. **gptc vs gpt_computer**: Separate config systems for the two packages
4. **Provider Config Mixed**: Provider-specific config mixed with global config in `gptc/config.py`

### Proposed Resolution

**Owner**: `infrastructure/config/`

**New Structure**:
```
infrastructure/config/
├── settings.py             # Global application settings with precedence
├── loader.py               # Config loader (env, file, CLI, defaults)
└── project_config.py       # Project-specific configuration (moved from core)
```

**Provider Config**:
```
ai/providers/config.py      # Provider-specific configuration only
```

**Migration Strategy**:

1. **Create `infrastructure/config/settings.py`**:
   - Consolidate global application settings
   - Implement precedence rules (CLI > env > project file > user file > defaults)
   - Use Pydantic Settings for type safety

2. **Create `infrastructure/config/loader.py`**:
   - Implement config loading from multiple sources
   - Handle precedence rules
   - Support TOML, YAML, and environment variables

3. **Move `gpt_computer/core/project_config.py`**:
   - Move to `infrastructure/config/project_config.py`
   - Keep project-specific configuration separate from global settings

4. **Separate Provider Config**:
   - Keep only provider-specific settings in `ai/providers/config.py`
   - Move global config from `gptc/config.py` to `infrastructure/config/`
   - Remove duplicate constants

5. **Deprecate Old Config**:
   - Add deprecation warnings to `gptc/config.py`
   - Add deprecation warnings to `gpt_computer/core/config.py`
   - Provide migration guide

**Precedence Rules**:
```python
# infrastructure/config/loader.py
class ConfigLoader:
    def load(self) -> Config:
        # 1. Start with defaults
        config = Config.from_defaults()

        # 2. Load user config
        user_config = self.load_user_config()
        config = config.merge(user_config)

        # 3. Load project config
        project_config = self.load_project_config()
        config = config.merge(project_config)

        # 4. Load environment variables
        env_config = self.load_env_vars()
        config = config.merge(env_config)

        # 5. Apply CLI overrides (done separately)
        return config
```

**API Design**:
```python
# infrastructure/config/settings.py
class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # Model Defaults
    model_name: str = "gpt-4o"
    temperature: float = 0.1

    # Paths
    config_dir: Path = Field(default_factory=get_default_config_dir)
    workspace_dir: Path = Field(default_factory=get_default_workspace_dir)

    # Observability
    verbose: bool = False
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GPTC",
        extra="ignore"
    )

# infrastructure/config/loader.py
def get_settings() -> Settings:
    """Get settings with full precedence applied."""
    loader = ConfigLoader()
    return loader.load()
```

---

## Migration Priority

### High Priority (Phase 2)

1. **Git Operations**:
   - Simple to move (single module)
   - Clear ownership
   - Low risk

2. **Configuration**:
   - Critical for restructure
   - Must be resolved before other modules
   - Affects many parts of codebase

### Medium Priority (Phase 3)

3. **File Operations**:
   - More complex (multiple modules)
   - Requires careful security considerations
   - Higher risk

---

## Compatibility Strategy

### During Migration

1. **Keep Old Modules with Deprecation Warnings**:
   ```python
   # gpt_computer/core/git.py (compatibility shim)
   import warnings
   from infrastructure.git.operations import GitOperations

   warnings.warn(
       "Importing from gpt_computer.core.git is deprecated. "
       "Use infrastructure.git.operations instead.",
       DeprecationWarning,
       stacklevel=2
   )

   # Re-export for compatibility
   stage_files = GitOperations.stage
   is_git_repo = GitOperations.is_repo
   # ...
   ```

2. **Gradual Migration**:
   - Migrate one module at a time
   - Test after each migration
   - Update imports incrementally

3. **Test Coverage**:
   - Ensure all old imports still work with warnings
   - Test new imports work correctly
   - Verify no functionality is lost

### Post-Migration

1. **Remove Compatibility Shims**:
   - After deprecation period (12 months)
   - Remove old modules
   - Update all remaining imports

2. **Documentation**:
   - Update all documentation to use new imports
   - Update examples
   - Update README

---

## Testing

### Unit Tests

For each migrated module:

1. **Test Old API**:
   - Ensure deprecated imports still work
   - Verify deprecation warnings are emitted
   - Test functionality is preserved

2. **Test New API**:
   - Test new imports work correctly
   - Verify new features (security, async, etc.)
   - Test error handling

3. **Integration Tests**:
   - Test migrated modules work with other code
   - Test end-to-end functionality
   - Test with real-world scenarios (Discord bot, etc.)

### Regression Tests

Run full test suite after each migration:
- Ensure no new test failures
- Verify existing tests still pass
- Check for performance regressions

---

## Dependencies Between Migrations

1. **Configuration First**:
   - Configuration affects almost everything
   - Must be migrated before other modules
   - Other modules depend on config

2. **Git Operations Second**:
   - Relatively independent
   - Can be migrated in parallel with config
   - Low risk

3. **File Operations Last**:
   - Most complex
   - Depends on configuration (paths, etc.)
   - Highest risk

---

## References

- **RESTRUCTURE_PLAN.md**: Decision 3 - Responsibility Ownership
- **DEPENDENCY_RULES.md**: Architectural layer rules
- **infrastructure/** layer: Target location for all migrated modules

---

**Last Updated**: 2026-10-28
**Phase**: Phase 1 - Architecture and Security Rules
**Status**: Draft - Current State Analysis
