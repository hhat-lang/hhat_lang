from copy import deepcopy
from typing import Any
from hhat_lang.interpreter.post_ast import R
from hhat_lang.interpreter.var_handlers import Var
from hhat_lang.syntax_trees.ast import ATO
from hhat_lang.datatypes.builtin_datatype import (
    builtin_data_types_dict,
    builtin_array_types_dict,
    quantum_array_types_list,
    DefaultType
)
from hhat_lang.datatypes.base_datatype import DataType, DataTypeArray
from hhat_lang.builtins.functions import builtin_fn_dict, builtin_quantum_fn_dict
from hhat_lang.utils.utils import get_types_set
from hhat_lang.interpreter.memory import Mem


class Eval:
    def __init__(self, code: R):
        self.code = code

    def run(self):
        mem = Mem()
        execute(self.code, mem)
        print(mem)


def eval_token(code: ATO, mem: Mem) -> Any:
    if code.type in ["oper", "@oper", "id"]:
        # print(f"  = oper:", end=" ")
        if res := builtin_fn_dict.get(code.token, False):
            return res
        if code.token in mem:
            return mem.get_var(code.token)
        return Var(code.token)
    # print(f"  = literal:", end=" ")
    return builtin_data_types_dict.get(code.type, DefaultType)(code.token)


def eval_oper(code: R, mem: Mem) -> Any:
    # print("* oper:")
    res = ()
    # print(f"  -> oper content: {code} {[(k, type(k)) for k in code]}")
    for k in code:
        last = execute(k, mem)
        if isinstance(last[0], Var):
            # print(f"  => {type(k)} {code.role}")
            if code.role == "callee":
                # print("  ! oper callee found!")
                var = mem.get_var(last[0].name)
                # print(f"  ! [oper callee] after mem: {mem}")
                res += var,
            else:
                # print("IS VAR!!")
                mem.put_expr(last[0])
                res += last
        elif isinstance(last[0], (DataType, DataTypeArray)):
            mem.put_stack(last[0])
            res += last
        else:
            data = mem.get_stack()
            types = get_types_set(*data)
            if (
                len(set(quantum_array_types_list).intersection(types)) > 0
                and last[0].token in builtin_quantum_fn_dict.keys()
            ):
                # this has some quantum, let's do the magic
                print(f"* * has quantum! {code} -> {data}")
                data = data + (code,)
                oper = last[0](mem, *data)
            else:
                # this is not quantum, just keep rolling
                oper = last[0](mem, *data)
            # print(f"---> {type(oper)} {oper}")
            mem.put_expr(oper)
            # mem.put_stack(oper)
            res += oper,
    # print(f"  -> oper res: {res}")
    return res


def eval_args(code: R, mem: Mem) -> Any:
    # print("* args:")
    res = ()
    # print(f"    -> {len(code)} {code}")
    for k in code:
        # print(f"  !=> what is k: {k} | {mem}")
        last = execute(k, mem)
        # print(f"  => arg data: {last[0]} ({type(last[0])}) {type(last)} ({code}) {mem=}")
        mem.put_stack(last[0])
        res += last
    return res


def eval_call(code: R, mem: Mem) -> Any:
    # print("* call:")
    res = ()
    for k in code:
        res += execute(k, mem)
    # print(f"! what is call res: {res}")
    if len(code) == 2:
        args = mem.pop_stack()
        oper = mem.pop_expr()
        # print(f"call: {oper=} | {args=} ({type(args)})")
        new_res = oper(args)
        for p in new_res:
            mem.put_stack(p)
        new_res = ()
    else:
        if isinstance(res[0], Var):
            if res[0].initialized:
                new_res = res
            else:
                mem.pop_expr()
                # print(f"VAR!? {code=} | {res[0]=} | {mem=}")
                new_res = res[0](mem.pop_stack()),
                mem.put_var(res[0], "")
                mem.put_stack(res[0])
        else:
            print(f"? {code}")
            oper = mem.pop_expr()
            if oper.token in builtin_fn_dict.keys():
                new_res = oper()
                # print(f"* [{oper}] received {new_res=}")
                for p in new_res:
                    mem.put_stack(p)
            else:
                print("WHAT")
                new_res = res
    return new_res


def eval_array(code: R, mem: Mem) -> Any:
    # print("* array:")
    res = ()
    for k in code:
        res += execute(k, mem)
    # print(f"! {res=} {len(set(k.type for k in res))=}")
    if len(set(k.type for k in res)) == 1:
        if isinstance(res[0], DataType):
            array = builtin_array_types_dict[res[0].type](*res)
            mem.put_stack(array)
            res = array,
        elif isinstance(res[0], int):
            print("* WE GOT AN INT!!")
    return res


def eval_expr(code: R, mem: Mem) -> Any:
    # print("* expr:")
    res = ()
    for k in code:
        res += execute(k, mem)
        # print(f"  [end][expr]-> after mem: {mem} | {res=}")
    return (res[-1],) if res else ()


def eval_many_expr(code: R, mem: Mem) -> Any:
    # print("* many-expr:")
    # print(f"  [cur]-> {mem}")
    res = ()
    for n, k in enumerate(code):
        new_mem = deepcopy(mem)
        # print(f"  [{n}][start][many-expr]({k})")
        # print(f"     -> prev mem: {mem}")
        # print(f"     -> new mem: {new_mem}")
        res += execute(k, new_mem)
        new_mem.share_vars(mem)
        # print(f"  [{n}][end][many-expr]({k}) -> after new mem: {new_mem} | mem: {mem} | {res=}")
    mem.clear_stack()
    for k in res:
        mem.put_stack(k)
    return res


def eval_main(code: R, mem: Mem) -> Any:
    # print("* main:")
    res = ()
    for k in code:
        res += execute(k, mem),
        mem.clear_stack()
    return res


def execute(code: Any, mem: Mem) -> tuple[Any]:
    res = ()
    match code:
        case R():
            match code.type:
                case "program":
                    pass

                case "main":
                    res = eval_main(code, mem)

                case "many-expr":
                    res = eval_many_expr(code, mem)

                case "expr":
                    res = eval_expr(code, mem)

                case "array":
                    res = eval_array(code, mem)

                case "call":
                    res = eval_call(code, mem)

                case "args":
                    res = eval_args(code, mem)

                case "oper" | "@oper" | "id":
                    res = eval_oper(code, mem)

        case ATO():
            res = eval_token(code, mem)
            # print(res)
            res = res,
    return res
