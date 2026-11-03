# Provider Config vs Global Config Overlap

**Date**: 2026-10-28
**Phase**: Phase 1 - Architecture and Security Rules
**Status**: Resolved - Documented in RESPONSIBILITY_RESOLUTION.md

This document specifically addresses the overlap between provider-specific configuration and global application configuration.

---

## Current State

### Provider Config

**Location**: `gptc/providers/config_provider.py`
**Purpose**: Provider-specific configuration handling
**Contents**: `ConfigProvider` class for provider settings

### Global Config

**Location**: `gptc/config.py`
**Purpose**: Global gptc configuration
**Contents**: 
- `AppConfig` class with provider settings mixed in
- Global constants (paths, URLs, ports)
- Configuration directory management

### Overlap Issues

1. **Mixed Concerns**: `gptc/config.py` contains both global settings and provider-specific settings
2. **No Clear Separation**: Unclear which config is provider-specific vs global
3. **Duplication**: Some settings may be duplicated across modules
4. **Precedence Unclear**: No clear rule for which config takes precedence

---

## Resolution

### Decision (from RESTRUCTURE_PLAN.md)

**Provider-specific settings**: `ai/providers/config.py`
**Global application configuration**: `infrastructure/config/`

### New Structure

```
ai/providers/config.py      # Provider-specific configuration only
├── ProviderConfig class
├── API keys per provider
├── Provider-specific endpoints
└── Provider-specific settings

infrastructure/config/       # Global application configuration
├── settings.py             # Global settings with precedence
├── loader.py               # Config loader (env, file, CLI, defaults)
└── project_config.py       # Project-specific configuration
```

### Separation of Concerns

**Provider Config** (`ai/providers/config.py`):
- Provider API keys
- Provider-specific endpoints
- Provider-specific timeouts
- Provider-specific retry logic
- Provider-specific models

**Global Config** (`infrastructure/config/settings.py`):
- Default model selection
- Default provider selection
- Global timeouts
- Global paths
- Observability settings (verbose, debug)
- API keys (global fallbacks)

---

## Migration Plan

### Phase 2 (Infrastructure Migration)

**Steps**:

1. **Create `infrastructure/config/settings.py`**:
   - Move global settings from `gptc/config.py`
   - Implement precedence rules
   - Use Pydantic Settings

2. **Create `infrastructure/config/loader.py`**:
   - Implement config loading from multiple sources
   - Handle precedence (CLI > env > project > user > defaults)

3. **Move Provider Config**:
   - Keep provider-specific config in `ai/providers/config.py`
   - Remove global settings from provider config
   - Ensure provider config only deals with provider concerns

4. **Update `gptc/config.py`**:
   - Remove global settings (moved to infrastructure)
   - Keep only gptc-specific constants (paths, URLs)
   - Add deprecation warnings for moved settings

5. **Update All Callers**:
   - Update imports from `gptc.config` to `infrastructure.config.settings`
   - Update imports from `gptc.providers.config_provider` to `ai.providers.config`
   - Test all updates

6. **Add Compatibility Shims**:
   ```python
   # gptc/config.py (compatibility shim)
   import warnings
   from infrastructure.config.settings import Settings as _Settings
   
   warnings.warn(
       "Importing from gptc.config is deprecated. "
       "Use infrastructure.config.settings instead.",
       DeprecationWarning,
       stacklevel=2
   )
   
   # Re-export for compatibility
   AppConfig = _Settings
   get_settings = _Settings
   ```

---

## Configuration Precedence

### Order (Highest to Lowest)

1. **CLI command-line arguments**
2. **Environment variables**
3. **Project-specific config file** (`.gptc.toml` or `.gptc.yaml`)
4. **User config file** (`~/.config/gptc/config.toml`)
5. **Default values in code**

### Implementation

```python
# infrastructure/config/loader.py
class ConfigLoader:
    def load(self) -> Settings:
        # 1. Start with defaults
        config = Settings.from_defaults()
        
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

---

## Provider Config API

### New Structure

```python
# ai/providers/config.py
class ProviderConfig:
    """Provider-specific configuration."""
    
    def __init__(
        self,
        provider_name: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: int = 600,
        max_retries: int = 3,
    ):
        self.provider_name = provider_name
        self.api_key = api_key
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_retries = max_retries
    
    @classmethod
    def from_env(cls, provider_name: str) -> "ProviderConfig":
        """Load provider config from environment variables."""
        env_prefix = f"{provider_name.upper()}_"
        return cls(
            provider_name=provider_name,
            api_key=os.environ.get(f"{env_prefix}API_KEY"),
            endpoint=os.environ.get(f"{env_prefix}ENDPOINT"),
            timeout=int(os.environ.get(f"{env_prefix}TIMEOUT", 600)),
            max_retries=int(os.environ.get(f"{env_prefix}MAX_RETRIES", 3)),
        )
```

---

## Global Config API

### New Structure

```python
# infrastructure/config/settings.py
class Settings(BaseSettings):
    """Global application settings."""
    
    # Model Defaults
    model_name: str = "gpt-4o"
    temperature: float = 0.1
    default_provider: str = "openai"
    
    # Paths
    config_dir: Path = Field(default_factory=get_default_config_dir)
    workspace_dir: Path = Field(default_factory=get_default_workspace_dir)
    
    # Observability
    verbose: bool = False
    debug: bool = False
    
    # Global API Keys (fallbacks)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GPTC",
        extra="ignore"
    )
```

---

## Status

**Current**: Provider config and global config are mixed in `gptc/config.py`
**Target**: Separated into `ai/providers/config.py` and `infrastructure/config/`
**Migration Phase**: Phase 2 (Infrastructure)
**Status**: Resolved - Documented in RESPONSIBILITY_RESOLUTION.md

---

## References

- **RESTRUCTURE_PLAN.md**: Decision 3 - Responsibility Ownership
- **RESPONSIBILITY_RESOLUTION.md**: Detailed configuration resolution plan
- **DEPENDENCY_RULES.md**: Architectural layer rules

---

**Last Updated**: 2026-10-28
**Phase**: Phase 1 - Architecture and Security Rules
