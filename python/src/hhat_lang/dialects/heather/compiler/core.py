from __future__ import annotations

from typing import Callable

from arpeggio import ParserPython

from hhat_lang.core.code.ir_graph import IRGraph
from hhat_lang.core.compiler.builtin_modules import gen_builtin_modules
from hhat_lang.core.config.base import HhatProjectSettings
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import IR, IRModule
from hhat_lang.dialects.heather.grammar.fn_grammar import fn_program
from hhat_lang.dialects.heather.parsing.ir_visitor import parse, parser_grammar_code
from hhat_lang.toolchain.project import MAIN_PATH


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

    # TODO: move gen_builtin_modules below parse after checking
    #  built-in load and functions are working
    gen_builtin_modules(ir_graph, ir_module, ir)
    parse(
        grammar_parser=grammar_parser,
        program_rule=program_rule,
        raw_code=raw_code,
        project_root=project_settings.project_root,
        module_path=project_settings.project_root / MAIN_PATH,
        ir_graph=ir_graph,
    )
    ir_graph.build()
    return ir_graph
