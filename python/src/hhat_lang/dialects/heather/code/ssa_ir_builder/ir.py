from __future__ import annotations

from typing import Any, Iterable

from hhat_lang.core.data.core import CompositeSymbol, CoreLiteral, Symbol

# TODO: continue to implement this approach in the future


class SSACounter:
    _count: int

    def __init__(self):
        # count starts at -1 to align with list indexes
        self._count = -1

    def inc(self):
        self._count += 1
        return self._count

    def reset(self):
        """Use this mainly when testing code"""
        self._count = -1


class IRModifier:
    """
    Modifier generates some extra behaviors for the data it's applied on.

    Data can be a variable, a type, a function/instruction/operation, or
    anything that has a `Symbol` and can be manipulated at runtime.
    """

    _ssa: SSA
    _mods: dict[int | Symbol, Any] | dict

    def __init__(
        self, ssa: SSA, *, amods: tuple | None = None, kmods: dict | None = None
    ):
        self._ssa = ssa

        # check whether amods (mod arguments) is not empty:
        if amods:

            for n, p in enumerate(amods):
                if isinstance(p, (Symbol, CompositeSymbol, SSA)):
                    self._mods[n] = p

                else:
                    raise ValueError(f"unsupported mod for {self._ssa}: {p}")

        # check whether kmods (mod key-value pairs) is not empty instead:
        elif kmods:

            for k, v in kmods.items():
                if isinstance(k, Symbol) and isinstance(
                    v, (Symbol, CompositeSymbol, SSA, CoreLiteral)
                ):
                    self._mods[k] = v

                else:
                    raise ValueError(
                        f"unsupported mod and param for {self._ssa}: {k} -> {v}"
                    )

        # if nothing is provided, the mod is empty:
        else:
            # no modifier generated; empty data
            self._mods = dict()

    @property
    def ssa(self) -> SSA:
        return self._ssa

    @property
    def symbol(self) -> Symbol:
        return self._ssa.symbol

    @property
    def mods(self) -> dict[int | Symbol, Any] | dict:
        return self._mods

    def __repr__(self) -> str:
        mod_repr = (
            " ".join(f"{k}:{v}" for k, v in self._mods.items()) if self._mods else ""
        )
        return f"$mod({self.ssa})[{mod_repr}]"


class SSA:
    """
    SSA form data value.

    Contains the `Symbol` and the `SSACounter` index. Optionally, it will
    either have a `SSAPhi` or an `IRModifier`, but cannot have both.
    """

    _symbol: Symbol
    _idx: int | None
    _phi: SSAPhi | None
    _mod: IRModifier | None

    def __init__(self, value: Symbol):
        if isinstance(value, Symbol):
            self._phi = None
            self._symbol = value
            self._idx = None
            self._mod = None

        else:
            raise ValueError("SSA value must be a symbol.")

    @property
    def symbol(self) -> Symbol:
        return self._symbol

    @property
    def name(self) -> str:
        return self._symbol.value

    @property
    def idx(self) -> int | None:
        return self._idx

    @property
    def phi(self) -> None | SSAPhi:
        return self._phi

    @property
    def mod(self) -> None | IRModifier:
        return self._mod

    def set_idx(self, idx: int) -> None:
        if self.idx is None:
            self._idx = idx

    @classmethod
    def get_ssa(cls, value: Symbol | SSAPhi) -> SSA:
        """Get a new SSA from a Symbol or a SSAPhi."""

        if isinstance(value, SSAPhi):
            new_ssa = SSA(value.symbol)
            new_ssa.set_phi(value)
            return new_ssa

        return SSA(value)

    def set_phi(self, value: SSAPhi) -> None:
        if isinstance(value, SSAPhi):
            self._phi = value

        else:
            raise ValueError(f"{value} is not a Phi/SSAPhi ({type(value)}).")

    def set_mod(self, value: IRModifier) -> None:
        if isinstance(value, IRModifier):
            self._mod = value

        else:
            raise ValueError(f"{value} is not a modifier ({type(value)}).")

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SSA):
            return self._symbol == other._symbol and self._idx == other._idx
        return False

    def __hash__(self) -> int:
        return hash((self._symbol, self._idx))

    def __repr__(self) -> str:
        phi = f"<{self.phi}>" if self.phi else ""
        mod = f"<{self.mod}>" if self.mod else ""
        return f"%{self.name}#{self.idx}{phi or mod}"


class SSAPhi:
    """
    The phi function for disambiguity between a variable coming from a control flow.
    """

    _symbol: Symbol
    _args: tuple[SSA, ...]

    def __init__(self, *vars: SSA):
        if self._check_args(*vars):
            self._args = vars
            self._symbol = vars[0].symbol

        else:
            raise ValueError("SSAPhi must contain the same variables.")

    @property
    def symbol(self) -> Symbol:
        return self._symbol

    def _check_args(self, *args: SSA) -> bool:
        return len(set(k.name for k in args)) == 1

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SSAPhi):
            return self._symbol == other._symbol and self._args == other._args
        return False

    def __hash__(self) -> int:
        return hash((self._symbol, self._args))

    def __repr__(self) -> str:
        return f"ø({','.join(str(k) for k in self._args)})"


class IRVar:
    """
    Holds a list of all the SSA forms for a given variable. Each SSA form
    index matches the list index, so it's easy to compare, retrieve or do
    optimizations with it.
    """

    _symbol: Symbol
    _data: list[SSA] | list
    _ssa_counter: SSACounter

    def __init__(self, symbol: Symbol):
        self._symbol = symbol
        self._data = []
        self._ssa_counter = SSACounter()

    @property
    def symbol(self) -> Symbol:
        return self._symbol

    @property
    def data(self) -> list[SSA]:
        return self._data

    def ssa_inc(self) -> int:
        return self._ssa_counter.inc()

    def push(self, name: Symbol | SSA | SSAPhi | IRModifier) -> None:
        match name:
            case SSA():
                if self.symbol == name.symbol:
                    name.set_idx(self.ssa_inc())
                    self._data.append(name)
                    return

            case IRModifier():
                if self.symbol == name.symbol:
                    new_ssa = SSA.get_ssa(name.symbol)
                    new_ssa.set_idx(self.ssa_inc())
                    new_ssa.set_mod(name)
                    self._data.append(new_ssa)
                    return

            case SSAPhi():
                if self.symbol == name.symbol:
                    new_ssa = SSA.get_ssa(name)
                    new_ssa.set_idx(self.ssa_inc())
                    self._data.append(new_ssa)
                    return

            case Symbol():
                if self.symbol == name:
                    new_ssa = SSA.get_ssa(name)
                    new_ssa.set_idx(self.ssa_inc())
                    self._data.append(new_ssa)
                    return

            case _:
                raise ValueError(
                    f"IRVar only accepts Symbol, SSA, SSAPhi or IRModifier."
                    f" ({name} ({type(name)}))"
                )

        raise ValueError("IRVar cannot accept a different symbol (variable).")

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index: int) -> SSA:
        return self._data[index]

    def __iter__(self) -> Iterable:
        yield from self._data

    def __repr__(self) -> str:
        return f"var:{self.symbol}.{self._data}"
