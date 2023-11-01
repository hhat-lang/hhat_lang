from typing import Any

from copy import deepcopy
import asyncio
from hhat_lang.interpreter.post_ast import R
from hhat_lang.interpreter.var_handlers import Var
from hhat_lang.syntax_trees.ast import ATO, ASTType, operations_or_id
from hhat_lang.datatypes.builtin_datatype import (
    builtin_data_types_dict,
    builtin_array_types_dict,
    quantum_array_types_list,
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
        print("\n", mem)


#######################
# AUXILIARY FUNCTIONS #
#######################

def arrange_array_output(res: tuple, mem: Mem) -> tuple[Any]:
    # TODO: implement a function to deal with single or
    #  multiple array elements
    if len(set(k.type for k in res)) == 1:
        res_type = res[0].type
    else:
        res_type = ASTType.ARRAY

    array = builtin_array_types_dict[res_type](*res)
    mem.put_stack(array)
    return array,


def handle_literals(code: ATO | R, mem: Mem) -> Any:
    pass


def handle_variables(code: ATO | R, mem: Mem) -> Any:
    pass


def handle_functions(code: ATO | R, mem: Mem) -> Any:
    pass


#################################
# SEQUENTIAL PARADIGM FUNCTIONS #
#################################

def eval_seq_fn(code: ATO | R, mem: Mem) -> Any:
    pass


def sequential_paradigm_fn(code: R, mem: Mem) -> Any:
    pass


#################################
# CONCURRENT PARADIGM FUNCTIONS #
#################################


# pain :{{{{{{{{{{{{{{{{{{{{{{{{{{{{

async def eval_conc_fn(code: ATO | R, mem: Mem) -> Any:
    pass


async def concurrent_paradigm_fn(code: R, mem: Mem) -> Any:
    return await asyncio.gather(*[eval_conc_fn(k, mem) for k in code])


###############################
# PARALLEL PARADIGM FUNCTIONS #
###############################

# TODO: start is a good starting point

def eval_par_fn(code: ATO | R, mem: Mem) -> Any:
    pass


def parallel_paradigm_fn(code: R, mem: Mem) -> Any:
    pass


##################
# EVAL FUNCTIONS #
##################

def eval_token(code: ATO, mem: Mem) -> Any:
    print(f"* token: {code}")
    if code.type in operations_or_id:
        if code.token in builtin_fn_dict.keys():
            return builtin_fn_dict[code.token]
        if code.token in mem:
            return mem.get_var(code.token)
        return Var(code.token)
    if code.type in builtin_data_types_dict.keys():
        return builtin_data_types_dict[code.type](code.token)
    raise NotImplementedError(f"Type {code.type} not implemented yet.")


def eval_oper(code: R, mem: Mem) -> Any:
    print("* oper:")
    res = ()
    for k in code:
        last = execute(k, mem)
        if isinstance(last[0], Var):
            # in case the operation is inside the argument
            if code.role == "callee":
                var = mem.get_var(last[0].name)
                res += var,
            else:
                mem.put_expr(last[0])
                res += last
        elif isinstance(last[0], (DataType, DataTypeArray)):
            mem.put_stack(last[0])
            res += last
        else:
            # if data is not variable or data array (should be function?)
            data = mem.pop_stack()
            types = get_types_set(data)
            if (
                len(set(quantum_array_types_list).intersection(types)) > 0
                and last[0].token in builtin_quantum_fn_dict.keys()
            ):
                # this has some quantum, let's do the magic
                print(f"* * has quantum! {code} -> {data}")
                data = data + (code,)
                oper = last[0](mem, *data)
            else:
                oper = last[0](mem, data)
            mem.put_expr(oper)
            res += oper,
    return res


def eval_args(code: R, mem: Mem) -> Any:
    print("* args:")
    res = ()
    for k in code:
        last = execute(k, mem)
        res += last
    res = arrange_array_output(res, mem)
    return res


def eval_call(code: R, mem: Mem) -> Any:
    print("* call:")
    res = ()
    for k in code:
        res += execute(k, mem)

    # if call has arguments
    if len(code) == 2:
        args = mem.pop_stack()
        oper = mem.pop_expr()
        new_res = oper(args)
        for p in new_res:
            mem.put_stack(p)
        new_res = ()
    else:
        if isinstance(res[0], Var):
            if res[0].initialized:
                new_res = res
            else:
                # if var is not initialized yet
                mem.pop_expr()
                new_res = res[0](mem.pop_stack()),
                mem.put_var(res[0], "")
                mem.put_stack(res[0])
        else:
            oper = mem.pop_expr()
            if oper.token in builtin_fn_dict.keys():
                new_res = oper()
                for p in new_res:
                    mem.put_stack(p)
            else:
                print("/!\\ unexpected code /!\\")
                new_res = res
    return new_res


def eval_array(code: R, mem: Mem) -> Any:
    """Evaluating array expressions.

    Everything that contains more than one full expression
    is an array and should be handled by this function.

    Arrays can be sequential, concurrent or parallel sets of data.

    Process:
    - code enters
    - according to its paradigm (sequential, concurrent, parallel),
        it will be handled accordingly
    - iteration over each code element
    - every code element is a full expression by itself
    - at the end of execution of each element, its last element
        will be stored in the outer scope memory, in the same
        order the code was written
    - at the end of array's execution, the last result from each
        full expression will be placed in an array of the same
        paradigm and will be passed forward to the next expression
        to evaluate it
    """
    print("* array:")

    # TODO: implement the paradigms in separated functions:
    # 1- sequential
    # 2- concurrent
    # 3- parallel

    res = ()
    for k in code:
        new_mem = deepcopy(mem)
        res += execute(k, new_mem)
        new_mem.share_vars(mem)
    mem.clear_stack()
    res = arrange_array_output(res, mem)
    return res


def eval_expr(code: R, mem: Mem) -> Any:
    print("* expr:")
    res = ()
    for k in code:
        res += execute(k, mem)
    return (res[-1],) if res else ()


def eval_main(code: R, mem: Mem) -> Any:
    res = ()
    for k in code:
        res += execute(k, mem),
        mem.clear_stack()
    return res


####################
# EXECUTE FUNCTION #
####################

def execute(code: R | ATO, mem: Mem) -> tuple[Any]:
    res = ()
    match code:
        case R():
            match code.type:
                case ASTType.PROGRAM:
                    pass

                case ASTType.MAIN:
                    res = eval_main(code, mem)

                case ASTType.EXPR:
                    res = eval_expr(code, mem)

                case ASTType.ARRAY:
                    res = eval_array(code, mem)

                case ASTType.CALL:
                    res = eval_call(code, mem)

                case ASTType.ARGS:
                    res = eval_args(code, mem)

                # TODO: separate in different cases?
                case ASTType.OPERATION | ASTType.Q_OPERATION | ASTType.ID | ASTType.BUILTIN:
                    res = eval_oper(code, mem)

        case ATO():
            res = eval_token(code, mem)
            res = res,
    return res
