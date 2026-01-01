from __future__ import annotations

from typing import Iterable

from hhat_lang.core.code.base import BaseIRInstr
from hhat_lang.core.code.ir_block import (
    IRBlock,
    IRBlockFlag,
)
from hhat_lang.core.data.core import (
    CompositeSymbol,
    Literal,
    LiteralArray,
    ObjArray,
    SimpleObj,
    Symbol,
)


class ArgsValuesBlock(IRBlock):
    _name = IRBlockFlag.ARGS_VALUES

    args: (
        tuple[
            Symbol,
            ...,
        ]
        | tuple
    )
    values: tuple[SimpleObj | ObjArray | IRBlock | BaseIRInstr, ...] | tuple

    def __init__(
        self,
        *args: tuple[
            Symbol | ModifierBlock,
            CompositeSymbol | Literal | LiteralArray | IRBlock | BaseIRInstr,
        ],
    ):
        self.args = ()
        self.values = ()

        for k in args:
            match k[0]:
                case Symbol():
                    self.args += (k[0],)

                case ModifierBlock():
                    self.args += (k[0],)

                case _:
                    raise ValueError(
                        "args values block's args must be symbol or modifier block "
                    )

            match k[1]:
                case (
                    Symbol()
                    | CompositeSymbol()
                    | Literal()
                    | LiteralArray()
                    | IRBlock()
                    | BaseIRInstr()
                ):
                    self.values += (k[1],)

                case _:
                    raise ValueError(
                        f"args values block's values must be symbol, literal, ir block or ir instr {k[1]} {type(k[1])}"
                    )

    def __iter__(self) -> Iterable:
        return iter(zip(self.args, self.values))

    def __repr__(self) -> str:
        return f"ARG-VALUE#[{' '.join(f'{a}:{v}' for a, v in zip(self.args, self.values))}]"


class BodyBlock(IRBlock):
    _name = IRBlockFlag.BODY

    def __init__(self, *args: IRBlock | BaseIRInstr):
        if all(isinstance(k, IRBlock | BaseIRInstr) for k in args):
            if len(args) == 1 and isinstance(args[0], BodyBlock):
                self.args = args[0].args

            else:
                self.args = args

        else:
            raise ValueError(
                f"args must be block or instruction, but got {tuple(type(k) for k in args)}"
            )

    def __repr__(self) -> str:
        return "\n".join(str(k) for k in self.args)


class ReturnBlock(IRBlock):
    _name = IRBlockFlag.RETURN

    args: tuple[SimpleObj | ObjArray | IRBlock | BaseIRInstr, ...]

    def __init__(self, *args: SimpleObj | ObjArray | IRBlock | BaseIRInstr):
        if all(
            isinstance(k, SimpleObj | ObjArray | IRBlock | BaseIRInstr) for k in args
        ):
            self.args = args

        else:
            raise ValueError("return block got wrong object types")

    def __repr__(self) -> str:
        return f"RETURN#[{' '.join(str(k) for k in self.args)}]"


class ModifierBlock(IRBlock):
    _name = IRBlockFlag.MODIFIER

    args: tuple[Symbol | CompositeSymbol | BaseIRInstr, ModifierArgsBlock]

    def __init__(
        self, obj: Symbol | CompositeSymbol | BaseIRInstr, args: ModifierArgsBlock
    ):
        if isinstance(obj, Symbol | CompositeSymbol | BaseIRInstr) and isinstance(
            args, ModifierArgsBlock
        ):
            self.args = (obj, args)

        else:
            raise ValueError(
                f"modifier block cannot have types {type(obj)} and {type(args)}"
            )

    @property
    def obj(self) -> Symbol | CompositeSymbol | BaseIRInstr:
        return self.args[0]

    @property
    def mods(self) -> ModifierArgsBlock:
        return self.args[1]

    def __repr__(self) -> str:
        return f"{self.obj}<{self.mods}>"


class ModifierArgsBlock(IRBlock):
    _name = IRBlockFlag.MODIFIER_ARGS

    args: tuple[Symbol | CompositeSymbol, ...] | ArgsValuesBlock | ArgsBlock  # type: ignore [assignment]

    def __init__(
        self, args: tuple[Symbol | CompositeSymbol, ...] | ArgsValuesBlock | ArgsBlock
    ):
        if isinstance(args, ArgsValuesBlock | ArgsBlock) or all(
            isinstance(k, Symbol | CompositeSymbol) for k in args
        ):
            self.args = args

        else:
            raise ValueError(
                f"modifier args must be made of ArgsValuesBlock elements, "
                f"not {[type(k) for k in args]}"
            )

    def __repr__(self) -> str:
        return " ".join(str(k) for k in self.args)


class ArgsBlock(IRBlock):
    _name = IRBlockFlag.ARGS

    args: (
        tuple[SimpleObj | ObjArray | ArgsValuesBlock | IRBlock | BaseIRInstr, ...]
        | tuple
    )

    def __init__(
        self, *args: SimpleObj | ObjArray | ArgsValuesBlock | IRBlock | BaseIRInstr
    ):
        if all(
            isinstance(k, SimpleObj | ObjArray | IRBlock | BaseIRInstr) for k in args
        ):
            self.args = args

        else:
            raise ValueError(
                f"args must be block or instruction, but got {tuple(type(k) for k in args)}"
            )

    def __repr__(self) -> str:
        return " ".join(str(k) for k in self.args)


class OptionBlock(IRBlock):
    _name = IRBlockFlag.OPTION

    args: (  # type: ignore [assignment]
        tuple[
            tuple[SimpleObj | ObjArray | IRBlock | BaseIRInstr, ...],
            IRBlock | BaseIRInstr,
        ]
        | tuple
    )

    def __init__(
        self,
        option: SimpleObj | ObjArray | IRBlock | BaseIRInstr,
        block: IRBlock | BaseIRInstr,
    ):
        if isinstance(
            option, SimpleObj | ObjArray | IRBlock | BaseIRInstr
        ) and isinstance(block, SimpleObj | ObjArray | IRBlock | BaseIRInstr):
            self.args = (option, block)

        else:
            raise ValueError(
                f"option ({type(option)}) or block ({type(block)}) is of wrong type."
            )

    @property
    def option(self) -> SimpleObj | ObjArray | IRBlock | BaseIRInstr:
        return self.args[0]

    @property
    def block(self) -> SimpleObj | ObjArray | IRBlock | BaseIRInstr:
        return self.args[1]

    def __repr__(self) -> str:
        return f"OPTION#[{self.args[0]}:{self.args[1]}]"
