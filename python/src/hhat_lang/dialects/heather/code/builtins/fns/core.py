from __future__ import annotations

from typing import Any

from hhat_lang.core.code.base import BaseFnCheck
from hhat_lang.core.code.symbol_table import FnTable
from hhat_lang.core.data.core import Symbol
from hhat_lang.core.data.fn_def import FnDef
from hhat_lang.dialects.heather.code.simple_ir_builder.new_ir import ArgsBlock, BodyBlock


# print single bool
print_single_bool_entry = BaseFnCheck(fn_name=Symbol("print"), args_types=(Symbol("bool"),))
print_single_bool_def = FnDef(
    fn_name=Symbol("print"),
    fn_args=ArgsBlock(Symbol("bool")),
    fn_body=BodyBlock(),
    fn_type=Symbol("null")
)


# print single int
print_single_int_entry = BaseFnCheck(fn_name=Symbol("print"), args_types=(Symbol("int"),))
print_single_int_def = FnDef(
    fn_name=Symbol("print"),
    fn_args=ArgsBlock(Symbol("int")),
    fn_body=BodyBlock(),
    fn_type=Symbol("null")
)

# print single float
print_single_float_entry = BaseFnCheck(fn_name=Symbol("print"), args_types=(Symbol("float"),))
print_single_float_def = FnDef(
    fn_name=Symbol("print"),
    fn_args=ArgsBlock(Symbol("float")),
    fn_body=BodyBlock(),
    fn_type=Symbol("null")
)


fn_table = FnTable()
fn_table.add(print_single_bool_entry, print_single_bool_def)
fn_table.add(print_single_int_entry, print_single_int_def)
fn_table.add(print_single_float_entry, print_single_float_def)
