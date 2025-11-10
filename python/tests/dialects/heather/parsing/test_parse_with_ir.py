from __future__ import annotations

import cProfile
import os
import shutil
from copy import deepcopy
from pathlib import Path
from pstats import SortKey, Stats, StatsProfile
from typing import Callable

import pytest

from hhat_lang.core.code.abstract import IRHash
from hhat_lang.core.code.ir_graph import IRGraph
from hhat_lang.dialects.heather.grammar.fn_grammar import fn_program
from hhat_lang.dialects.heather.parsing.ir_visitor import parse, parser_grammar_code
from hhat_lang.toolchain.project.new import (
    create_new_file,
    create_new_project,
    create_new_type_file,
)

THIS = Path(__file__).parent


def types_ex_main04(files: tuple[Path, ...]) -> None:
    with open(files[0], "a") as f:
        f.write("type space {x:i64 y:u64 z:i64}\ntype surface:u64\ntype volume:u64\n")
    print(f"{THIS=} | folder {files[0].parent}:{os.listdir(files[0].parent)}")

    with open(files[1], "a") as f:
        f.write("type form {vol:u64}\n")


def fns_ex_main04(files: tuple[Path, ...]) -> None:
    pass


def types_ex_main05(files: tuple[Path, ...]) -> None:
    with open(files[0], "a") as f:
        f.write("type point:i64\ntype line {x:i32}\ntype surface:u64\n")

    with open(files[1], "a") as f:
        f.write("type plane {x:i32 y:i32}\n")

    with open(files[2], "a") as f:
        f.write("type normal {dx:i32 dy:i32 dz:i32}")

    with open(files[3], "a") as f:
        f.write("type socket {raw:u32}")

    with open(files[4], "a") as f:
        f.write("type @sync_bool {@source:@bool @target:@bool}")


def fns_ex_main05(files: tuple[Path, ...]) -> None:
    with open(files[0], "a") as f:
        f.write(
            # floor()
            "fn floor (x:f64) i64 {\n"
            "  xi:i64 = x*i64\n"
            "  ::if(and(ltz(x) ne(x xi*f64)):sub(xi 1) true:xi)\n"
            "}\n"
            # mod-2pi()
            "fn mod-2pi (theta:f64) f64 {\n"
            "  two-pi:f64 = 6.283185307179586\n"
            "  quot:i64 = floor(div(theta two-pi))\n"
            "  ::sub(theta mul(two-pi quot*f64))\n"
            "}\n"
            # mod-pi()
            "fn mod-pi (theta:f64) f64 {\n"
            "  pi:f64 = 3.141592653589793\n"
            "  two-pi:f64 = 6.283185307179586\n"
            "  quot:i64 = floor(div(add(theta pi) two-pi))\n"
            "  ::sub(theta mul(two-pi quot*f64))\n"
            "}\n"
            # abs()
            "fn abs (x:f64) f64 {\n"
            "  bit63:u64 = 9223372036854775807 // sub(pow(2 63) 1), clear sign bit\n"
            "  b:u64\n"
            "  memcpy(b<&> x<&> sizeof(b))\n"
            "  memcpy(x<&> b-and(b bit63)<&> sizeof(x))\n"
            "  ::x\n"
            "}\n"
            # sin()
            "fn sin (theta:f64) f64 {\n"
            "  pi:f64 = 3.141592653589793\n"
            "  pi2:f64 = pow(pi 2.0)\n"
            "  new-theta:f64 = mod-pi(theta)\n"
            "  abs-theta:f64 = if(ltz(new-theta):neg(new-theta) true:new-theta)\n"
            "  quad-approx:f64 = sub(div(4.0 pi) div(mul(4.0 abs(new-theta)) pi2))\n"
            "  ::mul(new-theta quad-approx)\n"
            "}\n"
        )


@pytest.mark.parametrize(
    "type_fn, fn_fn, file_name, type_files, fn_files",
    [
        (
            types_ex_main04,
            fns_ex_main04,
            "ex_main04.hat",
            ("geometry/euclidian", "geometry/differential"),
            (),
        ),
        (
            types_ex_main05,
            fns_ex_main05,
            "ex_main05.hat",
            (
                "geometry/euclidian2",
                "geometry/euclidian2",
                "geometry/differential2",
                "std/io",
                "std/base",
            ),
            ("math",),
        ),
    ],
)
def test_parse_type_ir(
    type_fn: Callable,
    fn_fn: Callable,
    file_name: str,
    type_files: tuple[str, ...],
    fn_files: tuple[str, ...],
) -> None:
    # # uncomment below to enable cProfile-ing the code, to
    # # check for time execution bottlenecks
    # pr = cProfile.Profile()
    # pr.enable()

    project_name = "parse-test"
    project_root = Path(THIS / project_name).resolve()

    project_main_file_cp = project_root / "src" / file_name
    project_main_file = project_root / "src" / "main.hat"

    try:
        if not project_root.exists():
            create_new_project(project_root)

        types_path = ()

        for k in type_files:
            types_path += (create_new_type_file(project_root, k),)

        type_fn(types_path)
        assert all(k.exists() for k in types_path)

        fns_path = ()

        for f in fn_files:
            fns_path += (create_new_file(project_root, f),)

        fn_fn(fns_path)
        assert all(k.exists() for k in fns_path)

        shutil.copy(src=(THIS / file_name), dst=project_main_file_cp)
        shutil.move(project_main_file_cp, project_main_file)

        code = open(project_main_file.resolve(), "r").read()

        try:
            ir_graph = IRGraph()
            parse(
                parser_grammar_code,
                fn_program,
                code,
                project_root,
                project_main_file,
                ir_graph,
            )

            ir_graph.build()
            main_node = ir_graph.nodes[IRHash(project_main_file)]
            assert ir_graph.nodes[ir_graph.main_node] == main_node

            # # uncomment below for prints of the raw code and the IR graph
            # print(f"\nnum nodes in the graph: {len(ir_graph.nodes)}")
            # print(
            #     f"main node has hash {ir_graph.main_node} and is on position"
            #     f"{get_hash(hash(ir_graph.main_node), ir_graph.nodes.phf)}"
            # )
            # print(f"[!] code:\n{code}\n")
            # print(f"\nir graph:\n{ir_graph}")

        finally:
            pass

    finally:
        # # comment the line below to avoid deleting the folder with the project;
        # # useful for debugging possible project toolchain-related errors
        # shutil.rmtree(project_root)
        pass

        # # uncomment below to enable cProfile-ing the code, to
        # # check for time execution bottlenecks
        # pr.disable()
        # pr.print_stats(sort=SortKey.CUMULATIVE)
        # ps = Stats(pr).sort_stats(SortKey.CUMULATIVE)
        #
        # print(f"print callers:\n")
        # ps.print_callers()
        #
        # print("print callees:\n")
        # ps.print_callees()
