"""To handle the `imports` part, for both types and functions"""

from __future__ import annotations

import os
from functools import reduce
from operator import iconcat
from pathlib import Path
from typing import Any, Iterator, List, Optional, Tuple, Dict

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
    FnArgs,
    Body,
    FnImport
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
    try:
        # Handle different node types
        if isinstance(fn_import, Id):
            # Simple function name
            function_name = fn_import._value[0]
            
        elif isinstance(fn_import, CompositeId):
            # CompositeId contains a tuple of Id nodes
            function_name = ".".join(id._value[0] for id in fn_import._value)
                
        else:  # CompositeIdWithClosure
            # CompositeIdWithClosure has name and values attributes
            name, values = fn_import._value
            
            if isinstance(name, CompositeId):
                # If name is a CompositeId, join its parts
                base_path = ".".join(id._value[0] for id in name._value)
            else:
                # If name is a single Id
                base_path = name._value[0] if name else ""
                
            # Get the function name from values
            if values:
                function_name = f"{base_path}.{values[0]._value[0]}" if base_path else values[0]._value[0]
            else:
                function_name = base_path
        
        # Find the source file
        source_location = locate_function_source(function_name, project_root)
        if isinstance(source_location, ErrorHandler):
            return [], [source_location]
        elif isinstance(source_location, tuple):
            source_location = source_location[0]  # Extract path from (path, warning) tuple
            
        # Get definitions from the source using a dialect-specific parser
        definitions = get_function_definitions(source_location, function_name, lambda ast: [])
            
        # Convert definitions to FnDef AST nodes
        fn_defs = []
        for definition in definitions:
            fn_def = FnDef(
                fn_name=Id(definition["name"]),
                fn_type=Id(definition["type"]),
                args=FnArgs(),  # Empty args for now
                body=Body()  # Empty body for now
            )
            fn_defs.append(fn_def)
            
        return fn_defs, []
    except Exception as e:
        return [], [ErrorHandler(f"Failed to process function {function_name if 'function_name' in locals() else fn_import}: {str(e)}")]


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
        # Process each function in the import
        for fn in fn_import._value:
            # Handle nested imports with multiple functions
            if isinstance(fn, CompositeId) and isinstance(fn._value, str):
                if "{" in fn._value and "}" in fn._value:
                    base_path, functions = fn._value.rsplit(".", 1)
                    functions = functions.strip("{}").split()
                    
                    # Process each function in the nested import
                    for func in functions:
                        full_name = f"{base_path}.{func}"
                        fn_defs, errors = parse_fn_import(CompositeId(full_name), project_root)
                        
                        if errors:
                            all_errors.extend(errors)
                            return all_fn_defs, all_errors
                            
                        # Add new function definitions, avoiding duplicates
                        for fn_def in fn_defs:
                            if not any(
                                existing.fn_name._value[0] == fn_def.fn_name._value[0] and
                                existing.fn_type._value[0] == fn_def.fn_type._value[0]
                                for existing in all_fn_defs
                            ):
                                all_fn_defs.append(fn_def)
                    continue
            
            # Regular function import
            fn_defs, errors = parse_fn_import(fn, project_root)
            
            if errors:
                all_errors.extend(errors)
                return all_fn_defs, all_errors
                
            # Add new function definitions, avoiding duplicates
            for fn_def in fn_defs:
                if not any(
                    existing.fn_name._value[0] == fn_def.fn_name._value[0] and
                    existing.fn_type._value[0] == fn_def.fn_type._value[0]
                    for existing in all_fn_defs
                ):
                    all_fn_defs.append(fn_def)
            
    return all_fn_defs, all_errors


def parse_imports(code: Imports) -> Any:
    pass
