from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

import pytest

from hhat_lang.core.code.ir_graph import IRGraph
from hhat_lang.dialects.heather.grammar.fn_grammar import fn_program
from hhat_lang.dialects.heather.parsing.ir_visitor import parse, parser_grammar_code


@pytest.mark.parametrize("project", ["project_recipe1", "project_recipe2"])
def test_parse(project: Callable, request) -> None:
    project = request.getfixturevalue(project)
    _path: Path = project()
    assert _path.exists()

    main_file = _path / "src" / "main.hat"
    code = open(main_file, "r").read()
    ir_graph = IRGraph()

    try:
        parse(parser_grammar_code, fn_program, code, _path, main_file, ir_graph)
        ir_graph.build()
        print(ir_graph)

    except Exception as e:
        shutil.rmtree(_path)
        raise Exception(e)

    else:
        shutil.rmtree(_path)
