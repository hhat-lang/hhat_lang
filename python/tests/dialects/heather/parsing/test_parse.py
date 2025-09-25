from __future__ import annotations

import pytest
from pathlib import Path

from hhat_lang.dialects.heather.parsing.run import (
    parse_grammar,
    parse,
    parse_file,
)

THIS = Path(__file__).parent


def test_parse_grammar() -> None:
    assert parse_grammar()


@pytest.mark.parametrize(
    "hat_file",
    ["ex_type01.hat", "ex_type02.hat"]
)
def test_parse_type_sample_file(hat_file) -> None:
    hat_file = (THIS / hat_file).resolve()
    assert parse_file(hat_file)


@pytest.mark.parametrize(
    "hat_file",
    ["ex_fn01.hat", "ex_fn02.hat"]
)
def test_parse_fn_sample_file(hat_file) -> None:
    hat_file = (THIS / hat_file).resolve()
    assert parse_file(hat_file)


@pytest.mark.parametrize(
    "hat_file",
    ["ex_main01.hat", "ex_main02.hat"]
)
def test_parse_main_sample_file(hat_file) -> None:
    hat_file = (THIS / hat_file).resolve()
    assert parse_file(hat_file)
