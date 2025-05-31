import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.dialects.heather.code.ast import (
    Id,
    CompositeId,
    CompositeIdWithClosure,
    FnDef,
    Imports,
    FnImport
)
from hhat_lang.dialects.heather.parsing.imports import parse_fns, parse_fn_import

@pytest.fixture
def mock_imports():
    """Create mock imports AST node."""
    return Imports(
        type_import=(),
        fn_import=(FnImport((
            Id("main_function"),
            CompositeId("math.sum"),
            CompositeIdWithClosure(name="math.linalg.dot")
        )),)
    )

@pytest.fixture
def mock_function_definition():
    """Create a mock function definition."""
    return {
        "name": "test_function",
        "type": "function",
        "args": [],
        "body": []
    }

def test_parse_fn_import_with_id(tmp_path):
    with patch("hhat_lang.core.code.function_resolver.locate_function_source") as mock_locate, \
         patch("hhat_lang.core.code.function_resolver.get_function_definitions") as mock_get_defs:
        
        # Setup mocks
        mock_locate.return_value = tmp_path / "test.hat"
        mock_get_defs.return_value = iter([{
            "name": "main_function",
            "type": "function",
            "args": [],
            "body": []
        }])
        
        # Test
        fn_defs, errors = parse_fn_import(Id("main_function"), tmp_path)
        
        assert len(fn_defs) == 1
        assert isinstance(fn_defs[0], FnDef)
        assert len(errors) == 0

def test_parse_fn_import_with_composite_id(tmp_path):
    with patch("hhat_lang.core.code.function_resolver.locate_function_source") as mock_locate, \
         patch("hhat_lang.core.code.function_resolver.get_function_definitions") as mock_get_defs:
        
        # Setup mocks
        mock_locate.return_value = tmp_path / "math/sum.hat"
        mock_get_defs.return_value = iter([{
            "name": "sum",
            "type": "function",
            "args": [],
            "body": []
        }])
        
        # Test
        fn_defs, errors = parse_fn_import(CompositeId("math.sum"), tmp_path)
        
        assert len(fn_defs) == 1
        assert isinstance(fn_defs[0], FnDef)
        assert len(errors) == 0

def test_parse_fn_import_not_found(tmp_path):
    with patch("hhat_lang.core.code.function_resolver.locate_function_source") as mock_locate:
        # Setup mock to return error
        mock_locate.return_value = ErrorHandler("Function not found")
        
        # Test
        fn_defs, errors = parse_fn_import(Id("nonexistent"), tmp_path)
        
        assert len(fn_defs) == 0
        assert len(errors) == 1
        assert isinstance(errors[0], ErrorHandler)

def test_parse_fns_multiple_imports(tmp_path, mock_imports):
    with patch("hhat_lang.dialects.heather.parsing.imports.parse_fn_import") as mock_parse:
        # Setup mock to return a function def and no errors
        mock_parse.return_value = ([MagicMock(spec=FnDef)], [])
        
        # Test
        fn_defs, errors = parse_fns(mock_imports, tmp_path)
        
        assert len(fn_defs) == 3  # One for each import
        assert len(errors) == 0
        assert mock_parse.call_count == 3

def test_parse_fns_with_errors(tmp_path, mock_imports):
    with patch("hhat_lang.dialects.heather.parsing.imports.parse_fn_import") as mock_parse:
        # Setup mock to return error for second import
        mock_parse.side_effect = [
            ([MagicMock(spec=FnDef)], []),
            ([], [ErrorHandler("Test error")]),
            ([MagicMock(spec=FnDef)], [])
        ]
        
        # Test
        fn_defs, errors = parse_fns(mock_imports, tmp_path)
        
        assert len(fn_defs) == 2  # Two successful imports
        assert len(errors) == 1  # One error from failed import
        assert mock_parse.call_count == 3

def test_parse_fns_default_project_root(mock_imports):
    with patch("pathlib.Path.cwd") as mock_cwd, \
         patch("hhat_lang.dialects.heather.parsing.imports.parse_fn_import") as mock_parse:
        
        # Setup mocks
        mock_cwd.return_value = Path("/mock/path")
        mock_parse.return_value = ([], [])
        
        # Test with no project_root provided
        parse_fns(mock_imports)
        
        # Verify cwd was used
        mock_parse.assert_called_with(mock_imports.value[-1], Path("/mock/path"))

