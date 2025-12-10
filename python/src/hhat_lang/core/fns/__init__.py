from __future__ import annotations

from pathlib import Path


BUILTIN_CORE_MODULE_ROOT_PATH = Path("src/.hat_core/")
"""
Built-in core module root path is to be used for essential functions,
such as ``print``, ``if``, ``match``, ``cast``, etc.

These functions shall not be imported directly by the user; it must be 
internally handled by the dialect compiler. 
"""

BUILTIN_STD_MODULE_ROOT_PATH = Path("src/.hat_std/")
"""
Built-in standard module root path is to be used for standard libraries,
such as ``math`` (with modules such as ``arithmetic``, ``trigonometry``, 
``linear-algebra``, etc.), ``io`` (with modules such as ``socket``, etc.), etc.

These functions must be explicitly imported by the user. 
"""
