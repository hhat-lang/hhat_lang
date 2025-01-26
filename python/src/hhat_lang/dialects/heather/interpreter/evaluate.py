from __future__ import annotations

from typing import Any

from hhat_lang.core.type_system import FullName, NameSpace
from hhat_lang.dialects.heather.syntax.ast import (
    Declare,
    Assign,
    DeclareAssign,
    CallWithBody,
    Call,
    Args,
)
from hhat_lang.dialects.heather.syntax.base import Node, Terminal, AST
from hhat_lang.dialects.heather.ir.ast_to_ir import IR, IRMain, IRHeader
from hhat_lang.core.memory.manager import MemoryManager


def debug(*msg: Any, **options: Any) -> None:
    print("[DEBUG]", *msg, **options)


class Evaluate:
    ir_code: IR
    main: IRMain
    ref: IRHeader
    mem: MemoryManager

    def __init__(self, ir_code: IR):
        self.ir_code = ir_code
        self.main = ir_code.data.main
        self.ref = ir_code.data.header
        self.mem = MemoryManager()

    def run(self):
        self._walk(code=self.ir_code.data.main)

    def _walk(self, code: AST | Node | Terminal | IRMain) -> Any:
        match code:
            case Node():
                for expr in code:
                    match expr:
                        case Declare():
                            self._code_declare(expr)

                        case Assign():
                            self._code_assign(expr)

                        case DeclareAssign():
                            self._code_declareassign(expr)

                        case Call():
                            self._code_call(expr)

                        case CallWithBody():
                            self._code_callwithbody(expr)

                        case Args():
                            self._code_args(expr)

            case Terminal():
                _fullname = FullName(NameSpace(), code.value)
                self.mem.stack.put(_fullname)
                # debug(f"got terminal? ({type(code)}) {code}")

            case IRMain():
                self._walk(code.data)

    #############
    # CODE EVAL #
    #############

    def _code_declare(self, code: Node):
        raise NotImplementedError("Declare not implemented")

    def _code_assign(self, code: Node):
        raise NotImplementedError("Assign not implemented")

    def _code_declareassign(self, code: Node):
        # get var type as str
        _var_type = code.nodes[0].value
        # get var name as str
        _var_name = code.nodes[1].value
        # walk to evaluate code.nodes[2] and put it into the memory stack (self.mem.stack)
        self._walk(code.nodes[2])
        # retrieve the result from walking in the memory stack
        _var_assign = self.mem.stack.get()

        if len(code.nodes) > 3:
            raise ValueError(
                f"unknown DeclareAssign behavior, {len(code.nodes)} args: {code.nodes[3:]}"
            )

    def _code_call(self, code: Node):
        # assure there is only the caller and the args, or only a caller (to be decided)
        assert len(code.nodes) == 2 or len(code.nodes) == 1

        # get caller name (str) transformed as FullName; for now namespace is local
        self._walk(code.nodes[0])
        _caller_name = self.mem.stack.get()
        # find the caller in function code reference
        _caller = self.ref.data.fn_ref.get(_caller_name)
        # resolve args
        self._code_args(code.nodes[1])

        len_args = len(code.nodes[1].nodes)
        _args = [self.mem.stack.get() for k in range(len_args)]
        # call _caller with _args arguments
        _caller

    def _code_callwithbody(self, code: Node):
        raise NotImplementedError("CallWithBody not implemented")

    def _code_args(self, code: AST | Node | Terminal):
        # len_args = len(code.nodes)
        args_list = []
        for arg in code.nodes:
            self._walk(arg)
            args_list.append(self.mem.stack.get())

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
