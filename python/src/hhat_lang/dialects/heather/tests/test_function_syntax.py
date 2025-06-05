import pytest
from hhat_lang.dialects.heather.code.ast import Id, FnDef, FnArgs, Body

def test_function_syntax():
    # Create AST nodes for a simple function
    fn_name = Id("test_function")
    fn_type = Id("void")
    fn_args = FnArgs()  # Empty args
    fn_body = Body()    # Empty body
    
    fn_def = FnDef(
        fn_name=fn_name,
        fn_type=fn_type,
        args=fn_args,
        body=fn_body
    )
    
    assert fn_def._value[0]._value[0] == "test_function"  # Check function name
    assert fn_def._value[1]._value[0] == "void"          # Check return type

    # Correct Heather syntax
    mock_file_content = """
    fn test_function() void {
        // Function body
    }
    """
    # Test implementation will go here
    # This is just a placeholder to show the correct syntax 