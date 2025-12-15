from __future__ import annotations

from typing import Callable

from arpeggio import ParserPython

from hhat_lang.core.code.ir_graph import IRGraph
from hhat_lang.core.config.base import HhatProjectSettings
from hhat_lang.core.fns.builtin_ir_builder import gen_all_builtin_modules
from hhat_lang.dialects.heather.code.simple_ir_builder.new_ir import IRModule, IR
from hhat_lang.dialects.heather.grammar.fn_grammar import fn_program
from hhat_lang.dialects.heather.parsing.ir_visitor import parser_grammar_code, parse


def compile_project_ir(
    project_settings: HhatProjectSettings,
    raw_code: str,
    grammar_parser: Callable[[Callable], ParserPython] | None = None,
    program_rule: Callable | None = None,
) -> IRGraph:
    """
    Parse the whole project (including built-in modules), generating an IR graph instance.

    Args:
        project_settings: ``HhatProjectSettings`` instance
        raw_code: code as str
        grammar_parser:
        program_rule:

    Returns:
        An ``IRGraph`` instance for the project.
    """

    grammar_parser = grammar_parser or parser_grammar_code
    program_rule = program_rule or fn_program
    ir_module = IRModule
    ir = IR
    ir_graph = IRGraph()

    gen_all_builtin_modules(ir_graph=ir_graph, ir_module=ir_module, ir=ir)
    parse(
        grammar_parser=grammar_parser,
        program_rule=program_rule,
        raw_code=raw_code,
        project_root=project_settings.project_root,
        module_path=project_settings.project_root / "src" / "main.hat",
        ir_graph=ir_graph,
    )
    ir_graph.build()
    return ir_graph
