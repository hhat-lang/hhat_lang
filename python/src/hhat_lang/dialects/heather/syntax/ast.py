from __future__ import annotations

from typing import Any, Union

from .base import AST, Node, Terminal, Symbol, CSymbol, QSymbol
from hhat_lang.core.utils.dialect_descriptor import DialectDescriptor


class GenericTypeDef(Node):
    def __init__(self, name: Terminal, generic: list[AST], elems: list[AST], dialect: DialectDescriptor):
        super().__init__(".generic-typedef", [name, generic, elems], dialect)

    # def __repr__(self) -> str:
    #     text = f"{self.__class__.__name__}"
    #     text += _print_nodes(self.nodes, 1)
    #     text += "\n"
    #     return text


class GenericCall(Node):
    def __init__(self, generic_type: GenericArgs, name: Terminal, args: Args, dialect: DialectDescriptor):
        super().__init__(".generic-call", [generic_type, name, args], dialect)


class GenericTypeCall(Node):
    def __init__(self, args: GenericArgs | list[AST], dialect: DialectDescriptor):
        super().__init__(".generic-typecall", args, dialect)


class GenericArgs(Node):
    def __init__(self, args: list[AST], dialect: DialectDescriptor):
        super().__init__(".generic-args", args, dialect)


class GenericFunctionDef(Node):
    def __init__(
        self,
        fn_type: Terminal,
        name: Terminal,
        generic: GenericArgs,
        args: Args,
        body: Body,
        dialect: DialectDescriptor,
    ):
        super().__init__(".generic-fndef", [fn_type, name, generic, args, body], dialect)

    # def __repr__(self) -> str:
    #     text = f"{self.__class__.__name__}"
    #     text += _print_nodes(self.nodes, 1)
    #     text += "\n"
    #     return text


class Struct(Node):
    def __init__(self, *elems: Any, dialect: DialectDescriptor | None = None):
        if dialect is not None:
            super().__init__(".struct", list(elems), dialect)
        else:
            raise ValueError("dialect must be specified")


class Enum(Node):
    def __init__(self, elems: Any, dialect: DialectDescriptor | None = None):
        if dialect is not None:
            super().__init__(".enum", elems, dialect)
        else:
            raise ValueError("dialect must be specified")


class EnumsStruct(Node):
    def __init__(self, name: Terminal, body: Struct, dialect: DialectDescriptor):
        if isinstance(body, Struct):
            super().__init__(".enums-struct", [name, body], dialect)
        else:
            raise ValueError("body must be a Struct")


class Member(Node):
    def __init__(self, elem: list[AST], dialect: DialectDescriptor):
        super().__init__(".elem", elem, dialect)


class PropId(Node):
    def __init__(self, *ids: Any, dialect: DialectDescriptor | None = None):
        if dialect is not None:
            super().__init__(".propid", list(ids), dialect)
        else:
            raise ValueError("dialect must be specified")


class Declare(Node):
    def __init__(self, var_type: Symbol, var: Symbol, dialect: DialectDescriptor):
        super().__init__(".declare", [var_type, var], dialect)


class Assign(Node):
    def __init__(self, var: Symbol, value: AST, dialect: DialectDescriptor):
        super().__init__(".assign", [var, value], dialect)


class DeclareAssign(Node):
    def __init__(self, var_type: Symbol, var: Symbol, value: AST, dialect: DialectDescriptor):
        super().__init__(".declare-assign", [var_type, var, value], dialect)


class Call(Node):
    def __init__(self, name: Terminal, args: Args, dialect: DialectDescriptor, **kwargs: Any):
        """
        `kwargs` can be some extra arguments for custom h-hat interpreters
        """
        if kwargs:
            super().__init__(".call", [name, args, list(kwargs.values())], dialect)
        else:
            super().__init__(".call", [name, args], dialect)


class CallWithBody(Node):
    def __init__(self, name: Terminal, *group: Any, dialect: DialectDescriptor | None = None, **kwargs: Any):
        if dialect is not None:
            if kwargs:
                super().__init__(".call-with-body", [name, *group, list(kwargs.values())], dialect)
            else:
                super().__init__(".call-with-body", [name, *group], dialect)
        else:
            raise ValueError("dialect must be specified")


class Group(Node):
    def __init__(self, elem: list[Head | Body], dialect: DialectDescriptor):
        super().__init__(".group", elem, dialect)


