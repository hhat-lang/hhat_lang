from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterator, Optional, List, Callable

from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    FunctionNotFoundError,
    InvalidPathError,
    TypesFunctionWarning
)
from hhat_lang.core.code.ast import AST
from hhat_lang.dialects.heather.code.ast import Id, CompositeId, Body, FnDef, FnArgs

def is_valid_path_component(component: str, allow_hat_types: bool = False) -> bool:
    """
    Validate a path component (file or directory name).
    
    Args:
        component: The path component to validate
        allow_hat_types: Whether to allow hat_types directory
    """
    # Can't start with number
    if re.match(r"^\d", component):
        return False
        
    # Special case for hat_types
    if allow_hat_types and component == "hat_types":
        return True
        
    # Don't allow hat_ prefix otherwise
    if component.startswith("hat_"):
        return False
        
    # Only allow alphanumeric, underscore and hyphen
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", component))

def locate_function_source(
    function_name: str | Symbol | CompositeSymbol,
    project_root: Path,
) -> tuple[Path, ErrorHandler] | Path | ErrorHandler:
    """
    Locate the source file containing the function definition.
    
    Args:
        function_name: Name of the function to find
        project_root: Root directory of the H-hat project
        
    Returns:
        Either the Path to the file containing the function, or an error
    """
    # Convert function name to string if needed
    if isinstance(function_name, Symbol):
        function_name = function_name.value
    elif isinstance(function_name, CompositeSymbol):
        function_name = ".".join(str(sym.value) for sym in function_name.value)
    
    # Split function name into components for nested lookup
    components = function_name.split(".")
    
    # Validate path components
    for component in components:
        if re.match(r"^\d", component):
            return InvalidPathError(component, "Path component cannot start with a number")
            
    # Special handling for hat_types
    if components[0] == "hat_types":
        if len(components) < 2:
            return InvalidPathError(function_name, "Invalid hat_types path")
            
        # Build path in src/hat_types
        file_path = project_root / "src" / "hat_types"
        for component in components[1:-1]:
            file_path = file_path / component
        file_path = file_path / f"{components[-1]}.hat"
        
        if file_path.exists():
            return file_path, TypesFunctionWarning(function_name)
        
    # Check for invalid hat_ prefix
    if any(c.startswith("hat_") and c != "hat_types" for c in components):
        return InvalidPathError(function_name, "Invalid hat_ prefix")
    
    # First check main.hat in project root if it's a simple function name
    if len(components) == 1:
        main_hat = project_root / "main.hat"
        if main_hat.exists():
            return main_hat
    
    # Build path in src directory
    src_dir = project_root / "src"
    if not src_dir.exists():
        return InvalidPathError(str(src_dir), "src directory does not exist")
        
    # Try nested directory structure
    file_path = src_dir
    for component in components[:-1]:
        file_path = file_path / component
        if not file_path.exists():
            return FunctionNotFoundError(function_name)
            
    file_path = file_path / f"{components[-1]}.hat"
    
    if file_path.exists():
        return file_path
        
    return FunctionNotFoundError(function_name)

def get_function_definitions(
    source_file: Path,
    function_name: str | Symbol | CompositeSymbol,
    parser_fn: Callable[[AST], List[dict]]
) -> List[dict]:
    """
    Extract all function definitions matching the given name from a source file.
    
    Args:
        source_file: Path to the source file
        function_name: Name of the function to find
        parser_fn: Dialect-specific parser function that converts AST to function definitions
        
    Returns:
        List of function definitions
    """
    try:
        with open(source_file, "r") as f:
            content = f.read()
            # Let the dialect-specific parser handle the content
            return parser_fn(content)
    except IOError:
        return []

def parse_function_definition(content: str, parser_fn: Callable[[str], List[dict]]) -> List[dict]:
    """
    Parse function definitions from source code content.
    
    Args:
        content: The source code content
        parser_fn: Dialect-specific parser function that converts source code to function definitions
        
    Returns:
        List of function definitions
    """
    return parser_fn(content) 