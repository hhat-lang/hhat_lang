from __future__ import annotations

from typing import Any

from hhat_lang.dialects.heather.syntax.run_parser import parser_code_example
from hhat_lang.dialects.heather.ir.parser import parse_to_ir


def ir_code_example(example_file: str | None = None) -> Any:
    code, parsed_code = parser_code_example(example_file)
    print("H-hat Heather dialect IR test\n\n\n")
    print("* Running IR process\n")
    print(f"* Parsed code:\n\n{parsed_code}")
    ir_code = parse_to_ir(parsed_code)
    print(ir_code)
    return ir_code


if __name__ == "__main__":
    ir_code_example("simple_program_cast.hat")
