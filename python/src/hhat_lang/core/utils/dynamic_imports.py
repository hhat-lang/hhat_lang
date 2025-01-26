"""
To handle the dynamic imports that happen throughout the core code, for instance
on the `core.cast_system.base.Cast` class that needs to import a `BaseLowLevelAPI`
child from an implemented dialects on its `__call__` method.
"""

from __future__ import annotations

from types import ModuleType
from typing import Any

from importlib import import_module

from hhat_lang.core.lang_settings.config_builder import ConfigBuilder


def import_q_lowlevel_backend_module(backend_name: str, version: str) -> ModuleType:
    """
    For now, only accounts for backends inside the H-hat repository.

    TODO: generalize it
    """

    mod = import_module(f"hhat_lang.quantum_lowlevel.{backend_name}.backend.{version}")
    return mod


def import_q_lowlevel_lang_module(
    backend_name: str,
    backend_version: str,
    lowlevel_lang: str,
    lang_version: str
) -> ModuleType:
    """
    For now, only accounts for quantum low-level languages inside the H-hat repository.

    TODO: generalize it
    """

    mod = import_module(
        f"hhat_lang.quantum_lowlevel.{backend_name}.frontend.{lowlevel_lang}.{lang_version}"
    )
    return mod


def import_lowlevel_modules(config: ConfigBuilder) -> tuple[ModuleType, ModuleType]:
    return (
        import_q_lowlevel_backend_module(config.backend.short_name, config.backend.version),
        import_q_lowlevel_lang_module(
            config.backend.short_name,
            config.backend.version,
            config.ql3.short_name,
            config.ql3.version
        ),
    )


def import_dialect_module(dialect_name: str, _dialect_version: str | None = None) -> ModuleType:
    """
    For now, only accounts for dialects inside the H-hat repository and their latest version.

    Args:
        dialect_name (str): dialect (short) name
        _dialect_version (str, optional): dialect version. Defaults to `None`.

    Returns:
        dialect module
    """
    mod = import_module(f"hhat_lang.dialects.{dialect_name}")
    return mod
