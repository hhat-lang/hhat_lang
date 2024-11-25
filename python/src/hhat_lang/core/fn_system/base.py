from __future__ import annotations

from abc import ABC


class BaseFunctionData(ABC):
    """
    To be used as a holder of function name (FullName),
    args (BaseFunctionArgs class) and body (BaseFunctionBody class).
    """

    pass


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
