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
    function_name = str(fn_import.value[0]) if isinstance(fn_import, Id) else str(fn_import)
    
    # Find the source file
    source_location = locate_function_source(function_name, project_root)
    if isinstance(source_location, ErrorHandler):
        return [], [source_location]
        
    # Get function definitions
    definitions = get_function_definitions(source_location, function_name)
    if isinstance(definitions, ErrorHandler):
        return [], [definitions]
        
    # Convert definitions to FnDef AST nodes
    fn_defs = []
    errors = []
    
    for definition in definitions:
        try:
            fn_def = FnDef(
                fn_name=Id(definition["name"]),
                fn_type=definition["type"],
                args=definition["args"],
                body=definition["body"]
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
    
    for fn_import in code.value:
        fn_defs, errors = parse_fn_import(fn_import, project_root)
        all_fn_defs.extend(fn_defs)
        all_errors.extend(errors)
        
    return all_fn_defs, all_errors


def parse_imports(code: Imports) -> Any:
    pass
