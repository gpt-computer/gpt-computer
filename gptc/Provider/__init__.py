"""Compatibility shim for the legacy ``gptc.Provider`` package."""

import warnings

warnings.warn(
    "Importing from 'gptc.Provider' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.provider import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

import sys  # noqa: E402
import types  # noqa: E402

import gpt_computer.ai.provider as _new  # noqa: E402

# Delegate submodule resolution to the migrated package.
__path__ = list(_new.__path__)


# Delegate dynamic provider access.
def __getattr__(name):
    return _new.__getattr__(name)


class LazyProviderModule(types.ModuleType):
    def __getattribute__(self, name):
        if name.startswith("__"):
            return super().__getattribute__(name)
        try:
            return __getattr__(name)
        except AttributeError:
            pass
        return super().__getattribute__(name)


sys.modules[__name__].__class__ = LazyProviderModule
