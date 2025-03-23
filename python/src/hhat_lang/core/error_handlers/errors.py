from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto


class ErrorCodes(Enum):
    INDEX_UNKNOWN_ERROR = auto()
    INDEX_ALLOC_ERROR = auto()
    INDEX_VAR_HAS_INDEXES_ERROR = auto()

    TYPE_SINGLE_ASSIGN_ERROR = auto()
    TYPE_STRUCT_ASSIGN_ERROR = auto()
    TYPE_UNION_ASSIGN_ERROR = auto()
    TYPE_ENUM_ASSIGN_ERROR = auto()

    CONTAINER_VAR_ASSIGN_ERROR = auto()
    CONTAINER_VAR_IS_IMMUTABLE_ERROR = auto()

    VARIABLE_WRONG_MEMBER_ERROR = auto()


class ErrorHandler(ABC):
    def __init__(self, error_code: ErrorCodes):
        self.err_code = error_code

    @property
    def error_code(self) -> ErrorCodes:
        return self.err_code

    @abstractmethod
    def __call__(self) -> str:
        ...


class IndexUnknownError(ErrorHandler):
    def __init__(self):
        super().__init__(ErrorCodes.INDEX_UNKNOWN_ERROR)

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Unknown error."


class IndexAllocationError(ErrorHandler):
    def __init__(self, requested_idxs: int, max_idxs: int):
        self._req_idxs = requested_idxs
        self._max_idxs = max_idxs
        super().__init__(ErrorCodes.INDEX_ALLOC_ERROR)

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Requested {self._req_idxs},"
            f" but maximum is {self._max_idxs}"
        )


class IndexVarHasIndexesError(ErrorHandler):
    def __init__(self, var_name: str):
        self._var = var_name
        super().__init__(ErrorCodes.INDEX_VAR_HAS_INDEXES_ERROR)

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Var '{self._var}' already has indexes."


class TypeSingleError(ErrorHandler):
    def __init__(self, type_name: str):
        super().__init__(ErrorCodes.TYPE_SINGLE_ASSIGN_ERROR)
        self._type_name = type_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Type '{self._type_name}'"
            f" cannot contain more than one member."
        )


class TypeStructError(ErrorHandler):
    def __init__(self, type_name: str):
        super().__init__(ErrorCodes.TYPE_STRUCT_ASSIGN_ERROR)
        self._type_name = type_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Attempting to add wrong member"
            f" types to type '{self._type_name}'."
        )


class TypeUnionError(ErrorHandler):
    def __init__(self, type_name: str):
        super().__init__(ErrorCodes.TYPE_UNION_ASSIGN_ERROR)
        self._type_name = type_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Attempting to add wrong member"
            f" types to type '{self._type_name}'."
        )


class TypeEnumError(ErrorHandler):
    def __init__(self, type_name: str):
        super().__init__(ErrorCodes.TYPE_ENUM_ASSIGN_ERROR)
        self._type_name = type_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Attempting to add wrong member"
            f" types to type '{self._type_name}'."
        )


class ContainerVarError(ErrorHandler):
    def __init__(self, var_name: str):
        super().__init__(ErrorCodes.CONTAINER_VAR_ASSIGN_ERROR)
        self._var_name = var_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Error assigning value to variable '{self._var_name}'"
        )


class ContainerVarIsImmutableError(ErrorHandler):
    def __init__(self, var_name: str):
        super().__init__(ErrorCodes.CONTAINER_VAR_IS_IMMUTABLE_ERROR)
        self._var_name = var_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Variable '{self._var_name}' is immutable."
        )


class VariableWrongMemberError(ErrorHandler):
    def __init__(self, var_name: str):
        super().__init__(ErrorCodes.VARIABLE_WRONG_MEMBER_ERROR)
        self._var_name = var_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Variable '{self._var_name}' member is wrong."
        )
