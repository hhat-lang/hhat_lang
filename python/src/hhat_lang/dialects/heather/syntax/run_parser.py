from __future__ import annotations

from pathlib import Path

from hhat_lang.dialects.heather.syntax.base import AST
from hhat_lang.dialects.heather.syntax.parser import parse_code


EXAMPLES_PATH = Path(__file__).parent.parent / "examples"


def parser_code_example(example_file: str | None = None) -> tuple[str, AST]:
    example_file = example_file if example_file is not None else "simple_program_cast.hat"
    code_path = EXAMPLES_PATH / example_file
    _code = open(code_path, "r").read()
    _parsed_code = parse_code(_code)
    return _code, _parsed_code


if __name__ == "__main__":
    code, parsed_code = parser_code_example()
    print("H-hat Heather dialect code parsing test\n\n")
    print(f"* Original code:\n\n{code}\n")
    print("-"*50)
    print(f"* Parsed code:\n\n{parsed_code}\n")
