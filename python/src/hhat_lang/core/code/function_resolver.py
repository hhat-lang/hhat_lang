from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterator, Optional, List

from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.error_handlers.errors import ErrorHandler

class FunctionNotFoundError(ErrorHandler):
    def __init__(self, function_name: str):
        super().__init__("FUNCTION_NOT_FOUND")
        self._function_name = function_name

    def __call__(self) -> str:
        return f"Function '{self._function_name}' not found"

class InvalidPathError(ErrorHandler):
    def __init__(self, path: str, reason: str):
        super().__init__("INVALID_PATH")
        self._path = path
        self._reason = reason

    def __call__(self) -> str:
        return f"Invalid path '{self._path}': {self._reason}"

class TypesFunctionWarning(ErrorHandler):
    def __init__(self, function_name: str):
        super().__init__("TYPES_FUNCTION_WARNING")
        self._function_name = function_name

    def __call__(self) -> str:
        return f"Warning: Function '{self._function_name}' is in hat_types directory. It should only be used by types."

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
) -> tuple[Path, ErrorHandler] | Path:
    """
    Locate the source file containing the function definition.
    
    Args:
        function_name: Name of the function to find
        project_root: Root directory of the H-hat project
        
    Returns:
        Either the Path to the file containing the function, or an error
    """
    # Convert function name to string if needed
    if isinstance(function_name, (Symbol, CompositeSymbol)):
        function_name = str(function_name)
    
    # First check main.hat in project root
    main_hat = project_root / "main.hat"
    if main_hat.exists():
        return main_hat
        
    # Split function name into components for nested lookup
    components = function_name.split(".")
    
    # Build potential file paths
    paths_to_check = []
    
    # Check direct file in src/
    src_dir = project_root / "src"
    if not src_dir.exists():
        return InvalidPathError(str(src_dir), "src directory does not exist")
        
    # Track if we're in hat_types directory
    in_hat_types = False
    
    # Validate all path components
    for i, component in enumerate(components[:-1]):
        # Special handling for hat_types directory
        if i == 0 and component == "hat_types":
            in_hat_types = True
            if not is_valid_path_component(component, allow_hat_types=True):
                return InvalidPathError(
                    component,
                    "Invalid directory name - must start with letter and contain only alphanumeric, underscore or hyphen"
                )
        else:
            if not is_valid_path_component(component):
                return InvalidPathError(
                    component,
                    "Invalid directory name - must start with letter and contain only alphanumeric, underscore or hyphen"
                )
            
    # Build file path variations
    base_path = src_dir
    for i in range(len(components)):
        # Get module path up to this component
        module_path = components[:i+1]
        
        # Try as direct .hat file
        file_path = base_path / f"{'.'.join(module_path)}.hat"
        paths_to_check.append((file_path, in_hat_types))
        
        # Try as directory with .hat file
        dir_path = base_path.joinpath(*module_path[:-1])
        if dir_path.exists() and dir_path.is_dir():
            file_path = dir_path / f"{module_path[-1]}.hat"
            paths_to_check.append((file_path, in_hat_types))
    
    # Check all potential paths
    for path, is_types_path in paths_to_check:
        if path.exists():
            if is_types_path:
                # Return both the path and a warning
                return path, TypesFunctionWarning(function_name)
            return path
            
    return FunctionNotFoundError(function_name)

def parse_function_definition(content: str) -> List[dict]:
    """Parse function definitions from .hat file content."""
    # This is a simplified parser - in reality, you'd want to use a proper lexer/parser
    definitions = []
    lines = content.split('\n')
    current_fn = None
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('//'):
            continue
            
        # Check for function start
        if line.startswith('fn '):
            # Basic function parsing - in reality would need proper parsing
            fn_match = re.match(r'fn\s+(\w+)\s*\((.*?)\)\s*->\s*(\w+)\s*{', line)
            if fn_match:
                current_fn = {
                    'name': fn_match.group(1),
                    'type': fn_match.group(3),
                    'args': [arg.strip() for arg in fn_match.group(2).split(',') if arg.strip()],
                    'body': []
                }
        
        # Check for function end
        elif line == '}' and current_fn is not None:
            definitions.append(current_fn)
            current_fn = None
            
        # Add line to current function body
        elif current_fn is not None:
            current_fn['body'].append(line)
            
    return definitions

def get_function_definitions(
    source_file: Path,
    function_name: str | Symbol | CompositeSymbol
) -> Iterator[dict] | ErrorHandler:
    """
    Extract all function definitions matching the given name from a source file.
    
    Args:
        source_file: Path to the source file
        function_name: Name of the function to find
        
    Returns:
        Iterator of function definitions or an error
    """
    # Convert function name to string if needed
    if isinstance(function_name, (Symbol, CompositeSymbol)):
        function_name = str(function_name)
    
    # Get just the final component of the function name
    function_name = function_name.split(".")[-1]
    
    try:
        with open(source_file, "r") as f:
            content = f.read()
            
        # Parse all function definitions
        definitions = parse_function_definition(content)
        
        # Yield matching functions (supports overloading)
        for definition in definitions:
            if definition['name'] == function_name:
                yield definition
            
    except Exception as e:
        return InvalidPathError(str(source_file), f"Failed to read file: {str(e)}") 