class Expr(Node):
    def __init__(self, expr: AST, dialect: DialectDescriptor):
        super().__init__(".expr", expr, dialect)


class Main(Node):
    def __init__(self, nodes: list[AST], dialect: DialectDescriptor):
        super().__init__(".main", nodes, dialect)


class Body(Node):
    def __init__(self, body: list[AST], dialect: DialectDescriptor):
        super().__init__(".body", body, dialect)


class Head(Node):
    def __init__(self, elems: list[AST], dialect: DialectDescriptor):
        super().__init__(".head", elems, dialect)


class Args(Node):
    def __init__(self, args: list[AST], dialect: DialectDescriptor):
        super().__init__(".args", args, dialect)

    def get_args_types(self) -> AST:
        return ArgsTypes(list(t for _, t in self.nodes), self.dialect)

    def get_args_types_str(self) -> tuple[Union[Terminal, Node], ...]:
        return tuple(t for _, t in self.nodes)


class ArgsTypes(Node):
    def __init__(self, args: list[AST], dialect: DialectDescriptor):
        super().__init__(".args-types", args, dialect)


class FunctionDef(Node):
    def __init__(
        self,
        fn_type: Terminal,
        name: Terminal,
        args: Args,
        body: Body,
        dialect: DialectDescriptor,
    ):
        super().__init__(".fndef", [fn_type, name, args, body], dialect)


class TypeDef(Node):
    def __init__(self, name: Terminal, elems: list[AST], dialect: DialectDescriptor):
        super().__init__(".typedef", [name, elems], dialect)

    # def __repr__(self) -> str:
    #     text = f"{self.__class__.__name__}"
    #     text += _print_nodes(self.nodes, 1)
    #     text += "\n"
    #     return text


class Import(Node):
    def __init__(self, elems: list[AST], dialect: DialectDescriptor):
        super().__init__(".import", elems, dialect)


class Program(Node):
    def __init__(self, body: list[AST], dialect: DialectDescriptor):
        super().__init__(".program", body, dialect)

    def __repr__(self) -> str:
        text = f"{self.__class__.__name__}<{self.dialect}>\n  "
        text += "\n  ".join(str(k) for k in self.nodes)
        text += f"end#{self.__class__.__name__}<{self.dialect}>\n"
        return text


def _print_nodes(code: list | AST, s: int = 0) -> str:
    text = ""
    match code:
        case list():
            text += " "*(2*s) + " ".join(_print_nodes(k, s+1) for k in code)

        case Enum():
            text += f"{code.value}\n" + " "*(2*s)
            if len(code.nodes) > 0:
                text += f"\n{' '*(2*s)}".join(_print_nodes(k, s+1) for k in code.nodes)
            else:
                text += "[Empty]"

        case EnumsStruct():
            text += f"".join(_print_nodes(k, s) for k in code.nodes)

        case Struct():
            text += f"{code.value}\n" + " "*(2*s)
            if len(code.nodes) > 0:
                text += f"\n{' '*(2*s)}".join(_print_nodes(k, s + 1) for k in code.nodes)
            else:
                text += "[Empty]"

        case GenericArgs():
            text += f"GenericArgs [("
            text += ") (".join(_print_nodes(k) for k in code.nodes)
            text += ")]"

        case Member():
            text += f"Symbol {code.nodes[0]} : Type {code.nodes[1]}"

        case GenericFunctionDef():
            gen_args = f" ".join(_print_nodes(k, 0) for k in code.nodes[2])
            args = " ".join(_print_nodes(k, 0) for k in code.nodes[3])
            text += f"1{_print_nodes(code.nodes[1], 0)} {gen_args} {args} 2Type {_print_nodes(code.nodes[0], 0)}\n" + " "*(2*s)
            text += f"{' '*(2*s)}".join(_print_nodes(k, s+1) for k in code.nodes[4])

        case Args():
            text += "Args [("
            text += ") (".join(_print_nodes(k, 0) for k in code.nodes)
            text += ")]"

        case Body():
            text += "\n" + " "*(2*s) + f"{code.value}\n" + " "*(2*(s+1))
            if len(code.nodes) > 0:
                text += f"\n{' '*(2*s)}".join(_print_nodes(k, s+1) for k in code.nodes)
            else:
                text += "[Empty]"

        case CSymbol() | QSymbol():
            text += f"{code}"

        case Terminal():
            text += f"%%{_print_nodes(code.value, 0)}"

        case _:
            text += " "*(2*s) + f"*{type(code)}{code}"

    return text
