from __future__ import annotations

from typing import Any

from hhat_lang.core.interpreter.base import BaseEvaluate
from hhat_lang.core.memory.utils import Scope
from hhat_lang.core.type_system import FullName, NameSpace
from hhat_lang.core.type_system.base import Appendable, Mutable
from hhat_lang.dialects.heather.syntax.ast import (
    Body,
    Declare,
    Assign,
    DeclareAssign,
    CallWithBody,
    Call,
    Args,
)
from hhat_lang.dialects.heather.syntax.base import Node, Terminal, AST, Symbol, Literal
from hhat_lang.dialects.heather.ir.ast_to_ir import IR, IRMain, IRHeader
from hhat_lang.core.memory.manager import MemoryManager


def debug(*msg: Any, **options: Any) -> None:
    print("[DEBUG]", *msg, **options)


class Evaluate(BaseEvaluate):
    ir_code: IR
    main: IRMain
    ref: IRHeader
    mem: MemoryManager
    cur_scope: Scope

    def __init__(self, ir_code: IR):
        self.ir_code = ir_code
        self.main = ir_code.data.main
        self.ref = ir_code.data.header
        self.mem = MemoryManager()
        self.cur_scope = Scope("main")

    def run(self):
        self._walk(code=self.ir_code.data.main)

    def _walk(self, code: AST | Node | Terminal | IRMain) -> Any:
        print(f"({type(code)}) {code}")
        match code:
            case Body():
                self._code_body(code)

            case Declare():
                self._code_declare(code)

            case Assign():
                self._code_assign(code)

            case DeclareAssign():
                self._code_declareassign(code)

            case Call():
                self._code_call(code)

            case CallWithBody():
                self._code_callwithbody(code)

            case Args():
                self._code_args(code)

            case Terminal() | Symbol() | Literal():
                self._walk_terminal(code)

            case IRMain():
                self._walk(code.data)

            case _:
                raise NotImplementedError(f"({code}) '{code.value}' not implemented yet")

    def _walk_terminal(self, code: Terminal) -> Any:
        match code:
            case Literal():
                _data = code.value
            case Symbol():
                _data = FullName(NameSpace(), code.value)
            case _:
                _data = code

        print(f" --> terminal into stack: {code} ({type(code)})")
        self.mem.stack.put(_data, block=False)
        print(f"   -> mem stack: {self.mem.stack.queue}")
        # debug(f"got terminal? ({type(code)}) {code}")

    #############
    # CODE EVAL #
    #############

    def _code_body(self, code: Node) -> Any:
        for expr in code:
            self._walk(expr)

    def _code_declare(self, code: Node) -> Any:
        raise NotImplementedError("Declare not implemented")

    def _code_assign(self, code: Node) -> Any:
        raise NotImplementedError("Assign not implemented")

    def _code_declareassign(self, code: Node):
        # get var type as FullName
        _var_type = FullName(NameSpace(), code.nodes[0].value)
        # get var name as FullName
        _var_name = FullName(NameSpace(), code.nodes[1].value)

        if _var_name in self.mem.heap[self.cur_scope]:
            raise ValueError(f"variable {_var_name} already declared")

        # walk to evaluate code.nodes[2] and put it into the memory stack (self.mem.stack)
        self._walk(code.nodes[2])
        # retrieve the result from walking in the memory stack
        _var_assign = self.mem.stack.get(block=False)

        # depending on the type and the value to be assigned, get a different base container
        if _var_type.name.startswith("@"):
            _var_container = Appendable(name=_var_name, var_type=_var_type, size=None)

        else:
            _len_var_data = len(_var_assign)
            if _len_var_data == 1:
                _var_container = Mutable(name=_var_name, var_type=_var_type, size=1)

            else:
                _var_container = Appendable(name=_var_name, var_type=_var_type, size=None)

        # allocated var data into heap
        self.mem.heap.add(self.cur_scope, _var_name, _var_container)
        print(f"  ?-> what is in stack: {self.mem.stack.queue}")
        print(f"  ?-> what is in heap: {self.mem.heap}")

        if len(code.nodes) > 3:
            raise ValueError(
                f"unknown DeclareAssign behavior, {len(code.nodes)} args: {code.nodes[3:]}"
            )

    def _code_call(self, code: Node):
        debug(f"calling {code}")
        # assure there is only the caller and the args, or only a caller (to be decided)
        assert len(code.nodes) == 2 or len(code.nodes) == 1

        # get caller name (str) transformed as FullName; for now namespace is local
        print(f" --> caller name {code.nodes[0]}")
        self._walk(code.nodes[0])
        _caller_name = self.mem.stack.get(block=False)
        # find the caller in function code reference
        _caller = self.ref.data.fn_ref.get(_caller_name)
        _prev_scope = self.cur_scope
        # resolve args
        print(f"  --> args? {code.nodes[1]}")
        self._code_args(code.nodes[1])

        len_args = len(code.nodes[1].nodes)
        print(f" => mem stack: {len(self.mem.stack.queue)}")
        _args = [self.mem.stack.get(block=False) for k in range(len_args)]
        # define a function scope
        self.cur_scope = Scope(_caller_name.value)
        # call _caller with _args arguments; it will place return data into the stack
        _caller(mem=self.mem, args=_args, eval=self)
        # get back the previous scope
        self.cur_scope = _prev_scope
        print(f"  -> after call done, stack: {self.mem.stack.queue}")

    def _code_callwithbody(self, code: Node):
        raise NotImplementedError("CallWithBody not implemented")

    def _code_args(self, code: AST | Node | Terminal):
        # len_args = len(code.nodes)
        args_list = []
        for arg in code.nodes:
            print(f" --> code arg: {arg}")
            self._walk(arg)
            # args_list.append(self.mem.stack.get(block=False))

    #####################
    # MEMORY MANAGEMENT #
    #####################

    # ----
    # HEAP
    # ----

    def _heap_alloc(self):
        pass

    def _heap_free(self):
        pass

    # -----
    # STACK
    # -----

    def _stack_put(self):
        pass

    def _stack_pop(self):
        pass
