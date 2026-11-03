"""Canonical import path for the Copilot provider."""

from __future__ import annotations


def __getattr__(name):
    from gpt_computer.ai import provider as _provider

    return getattr(_provider, name)
