from __future__ import annotations

from hhat_lang.dialects.heather.interpreter.parser import eval_ir
from hhat_lang.dialects.heather.syntax.run_parser import parser_code_example


def eval_code_example(example_file: str | None = None) -> None:
    _, parsed_code = parser_code_example(example_file)
    eval_ir(parsed_code)
