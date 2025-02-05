"""
Had to slightly change the way it will work to account for simple example.

The way it should work is: types are always in separated files in a 'types' folder.
Functions also are in separated files from the `main` closure.

For the sake of showing code, it works like: types and functions are in the same file
as the `main` closure. One the code is working and running, the above will be built.
"""

from __future__ import annotations

from typing import Any, Iterable
from importlib import import_module

from hhat_lang.core.fn_system.base import BaseFunctionData
from hhat_lang.core.type_system import FullName, NameSpace, DataTypesEnum
from hhat_lang.core.memory.code_manager import CodeManager, CodeReference
from hhat_lang.core.type_system.base import BaseDataType, BaseMember
from hhat_lang.core.type_system.datatypes import (
    StructType,
    UnionType,
    EnumType,
    SingleType,
    TypedMember,
    MemberType,
)
from hhat_lang.dialect_builder.builtins.types import datatypes_dict

from hhat_lang.dialects.heather.core.functions import FunctionData
from hhat_lang.dialects.heather.syntax.base import (
    AST,
    Node as ASTNode,
    Terminal as ASTTerminal,
    QSymbol,
    CSymbol,
    Symbol,
)
from hhat_lang.dialects.heather.syntax.ast import (
    Program as ASTProgram,
    Main as ASTMain,
    Body as ASTBody,
    TypeDef as ASTTypeDef,
    GenericTypeDef as ASTGenericTypeDef,
    FunctionDef as ASTFunctionDef,
    GenericFunctionDef as ASTGenericFunctionDef,
    Enum as ASTEnum,
    Struct as ASTStruct,
    EnumsStruct as ASTEnumsStruct,
    Member as ASTMember,
    Args as ASTArgs,
    Call as ASTCall, DeclareAssign, Declare,
)
from hhat_lang.dialects.heather.builtins import functions


class IR:
    parsed_code: ASTProgram
    data: IRData

    def __init__(self):
        pass

    @classmethod
    def load_ast(cls, parsed_code: ASTProgram) -> IR:
        assert isinstance(parsed_code, ASTProgram)
        ir = IR()
        ir.parsed_code = parsed_code
        ir.data = IRData()
        ir.data.header = IRHeader()
        return ir

    def build_ir(self) -> IR:
        for block in self.parsed_code:
            match block:
                case ASTMain():
                    self.data.main = block.nodes[0]

                case ASTTypeDef() | ASTGenericTypeDef():
                    self.data.header.build_type(block)
                    self.data.get_refs(block)

                case ASTFunctionDef() | ASTGenericFunctionDef():
                    self.data.header.build_fns(block)
                    self.data.get_refs(block)

                case _:
                    pass

        self.data.build_refs()
        return self

    def __repr__(self) -> str:
        _header = f"{self.data.header.data}"
        _main = f"{self.data.main}"
        text = "\n[IR]\n*HEADER\n"
        text += "=" * 80
        text += f"\n{_header}\n"
        text += "*MAIN\n"
        text += "=" * 80
        text += f"\n{_main}\n\n"
        text += "*=" * 40
        return text


class IRData:
    # TODO: refactor it afterward to include imports
    header: IRHeader
    main: IRMain

    def build_refs(self) -> None:
        for expr in self.main:
            self.get_refs(expr)

    def get_refs(self, expr: ASTNode | ASTTerminal):
        match expr:
            case ASTCall():
                caller = expr.nodes[0]

                if isinstance(caller, QSymbol):
                    fullname = FullName(NameSpace(), caller.value)
                    caller_fn = getattr(functions, caller.value.replace("@", "fn_q__"))

                elif isinstance(caller, CSymbol):
                    fullname = FullName(NameSpace(), caller.value)
                    caller_fn = getattr(functions, "fn_" + caller.value)

                else:
                    raise NotImplementedError(f"'{caller}' ({type(caller)}) is not implemented")

                self.header.data.fn_ref.add(fullname, caller_fn)

            case ASTTerminal():
                pass

            case DeclareAssign() | Declare():
                type_fn = self._add_type_ref(expr.nodes[0])
                self.header.data.type_ref.add(type_fn.name, type_fn)
                self.get_refs(expr.nodes[2])

            case ASTFunctionDef():
                type_fn = self._add_type_ref(expr.nodes[0])
                self.header.data.type_ref.add(type_fn.name, type_fn)
                self.get_refs(expr.nodes[1:])

            case ASTMember():
                type_fn = self._add_type_ref(expr.nodes[1])
                self.header.data.type_ref.add(type_fn.name, type_fn)

            case _:
                for k in expr:
                    self.get_refs(k)

    def _add_type_ref(self, type_name: Symbol) -> Any:
        type_fn = datatypes_dict.get(type_name.value, None)

        if type_fn is None:
            raise NotImplementedError(f"'{type_name}' is not implemented yet")

        return type_fn


