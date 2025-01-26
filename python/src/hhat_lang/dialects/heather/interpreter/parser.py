from __future__ import annotations

from hhat_lang.dialects.heather.interpreter.evaluate import Evaluate
from hhat_lang.dialects.heather.ir.parser import parse_to_ir
from hhat_lang.dialects.heather.syntax.ast import Program
from hhat_lang.dialects.heather.syntax.base import Node


def eval_ir(parsed_code: Node | Program) -> None:
    if not isinstance(parsed_code, Program):
        eval_ir(parsed_code.nodes[0])
    ir_code = parse_to_ir(parsed_code)
    evaluator = Evaluate(ir_code)
    evaluator.run()
