from __future__ import annotations

from pathlib import Path
from typing import Callable

from pytest import fixture

from .code_samples import (
    io1_types_def,
    math1_types_def,
    math2_types_def,
    math3_types_def,
    math4_types_def,
    math5_types_def,
    math_abs_def,
    math_floor_def,
    math_mod2pi_def,
    math_modpi_def,
    math_sin_def,
    qstd1_types_def,
)
from .utils import start_new_project

RelativePath = Path | str


@fixture
def math_floor_fn() -> str:
    return math_floor_def()


@fixture
def math_mod2pi_fn() -> str:
    return math_mod2pi_def()


@fixture
def math_modpi_fn() -> str:
    return math_modpi_def()


@fixture
def math_abs_fn() -> str:
    return math_abs_def()


@fixture
def math_sin_fn() -> str:
    return math_sin_def()


@fixture
def math_single_file1() -> tuple[RelativePath, str]:
    return (
        "math",
        f"{math_floor_def()}{math_mod2pi_def()}{math_modpi_def()}{math_abs_def()}{math_sin_def()}",
    )


@fixture
def empty_file() -> tuple[RelativePath, str]:
    return "", ""


@fixture
def math1_types_file() -> tuple[RelativePath, str]:
    return (
        "math/geometry/euclidian",
        math1_types_def(),
    )


@fixture
def math2_types_file() -> tuple[RelativePath, str]:
    return (
        "math/geometry/euclidian",
        math2_types_def(),
    )


@fixture
def math3_types_file() -> tuple[RelativePath, str]:
    return "math/geometry/differential", math3_types_def()


@fixture
def math4_types_file() -> tuple[RelativePath, str]:
    return "math/geometry/differential", math4_types_def()


@fixture
def math5_types_file() -> tuple[RelativePath, str]:
    return "math/geometry/euclidian", math5_types_def()


@fixture
def io1_types_file() -> tuple[RelativePath, str]:
    return "std/io/net", io1_types_def()


@fixture
def qstd1_types_file() -> tuple[RelativePath, str]:
    return "std/base", qstd1_types_def()


@fixture
def project_recipe1(
    math4_types_file: tuple[RelativePath, str], math5_types_file: tuple[RelativePath, str]
) -> Callable:
    def _run() -> Path:
        main = """
        use (type:math.geometry.{euclidian.space differential.form})
    
        main {
            p:space =.{x=1.0 y=2.0 z=0.0}
        }
        """
        return start_new_project(
            "project-test1",
            types_files=(math4_types_file, math5_types_file),
            fns_files=(),
            main_file=main,
        )

    return _run


@fixture
def project_recipe2(
    math1_types_file,
    math2_types_file,
    math3_types_file,
    io1_types_file,
    qstd1_types_file,
    math_single_file1,
) -> Callable:
    def _run() -> Path:
        main = """
        use (
            type:[
              math.geometry.{euclidian.{line plane} differential.normal}
              std.{io.net.socket base.@bell_t}
            ]
            fn:math.{sin floor}
        )
        
        main {
            l:line=.{x=41}
            p:plane
            p.{x=250 y=600}
            print(sin(0.0))
            @d:@bell_t=.{@source=@true @target=@false}
        }
        """
        return start_new_project(
            "project-test2",
            types_files=(
                math1_types_file,
                math2_types_file,
                math3_types_file,
                io1_types_file,
                qstd1_types_file,
            ),
            fns_files=(math_single_file1,),
            main_file=main,
        )

    return _run
