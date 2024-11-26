from __future__ import annotations

from abc import ABC

from hhat_lang.core.type_system import FullName


class BaseFunctionData(ABC):
    """
    To be used as a holder of function name (FullName),
    args (BaseFunctionArgs class) and body (BaseFunctionBody class).
    """

    _name: FullName
    _type: FullName
    _args: BaseFunctionArgs
    _body: BaseFunctionBody


class BaseFunctionArgs(ABC):
    """
    To be used as a holder of function arguments.
    """

    pass


class BaseFunctionBody(ABC):
    """
    To be used as a holder of function body.
    """

    pass
