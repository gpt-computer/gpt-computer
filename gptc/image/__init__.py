"""Compatibility shim for the legacy ``gptc.image`` package."""

import warnings

warnings.warn(
    "Importing from 'gptc.image' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.image import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

import sys
import types

import gpt_computer.infrastructure.image as _new

__path__ = list(_new.__path__)

from gpt_computer.infrastructure.image import *  # noqa: E402,F401,F403


def __getattr__(name):
    return getattr(_new, name)


class LazyImageModule(types.ModuleType):
    def __getattribute__(self, name):
        if name.startswith("__"):
            return super().__getattribute__(name)
        try:
            return __getattr__(name)
        except AttributeError:
            pass
        return super().__getattribute__(name)


sys.modules[__name__].__class__ = LazyImageModule
