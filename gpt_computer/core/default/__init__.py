"""
Legacy ``gpt_computer.core.default`` compatibility package.

.. deprecated:: 0.3.0
    Import from the new domain packages instead:

    * ``gpt_computer.agent.memory`` for ``DiskMemory``
    * ``gpt_computer.execution.local`` for ``DiskExecutionEnv``
    * ``gpt_computer.agent.default`` for ``SimpleAgent``

The modules in this package remain as thin compatibility shims until version
1.0.0.
"""

import importlib
import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.default' is deprecated and will be removed in version 1.0.0. "
    "Use 'gpt_computer.agent.memory', 'gpt_computer.execution.local', or "
    "'gpt_computer.agent.default' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

_EXPORTS = {
    "DiskExecutionEnv": ("gpt_computer.execution.local", "DiskExecutionEnv"),
    "DiskMemory": ("gpt_computer.agent.memory.disk", "DiskMemory"),
    "SimpleAgent": (
        "gpt_computer.agent.default.simple_agent",
        "SimpleAgent",
    ),
    "default_config_agent": (
        "gpt_computer.agent.default.simple_agent",
        "default_config_agent",
    ),
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    export = _EXPORTS.get(name)
    if export is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute_name = export
    module = importlib.import_module(module_name)
    return getattr(module, attribute_name)
