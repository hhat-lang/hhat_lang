"""To handle the `imports` part, for both types and functions"""

from __future__ import annotations

import os
from functools import reduce
from operator import iconcat
from pathlib import Path
from typing import Any, Iterator, List, Optional, Tuple

from hhat_lang.core.code.ast import AST
from hhat_lang.core.code.function_resolver import locate_function_source, get_function_definitions
from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.dialects.heather.code.ast import (
    CompositeId,
    CompositeIdWithClosure,
    FnDef,
    Id,
    Imports,
)


def parse_types(code: Any) -> Any:
    pass


def parse_types_compositeid(code: CompositeId) -> Any:
    # get the type path from the code
    type_path = Path(*reduce(iconcat, code.value, ()))
    # join the type path with its full path from the project path
    type_path = Path(".").resolve() / "hhat_types" / type_path
    # add .hat for the type file name (which should be the last item in the tuple)
    file_name = type_path.name + ".hat"
    full_path = type_path.parent / file_name

    if full_path.exists():
        data = open(full_path, "r").read()


def parse_types_compositeidwithclosure(code: CompositeIdWithClosure) -> Any:
    pass


def parse_fn_import(
    fn_import: Id | CompositeId | CompositeIdWithClosure,
    project_root: Path
) -> tuple[List[FnDef], List[ErrorHandler]]:
    """
    Parse a single function import.
    
    Args:
        fn_import: The function import AST node
        project_root: Root directory of the H-hat project
        
    Returns:
        Tuple of (function definitions, errors)
    """
    # Extract function name based on node type
    if isinstance(fn_import, Id):
        function_name = fn_import._value[0]
    elif isinstance(fn_import, CompositeId):
        function_name = ".".join(name._value[0] for name in fn_import._value)
    else:  # CompositeIdWithClosure
        name = fn_import._value[0]  # Get the root name
        if isinstance(name, Id):
            function_name = name._value[0]
        else:  # CompositeId
            function_name = ".".join(n._value[0] for n in name._value)
        # Add the closure values
        for value in fn_import._value[1]:
            if isinstance(value, Id):
                function_name += f".{value._value[0]}"
            else:  # CompositeId
                function_name += "." + ".".join(n._value[0] for n in value._value)
    
    # Find the source file
    source_location = locate_function_source(function_name, project_root)
    if isinstance(source_location, ErrorHandler):
        return [], [source_location]
    elif isinstance(source_location, tuple):
        source_location = source_location[0]  # Extract path from (path, warning) tuple
        
    # Get function definitions
    definitions = get_function_definitions(source_location, function_name)
    
    # Convert definitions to FnDef AST nodes
    fn_defs = []
    errors = []
    
    try:
        for definition in definitions:
            fn_def = FnDef(
                fn_name=Id(definition["name"]),
                fn_type=definition["type"],
                args=FnArgs(),  # Empty args for now
                body=Body()  # Empty body for now
            )
            fn_defs.append(fn_def)
    except Exception as e:
        errors.append(ErrorHandler(f"Failed to create FnDef: {str(e)}"))
            
    return fn_defs, errors


def parse_fns(code: Imports, project_root: Optional[Path] = None) -> tuple[List[FnDef], List[ErrorHandler]]:
    """
    Parse function imports and return function definitions.
    
    Args:
        code: The imports AST node
        project_root: Root directory of the H-hat project (optional)
        
    Returns:
        Tuple of (function definitions, errors)
    """
    if project_root is None:
        project_root = Path.cwd()
        
    all_fn_defs = []
    all_errors = []
    
    # Handle each function import
    type_imports, fn_imports = code._value
    for fn_import in fn_imports:
        for fn in fn_import._value:
            fn_defs, errors = parse_fn_import(fn, project_root)
            all_fn_defs.extend(fn_defs)
            all_errors.extend(errors)
            
            # Stop on first error
            if errors:
                break
        
    return all_fn_defs, all_errors


def parse_imports(code: Imports) -> Any:
    pass
