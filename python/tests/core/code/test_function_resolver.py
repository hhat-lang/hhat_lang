from pathlib import Path
import pytest
from unittest.mock import mock_open, patch

from hhat_lang.core.code.function_resolver import (
    locate_function_source,
    get_function_definitions,
    parse_function_definition,
    is_valid_path_component,
    FunctionNotFoundError,
    InvalidPathError,
    TypesFunctionWarning
)
from hhat_lang.core.data.core import Symbol, CompositeSymbol

def test_is_valid_path_component():
    # Valid cases
    assert is_valid_path_component("valid")
    assert is_valid_path_component("valid_name")
    assert is_valid_path_component("valid-name")
    assert is_valid_path_component("validName123")
    
    # Invalid cases
    assert not is_valid_path_component("1invalid")  # Starts with number
    assert not is_valid_path_component("hat_invalid")  # Starts with hat_
    assert not is_valid_path_component("invalid@name")  # Special character
    assert not is_valid_path_component("invalid.name")  # Special character
    assert not is_valid_path_component("")  # Empty string

def test_is_valid_path_component_hat_types():
    # hat_types is allowed when explicitly enabled
    assert is_valid_path_component("hat_types", allow_hat_types=True)
    # but not by default
    assert not is_valid_path_component("hat_types")
    # Other hat_ prefixes are never allowed
    assert not is_valid_path_component("hat_other", allow_hat_types=True)

@pytest.fixture
def mock_project_structure(tmp_path):
    """Create a mock project structure for testing."""
    # Create project structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create main.hat
    main_hat = tmp_path / "main.hat"
    main_hat.write_text("// Main file")
    
    # Create nested structure
    math_dir = src_dir / "math"
    math_dir.mkdir()
    linalg_dir = math_dir / "linalg"
    linalg_dir.mkdir()
    
    # Create .hat files
    (math_dir / "sum.hat").write_text("// Sum function")
    (linalg_dir / "dot.hat").write_text("// Dot product function")
    (src_dir / "utils.hat").write_text("// Utility functions")
    
    return tmp_path

def test_locate_function_source_main_hat(mock_project_structure):
    result = locate_function_source("main_function", mock_project_structure)
    assert isinstance(result, Path)
    assert result.name == "main.hat"

def test_locate_function_source_nested(mock_project_structure):
    result = locate_function_source("math.linalg.dot", mock_project_structure)
    assert isinstance(result, Path)
    assert result.name == "dot.hat"
    # Convert Windows path to forward slashes for comparison
    result_str = str(result).replace("\\", "/")
    assert "math/linalg" in result_str

def test_locate_function_source_not_found(mock_project_structure):
    result = locate_function_source("nonexistent.function", mock_project_structure)
    assert isinstance(result, FunctionNotFoundError)

def test_locate_function_source_invalid_name(mock_project_structure):
    result = locate_function_source("1invalid.function", mock_project_structure)
    assert isinstance(result, InvalidPathError)

def test_locate_function_source_with_symbol():
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        result = locate_function_source(Symbol("test_function"), Path("/mock/path"))
        assert isinstance(result, Path)

def test_locate_function_source_with_composite_symbol():
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        result = locate_function_source(CompositeSymbol("math.sum"), Path("/mock/path"))
        assert isinstance(result, Path)

def test_get_function_definitions():
    mock_file_content = """
    // Function definition
    fn test_function() -> void {
        // Function body
    }
    """
    
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        definitions = get_function_definitions(Path("/mock/path/test.hat"), "test_function")
        first_def = next(definitions)
        assert first_def["name"] == "test_function"
        assert first_def["type"] == "function"

def test_get_function_definitions_file_error():
    with patch("builtins.open", side_effect=IOError("Mock error")):
        result = get_function_definitions(Path("/nonexistent/path"), "test_function")
        assert isinstance(result, InvalidPathError)

def test_parse_function_definition_single():
    content = """
    fn test_function(x: int, y: int) -> int {
        return x + y
    }
    """
    
    definitions = parse_function_definition(content)
    assert len(definitions) == 1
    assert definitions[0]['name'] == 'test_function'
    assert definitions[0]['type'] == 'int'
    assert definitions[0]['args'] == ['x: int', 'y: int']
    assert 'return x + y' in definitions[0]['body']

def test_parse_function_definition_overloaded():
    content = """
    fn test_function(x: int) -> int {
        return x * 2
    }
    
    fn test_function(x: float) -> float {
        return x * 2.0
    }
    """
    
    definitions = parse_function_definition(content)
    assert len(definitions) == 2
    assert all(d['name'] == 'test_function' for d in definitions)
    assert definitions[0]['args'] == ['x: int']
    assert definitions[1]['args'] == ['x: float']

def test_parse_function_definition_with_comments():
    content = """
    // This is a comment
    fn test_function() -> void {
        // Inside function comment
        do_something()
    }
    """
    
    definitions = parse_function_definition(content)
    assert len(definitions) == 1
    assert 'do_something()' in definitions[0]['body']
    assert '// Inside function comment' not in definitions[0]['body']

def test_get_function_definitions_overloaded():
    content = """
    fn test_function(x: int) -> int {
        return x
    }
    
    fn test_function(x: float) -> float {
        return x
    }
    """
    
    with patch("builtins.open", mock_open(read_data=content)):
        definitions = list(get_function_definitions(Path("/mock/path/test.hat"), "test_function"))
        assert len(definitions) == 2
        assert all(d['name'] == 'test_function' for d in definitions)
        assert definitions[0]['type'] == 'int'
        assert definitions[1]['type'] == 'float'

def test_get_function_definitions_no_match():
    content = """
    fn other_function() -> void {
        // Some code
    }
    """
    
    with patch("builtins.open", mock_open(read_data=content)):
        definitions = list(get_function_definitions(Path("/mock/path/test.hat"), "test_function"))
        assert len(definitions) == 0

def test_locate_function_source_in_hat_types(mock_project_structure):
    # Create hat_types directory and file
    hat_types_dir = mock_project_structure / "src" / "hat_types" / "math"
    hat_types_dir.mkdir(parents=True)
    test_file = hat_types_dir / "vector.hat"
    test_file.write_text("// Vector type functions")
    
    # Test locating function in hat_types
    result = locate_function_source("hat_types.math.vector", mock_project_structure)
    
    # Should return both path and warning
    assert isinstance(result, tuple)
    path, warning = result
    assert isinstance(path, Path)
    assert path.name == "vector.hat"
    assert isinstance(warning, TypesFunctionWarning)

def test_locate_function_source_invalid_hat_prefix(mock_project_structure):
    # Test with other hat_ prefix (not hat_types)
    result = locate_function_source("hat_invalid.function", mock_project_structure)
    assert isinstance(result, InvalidPathError) 