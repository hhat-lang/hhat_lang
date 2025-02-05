from __future__ import annotations

from typing import Any

from hhat_lang.core.memory.utils import Scope
from hhat_lang.core.type_system import FullName, NameSpace
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


class Evaluate:
    ir_code: IR
    main: IRMain
    ref: IRHeader
    mem: MemoryManager
    cur_scope: str

    def __init__(self, ir_code: IR):
        self.ir_code = ir_code
        self.main = ir_code.data.main
        self.ref = ir_code.data.header
        self.mem = MemoryManager()
        self.cur_scope = "main"

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
        # get var type as str
        _var_type = code.nodes[0].value
        # get var name as str
        _var_name = code.nodes[1].value
        # walk to evaluate code.nodes[2] and put it into the memory stack (self.mem.stack)
        self._walk(code.nodes[2])
        # retrieve the result from walking in the memory stack
        _var_assign = self.mem.stack.get(block=False)
        # allocated var data into heap
        self.mem.heap.add(Scope(self.cur_scope), _var_name, _var_assign)
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
        # resolve args
        print(f"  --> args? {code.nodes[1]}")
        self._code_args(code.nodes[1])

        len_args = len(code.nodes[1].nodes)
        print(f" => mem stack: {len(self.mem.stack.queue)}")
        _args = [self.mem.stack.get(block=False) for k in range(len_args)]
        # call _caller with _args arguments
        _caller(mem=self.mem, args=_args)
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