class IRHeader:
    data: CodeManager

    def __init__(self):
        self.data = CodeManager()

    def build_type(self, ast_data: ASTTypeDef | ASTGenericTypeDef) -> None:
        IRTypes.build(ast_data, self.data.type_ref)

    def build_fns(self, ast_data: ASTFunctionDef | ASTGenericFunctionDef) -> None:
        IRFns.build(ast_data, self.data.fn_ref)


class IRTypes:
    @classmethod
    def build(
        cls,
        pcode: ASTTypeDef | ASTGenericTypeDef,
        type_ref: CodeReference[BaseDataType]
    ) -> None:
        name = pcode.nodes[0]
        assert isinstance(name, ASTTerminal)
        elems = pcode.nodes[1:]
        ns = NameSpace()  # work out on it when the types are located elsewhere
        fullname = FullName(ns, name.value)

        if fullname in type_ref:
            raise ValueError(f"type '{fullname}' already defined")

        for elem in elems:
            match elem:
                case ASTEnum():
                    datatype = EnumType(name=fullname, datatype=DataTypesEnum.ENUM)
                    cls._build_enum(elem, datatype)

                case ASTStruct():
                    datatype = StructType(name=fullname, datatype=DataTypesEnum.STRUCT)
                    cls._build_struct(elem, datatype)

                case ASTMember():
                    datatype = None
                    cls._build_member(elem)

                case ASTEnumsStruct():
                    datatype = None

                case _:
                    print(f"|build type| what has it? ({type(elem)}) {elem}")
                    datatype = None

            print(f"{datatype=}") if datatype is not None else print("", end="")
            type_ref.add(fullname, datatype)

    @classmethod
    def _build_enumsstruct(cls, pcode: ASTEnumsStruct, datatype: BaseDataType) -> None:
        # print(f"enumsstruct={pcode}")
        member_name = pcode.nodes[0].value
        member_fullname = FullName(NameSpace(), member_name)
        member_datatype = StructType(name=member_fullname, datatype=DataTypesEnum.STRUCT)

        for member in pcode[1:]:
            # print(f"  -> {member=}")
            match member:
                case ASTStruct():
                    cls._build_struct(member, member_datatype)
                case _:
                    print(f"|enumsstruct| what has it? ({type(member)}) {member}")
            datatype.add_member(member_datatype)

    @classmethod
    def _build_struct(cls, pcode: ASTStruct | ASTEnumsStruct, datatype: BaseDataType) -> None:
        # print(f"struct={pcode}")

        for member in pcode:
            # print(f"  -> {member=}")
            match member:
                case ASTMember():
                    datatype.add_member(cls._build_member(member))
                case _:
                    print(f"|struct| what has it? ({type(member)}) {member}")

    @classmethod
    def _build_enum(cls, pcode: ASTEnum, datatype: BaseDataType) -> None:
        # print(f"enum={pcode}")
        for member in pcode:
            # print(f"  -> {member=}")
            match member:
                case ASTEnumsStruct():
                    cls._build_enumsstruct(member, datatype)
                case ASTStruct():
                    cls._build_struct(member, datatype)
                case ASTMember():
                    datatype.add_member(cls._build_member(member))
                case _:
                    print(f"|enum| what has it? ({type(member)}) {member}")

    @classmethod
    def _build_union(cls, pcode: AST):
        pass

    @classmethod
    def _build_member(cls, member: list[AST]) -> BaseMember:
        return TypedMember(
            datatype=DataTypesEnum.TYPED_MEMBER,
            name=member[0].value,
            member_type=FullName(NameSpace(), member[1].value)
        )

    @classmethod
    def _build_single(cls, pcode: AST):
        pass


class IRFns:
    @classmethod
    def build(
        cls,
        pcode: ASTFunctionDef | ASTGenericFunctionDef,
        fn_ref: CodeReference[BaseFunctionData],
    ) -> None:
        # namespace local for now
        # get function type
        _fn_type = FullName(NameSpace(), pcode.nodes[0].value)
        # get function name
        _fn_name = FullName(NameSpace(), pcode.nodes[1].value)

        fn_data = FunctionData()
        fn_data.add_name(_fn_name)
        fn_data.add_type(_fn_type)
        fn_data.add_args(*pcode.nodes[2].nodes)
        fn_data.add_body(pcode.nodes[3])

        fn_ref.add(_fn_name, fn_data)


class IRPragmas:
    # TODO: implement it in the future
    pass


class IRMain:
    data: ASTBody

    def __init__(self, data: ASTBody):
        self.data = data

    def __iter__(self) -> Iterable:
        yield from self.data

    def __repr__(self) -> str:
        return f"MAIN:\n{self.data}\n"
