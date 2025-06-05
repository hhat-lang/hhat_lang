import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.dialects.heather.code.ast import (
    Id,
    CompositeId,
    CompositeIdWithClosure,
    FnDef,
    Imports,
    FnImport,
    FnArgs,
    Body
)
from hhat_lang.dialects.heather.parsing.imports import parse_fns, parse_fn_import

@pytest.fixture
def mock_imports():
    """Create mock imports AST node."""
    return Imports(
        type_import=(),
        fn_import=(FnImport((
            Id("main_function"),
            CompositeId(Id("math"), Id("sum")),
            CompositeIdWithClosure(
                Id("dot"),
                name=CompositeId(Id("math"), Id("linalg"))
            )
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
    mock_content = "mock file content"
    with patch("builtins.open", mock_open(read_data=mock_content)) as mock_file, \
         patch("hhat_lang.core.code.function_resolver.locate_function_source") as mock_locate, \
         patch("hhat_lang.core.code.function_resolver.get_function_definitions", autospec=True) as mock_get_defs:
        
        # Setup mocks
        mock_locate.return_value = tmp_path / "test.hat"
        mock_def = {
            "name": "main_function",
            "type": "void",
            "args": [],
            "body": []
        }
        mock_get_defs.return_value = [mock_def]
        
        # Test
        fn_defs, errors = parse_fn_import(Id("main_function"), tmp_path)
        assert len(fn_defs) == 1
        assert fn_defs[0].fn_name._value[0] == "main_function"

def test_parse_fn_import_with_composite_id(tmp_path):
    mock_content = "mock file content"
    with patch("builtins.open", mock_open(read_data=mock_content)) as mock_file, \
         patch("hhat_lang.core.code.function_resolver.locate_function_source") as mock_locate, \
         patch("hhat_lang.core.code.function_resolver.get_function_definitions", autospec=True) as mock_get_defs:
        
        # Setup mocks
        mock_locate.return_value = tmp_path / "math/sum.hat"
        mock_def = {
            "name": "sum",
            "type": "void",
            "args": [],
            "body": []
        }
        mock_get_defs.return_value = [mock_def]
        
        # Test with proper CompositeId construction
        fn_defs, errors = parse_fn_import(
            CompositeId(Id("math"), Id("sum")),
            tmp_path
        )
        assert len(fn_defs) == 1
        assert fn_defs[0].fn_name._value[0] == "sum"

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
        # Create mock FnDef objects with proper attributes
        fn_def1 = MagicMock(spec=FnDef)
        fn_def1.fn_name = Id("main_function")
        fn_def1.fn_type = Id("void")
        
        fn_def2 = MagicMock(spec=FnDef)
        fn_def2.fn_name = Id("sum")
        fn_def2.fn_type = Id("int")
        
        fn_def3 = MagicMock(spec=FnDef)
        fn_def3.fn_name = Id("dot")
        fn_def3.fn_type = Id("float")
        
        # Setup mock to return function defs
        mock_parse.side_effect = [
            ([fn_def1], []),  # First import
            ([fn_def2], []),  # Second import
            ([fn_def3], [])   # Third import
        ]
        
        # Test
        fn_defs, errors = parse_fns(mock_imports, tmp_path)
        
        assert len(fn_defs) == 3
        assert [fn.fn_name._value[0] for fn in fn_defs] == ["main_function", "sum", "dot"]

def test_parse_fns_with_errors(tmp_path, mock_imports):
    with patch("hhat_lang.dialects.heather.parsing.imports.parse_fn_import") as mock_parse:
        # Create mock FnDef objects with proper attributes
        fn_def1 = MagicMock(spec=FnDef)
        fn_def1.fn_name = Id("main_function")
        fn_def1.fn_type = Id("void")
        
        fn_def2 = MagicMock(spec=FnDef)
        fn_def2.fn_name = Id("dot")
        fn_def2.fn_type = Id("float")
        
        # Setup mock to return error for second import
        mock_parse.side_effect = [
            ([fn_def1], []),  # First import succeeds
            ([], [ErrorHandler("Test error")]),  # Second import fails
            ([fn_def2], [])  # Third import succeeds
        ]
        
        # Test
        fn_defs, errors = parse_fns(mock_imports, tmp_path)
        
        assert len(fn_defs) == 1  # Only first import succeeds
        assert fn_defs[0].fn_name._value[0] == "main_function"
        assert len(errors) == 1

def test_parse_fns_default_project_root(mock_imports):
    with patch("pathlib.Path.cwd") as mock_cwd, \
         patch("hhat_lang.dialects.heather.parsing.imports.parse_fn_import") as mock_parse:
        
        # Setup mocks
        mock_cwd.return_value = Path("/mock/path")
        mock_parse.return_value = ([], [])
        
        # Test with no project_root provided
        parse_fns(mock_imports)
        
        # Verify cwd was used
        assert mock_parse.call_count == 3  # One call for each function in the import
        assert all(
            call[0][1] == Path("/mock/path")  # Check project_root argument
            for call in mock_parse.call_args_list
        )

def test_parse_fn_import_with_relabeling(tmp_path):
    mock_content = "mock file content"
    with patch("builtins.open", mock_open(read_data=mock_content)) as mock_file, \
         patch("hhat_lang.core.code.function_resolver.locate_function_source") as mock_locate, \
         patch("hhat_lang.core.code.function_resolver.get_function_definitions", autospec=True) as mock_get_defs:
        
        # Setup mocks
        mock_locate.return_value = tmp_path / "stats/rv-continuous.hat"
        mock_def = {
            "name": "rv-continuous",
            "type": "void",
            "args": [],
            "body": []
        }
        mock_get_defs.return_value = [mock_def]
        
        # Test with proper CompositeIdWithClosure construction
        fn_defs, errors = parse_fn_import(
            CompositeIdWithClosure(
                Id("rv-continuous"),
                name=CompositeId(Id("stats"))
            ),
            tmp_path
        )
        assert len(fn_defs) == 1
        assert fn_defs[0].fn_name._value[0] == "rv-continuous"

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
        
        # Create mock FnDef objects with proper attributes
        fn_def1 = MagicMock(spec=FnDef)
        fn_def1.fn_name = Id("sum")  # int version
        fn_def1.fn_type = Id("int")
        
        fn_def2 = MagicMock(spec=FnDef)
        fn_def2.fn_name = Id("sum")  # float version
        fn_def2.fn_type = Id("float")
        
        # Setup mock to return multiple definitions for the same function
        mock_parse.return_value = ([fn_def1, fn_def2], [])
        
        # Test
        fn_defs, errors = parse_fns(imports, tmp_path)
        
        assert len(fn_defs) == 2  # Both overloaded versions
        assert all(fn.fn_name._value[0] == "sum" for fn in fn_defs)
        assert [fn.fn_type._value[0] for fn in fn_defs] == ["int", "float"]

def test_parse_fns_nested_imports(tmp_path):
    with patch("hhat_lang.dialects.heather.parsing.imports.parse_fn_import") as mock_parse:
        # Create imports with nested paths using proper AST construction
        imports = Imports(
            type_import=(),
            fn_import=(FnImport((
                CompositeId(Id("math"), Id("linalg"), Id("matrix")),
                CompositeId(Id("utils"), Id("io"), Id("file"))
            )),)
        )
        
        # Create mock FnDef objects
        fn_def1 = MagicMock(spec=FnDef)
        fn_def1.fn_name = Id("multiply")
        fn_def1.fn_type = Id("matrix")
        
        fn_def2 = MagicMock(spec=FnDef)
        fn_def2.fn_name = Id("transpose")
        fn_def2.fn_type = Id("matrix")
        
        # Setup mock to return functions
        mock_parse.side_effect = [
            ([fn_def1], []),
            ([fn_def2], [])
        ]
        
        # Test
        fn_defs, errors = parse_fns(imports, tmp_path)
        assert len(fn_defs) == 2
        assert fn_defs[0].fn_name._value[0] == "multiply"
        assert fn_defs[1].fn_name._value[0] == "transpose"

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