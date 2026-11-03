"""
Config Loader

Provides programmatic loading and reloading of application configuration.
"""

from gpt_computer.infrastructure.config.settings import Settings, get_settings


def load_config() -> Settings:
    """Load application configuration (cached)."""
    return get_settings()


def reload_config() -> Settings:
    """Force-reload application configuration."""
    get_settings.cache_clear()
    return get_settings()


__all__ = ["load_config", "reload_config"]