def test_parse_fn_import_with_relabeling(tmp_path):
    with patch("hhat_lang.core.code.function_resolver.locate_function_source") as mock_locate, \
         patch("hhat_lang.core.code.function_resolver.get_function_definitions") as mock_get_defs:
        
        # Setup mocks
        mock_locate.return_value = tmp_path / "stats/rv-continuous.hat"
        mock_get_defs.return_value = iter([{
            "name": "rv-continuous",
            "type": "function",
            "args": [],
            "body": []
        }])
        
        # Test with relabeling
        fn_defs, errors = parse_fn_import(
            CompositeIdWithClosure(name="stats.{rv-continuous:rvc}"),
            tmp_path
        )
        
        assert len(fn_defs) == 1
        assert isinstance(fn_defs[0], FnDef)
        assert str(fn_defs[0].fn_name.value[0]) == "rvc"  # Check relabeled name
        assert len(errors) == 0

def test_parse_fns_multiple_files(tmp_path):
    with patch("hhat_lang.dialects.heather.parsing.imports.parse_fn_import") as mock_parse:
        # Create imports with functions from different files
        imports = Imports(
            type_import=(),
            fn_import=(FnImport((
                Id("main_function"),  # from main.hat
                CompositeId("math.sum"),  # from math/sum.hat
                CompositeId("utils.helper")  # from utils/helper.hat
            )),)
        )
        
        # Setup mock to return different functions
        mock_parse.side_effect = [
            ([MagicMock(spec=FnDef, fn_name=Id("main_function"))], []),
            ([MagicMock(spec=FnDef, fn_name=Id("sum"))], []),
            ([MagicMock(spec=FnDef, fn_name=Id("helper"))], [])
        ]
        
        # Test
        fn_defs, errors = parse_fns(imports, tmp_path)
        
        assert len(fn_defs) == 3
        assert len(errors) == 0
        assert mock_parse.call_count == 3

def test_parse_fns_with_overloaded_functions(tmp_path):
    with patch("hhat_lang.dialects.heather.parsing.imports.parse_fn_import") as mock_parse:
        imports = Imports(
            type_import=(),
            fn_import=(FnImport((
                CompositeId("math.sum")  # Overloaded function
            )),)
        )
        
        # Setup mock to return multiple definitions for the same function
        mock_parse.return_value = (
            [
                MagicMock(spec=FnDef, fn_name=Id("sum")),  # int version
                MagicMock(spec=FnDef, fn_name=Id("sum"))   # float version
            ],
            []
        )
        
        # Test
        fn_defs, errors = parse_fns(imports, tmp_path)
        
        assert len(fn_defs) == 2  # Both overloaded versions
        assert len(errors) == 0

def test_parse_fns_nested_imports(tmp_path):
    with patch("hhat_lang.dialects.heather.parsing.imports.parse_fn_import") as mock_parse:
        # Create imports with nested paths
        imports = Imports(
            type_import=(),
            fn_import=(FnImport((
                CompositeId("math.linalg.matrix.{multiply transpose}"),
                CompositeId("utils.io.file.{read write}")
            )),)
        )
        
        # Setup mock to return functions
        mock_parse.return_value = ([MagicMock(spec=FnDef)], [])
        
        # Test
        fn_defs, errors = parse_fns(imports, tmp_path)
        
        assert len(fn_defs) == 2
        assert len(errors) == 0
        assert mock_parse.call_count == 2

def test_parse_fns_stops_on_first_error(tmp_path):
    with patch("hhat_lang.dialects.heather.parsing.imports.parse_fn_import") as mock_parse:
        imports = Imports(
            type_import=(),
            fn_import=(FnImport((
                Id("valid_function"),
                Id("invalid_function"),  # This will cause an error
                Id("never_reached")      # This should not be processed
            )),)
        )
        
        # Setup mock to return success then error
        mock_parse.side_effect = [
            ([MagicMock(spec=FnDef)], []),  # First call succeeds
            ([], [ErrorHandler("Test error")]),  # Second call fails
            ([MagicMock(spec=FnDef)], [])   # Should never be called
        ]
        
        # Test
        fn_defs, errors = parse_fns(imports, tmp_path)
        
        assert len(fn_defs) == 1  # Only the first function
        assert len(errors) == 1  # The error from the second function
        assert mock_parse.call_count == 2  # Third function not processed 