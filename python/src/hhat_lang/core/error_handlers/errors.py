from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any


class ErrorCodes(Enum):
    INDEX_UNKNOWN_ERROR = auto()
    INDEX_ALLOC_ERROR = auto()
    INDEX_VAR_HAS_INDEXES_ERROR = auto()
    INDEX_INVALID_VAR_ERROR = auto()

    TYPE_QUANTUM_ON_CLASSICAL_ERROR = auto()
    TYPE_AND_MEMBER_NO_MATCH = auto()
    TYPE_ADD_MEMBER_ERROR = auto()
    TYPE_SINGLE_ASSIGN_ERROR = auto()
    TYPE_STRUCT_ASSIGN_ERROR = auto()
    TYPE_UNION_ASSIGN_ERROR = auto()
    TYPE_ENUM_ASSIGN_ERROR = auto()
    TYPE_MEMBER_NOT_RESOLVED = auto()

    TYPE_SYMBOL_CONVERSION_ERROR = auto()

    CONTAINER_VAR_ASSIGN_ERROR = auto()
    CONTAINER_VAR_IS_IMMUTABLE_ERROR = auto()

    VARIABLE_WRONG_MEMBER_ERROR = auto()
    VARIABLE_CREATION_ERROR = auto()
    VARIABLE_FREEING_BORROWED_ERROR = auto()

    CAST_NEG_TO_UNSIGNED_ERROR = auto()
    CAST_INT_OVERFLOW_ERROR = auto()
    CAST_ERROR = auto()

    FUNCTION_WRONG_ARGS_TYPES_ERROR = auto()
    FUNCTION_WRONG_DATA_ERROR = auto()
    FUNCTION_EXECUTION_ERROR = auto()

    INVALID_DATA_CONTAINER_CAST_ERROR = auto()
    INVALID_TYPE_CAST_ERROR = auto()

    STACK_FRAME_GET_ERROR = auto()
    STACK_FRAME_NOT_FN_ERROR = auto()
    STACK_EMPTY_ERROR = auto()
    STACK_OVERFLOW_ERROR = auto()

    HEAP_INVALID_KEY_ERROR = auto()
    HEAP_EMPTY_ERROR = auto()

    SYMBOLTABLE_INVALID_KEY_ERROR = auto()

    INVALID_QUANTUM_COMPUTED_RESULT = auto()

    INSTR_NOTFOUND_ERROR = auto()
    INSTR_STATUS_ERROR = auto()

    DATA_OVERFLOW_ERROR = auto()

    EVALUATOR_CAST_DATA_ERROR = auto()
    EVALUATOR_CAST_WILDCARD_BUILTIN_TYPE_ERROR = auto()

    INTERPRETER_EVALUATION_ERROR = auto()


class ErrorHandler(BaseException, ABC):
    def __init__(self, error_code: ErrorCodes):
        self.err_code = error_code

    @property
    def error_code(self) -> ErrorCodes:
        return self.err_code

    @abstractmethod
    def __call__(self) -> str: ...

    def __repr__(self) -> str:
        return f"Error<{self.err_code.name}:{self.err_code.value}>"


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
    def __init__(self, var_name: Any):
        self._var = var_name
        super().__init__(ErrorCodes.INDEX_VAR_HAS_INDEXES_ERROR)

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Var '{self._var}' already has indexes."


class IndexInvalidVarError(ErrorHandler):
    def __init__(self, var_name: Any):
        self._var = var_name
        super().__init__(ErrorCodes.INDEX_INVALID_VAR_ERROR)

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Var '{self._var}' not in IndexManager."


class TypeQuantumOnClassicalError(ErrorHandler):
    """Cannot have quantum data inside classical data type. The opposite is valid."""

    def __init__(self, q: Any, c: Any):
        super().__init__(ErrorCodes.TYPE_QUANTUM_ON_CLASSICAL_ERROR)
        self._q = q
        self._c = c

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: '{self._q}' cannot be inside '{self._c}'."
        )


class TypeAndMemberNoMatchError(ErrorHandler):
    def __init__(self, m_type: Any, m_member: Any):
        super().__init__(ErrorCodes.TYPE_AND_MEMBER_NO_MATCH)
        self.m_type = m_type
        self.m_member = m_member

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: '{self.m_type}' type and '{self.m_member}'"
            f" member are not of the same paradigm."
        )


class TypeAddMemberError(ErrorHandler):
    def __init__(self, member_name: Any):
        self._member = member_name
        super().__init__(ErrorCodes.TYPE_ADD_MEMBER_ERROR)

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Member of '{self._member}' could not be added."


class TypeSingleError(ErrorHandler):
    def __init__(self, type_name: Any):
        super().__init__(ErrorCodes.TYPE_SINGLE_ASSIGN_ERROR)
        self._type_name = type_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Type '{self._type_name}'"
            f" cannot contain more than one member."
        )


class TypeStructError(ErrorHandler):
    def __init__(self, type_name: Any):
        super().__init__(ErrorCodes.TYPE_STRUCT_ASSIGN_ERROR)
        self._type_name = type_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Attempting to add wrong member"
            f" types to type '{self._type_name}'."
        )


class TypeUnionError(ErrorHandler):
    def __init__(self, type_name: Any):
        super().__init__(ErrorCodes.TYPE_UNION_ASSIGN_ERROR)
        self._type_name = type_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Attempting to add wrong member"
            f" types to type '{self._type_name}'."
        )


class TypeEnumError(ErrorHandler):
    def __init__(self, type_name: Any):
        super().__init__(ErrorCodes.TYPE_ENUM_ASSIGN_ERROR)
        self._type_name = type_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Attempting to add wrong member"
            f" types to type '{self._type_name}'."
        )


class TypeMemberNotResolvedError(ErrorHandler):
    def __init__(self, type_name: Any, type_member: Any):
        super().__init__(ErrorCodes.TYPE_MEMBER_NOT_RESOLVED)
        self._type_name = type_name
        self._type_member = type_member

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: member {self._type_member} cannot"
            f" be resolved for type '{self._type_name}'."
        )


class TypeSymbolConversionError(ErrorHandler):
    def __init__(self, type_type: Any):
        super().__init__(ErrorCodes.TYPE_SYMBOL_CONVERSION_ERROR)
        self._type_type = type_type

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: symbol could not be converted; "
            f"expected str or array of strs and got {self._type_type}."
        )


class ContainerVarError(ErrorHandler):
    def __init__(self, var_name: Any):
        super().__init__(ErrorCodes.CONTAINER_VAR_ASSIGN_ERROR)
        self._var_name = var_name

    def __call__(self) -> str:
        name = self.__class__.__name__
        return f"[[{name}]]: Error assigning value to variable '{self._var_name}'"


class ContainerVarIsImmutableError(ErrorHandler):
    def __init__(self, var_name: Any):
        super().__init__(ErrorCodes.CONTAINER_VAR_IS_IMMUTABLE_ERROR)
        self._var_name = var_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Variable '{self._var_name}' is immutable."
        )


class VariableWrongMemberError(ErrorHandler):
    def __init__(self, var_name: Any):
        super().__init__(ErrorCodes.VARIABLE_WRONG_MEMBER_ERROR)
        self._var_name = var_name

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Variable '{self._var_name}' member is wrong."


class VariableCreationError(ErrorHandler):
    def __init__(self, var_name: Any, var_type: Any):
        super().__init__(ErrorCodes.VARIABLE_CREATION_ERROR)
        self._var_name = var_name
        self._var_type = var_type

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Could not create variable '{self._var_name}'"
            f" of type '{self._var_type}'."
        )


class VariableFreeingBorrowedError(ErrorHandler):
    def __init__(self, var_name: Any):
        super().__init__(ErrorCodes.VARIABLE_FREEING_BORROWED_ERROR)
        self._var_name = var_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Could not freeing variable '{self._var_name}',"
            f" it's borrowing its data."
        )


class CastNegToUnsignedError(ErrorHandler):
    def __init__(self, neg_value: Any, unsigned_value: Any):
        super().__init__(ErrorCodes.CAST_NEG_TO_UNSIGNED_ERROR)
        self._neg_value = neg_value
        self._unsigned_value = unsigned_value

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Cannot cast negative {self._neg_value} "
            f"to unsigned {self._unsigned_value}."
        )


class CastIntOverflowError(ErrorHandler):
    def __init__(self, int_value: Any, limit: Any):
        super().__init__(ErrorCodes.CAST_INT_OVERFLOW_ERROR)
        self._int_value = int_value
        self._limit = limit

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Cannot cast integer {self._int_value}"
            f" on {self._limit}; overflow error."
        )


class CastError(ErrorHandler):
    def __init__(self, type_cast: Any, data: Any):
        super().__init__(ErrorCodes.CAST_ERROR)
        self._type_cast = type_cast
        self._data = data

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Cannot cast {self._data} into {self._type_cast}."


class FnWrongArgsTypesError(ErrorHandler):
    def __init__(self, values: Any, expected: Any):
        self._values = values
        self._expected = expected
        super().__init__(ErrorCodes.FUNCTION_WRONG_ARGS_TYPES_ERROR)

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: wrong args types; expected {self._expected},"
            f" but got {self._values}."
        )


class FnWrongDataError(ErrorHandler):
    def __init__(self, values: Any):
        self._values = values
        super().__init__(ErrorCodes.FUNCTION_WRONG_DATA_ERROR)

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: wrong args types; expected literal or data container,"
            f" but got {self._values}."
        )


class InvalidDataContainerCastError(ErrorHandler):
    def __init__(self, dc_type: Any, from_type: Any, to_type: Any):
        self._dc_type = dc_type
        self._from_type = from_type
        self._to_type = to_type
        super().__init__(ErrorCodes.INVALID_DATA_CONTAINER_CAST_ERROR)

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: invalid data container {self._dc_type} when"
            f" casting from {self._from_type} to {self._to_type}."
        )


class InvalidTypeCastError(ErrorHandler):
    def __init__(self, current: Any, expected: Any):
        self._current = current
        self._expected = expected
        super().__init__(ErrorCodes.INVALID_TYPE_CAST_ERROR)

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: invalid type cast; expected type {self._expected},"
            f" but got {self._current}."
        )


class StackFrameGetError(ErrorHandler):
    def __init__(self, data: Any):
        self._data = data
        super().__init__(ErrorCodes.STACK_FRAME_GET_ERROR)

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Stack frame could not retrieve data {self._data}."


class StackFrameNotFnError(ErrorHandler):
    def __init__(self):
        super().__init__(ErrorCodes.STACK_FRAME_NOT_FN_ERROR)

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: Stack frame is not defined for functions,"
            f" but tried to used as if."
        )


class StackEmptyError(ErrorHandler):
    def __init__(self):
        super().__init__(ErrorCodes.STACK_EMPTY_ERROR)

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Stack is empty."


class StackOverflowError(ErrorHandler):
    def __init__(self):
        super().__init__(ErrorCodes.STACK_OVERFLOW_ERROR)

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Stack overflow."


class HeapEmptyError(ErrorHandler):
    def __init__(self):
        super().__init__(ErrorCodes.HEAP_EMPTY_ERROR)

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: Heap is empty."


class HeapInvalidKeyError(ErrorHandler):
    def __init__(self, key: Any):
        super().__init__(ErrorCodes.HEAP_INVALID_KEY_ERROR)
        self._key = key

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: key '{self._key}' is invalid."


class SymbolTableInvalidKeyError(ErrorHandler):
    def __init__(self, key: Any, key_type: str):
        super().__init__(ErrorCodes.SYMBOLTABLE_INVALID_KEY_ERROR)
        self._key = key
        self._key_type = key_type

    @classmethod
    def Type(cls) -> str:
        return "type"

    @classmethod
    def Fn(cls) -> str:
        return "fn"

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: key '{self._key}' is invalid for {self._key_type}."


class InvalidQuantumComputedResult(ErrorHandler):
    def __init__(self, qdata: Any):
        super().__init__(ErrorCodes.INVALID_QUANTUM_COMPUTED_RESULT)
        self._qdata = qdata

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: quantum data {self._qdata} produced invalid result."


class InstrNotFoundError(ErrorHandler):
    def __init__(self, name: Any):
        super().__init__(ErrorCodes.INSTR_NOTFOUND_ERROR)
        self._name = name

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: instr {self._name} not found"


class InstrStatusError(ErrorHandler):
    def __init__(self, name: Any):
        super().__init__(ErrorCodes.INSTR_STATUS_ERROR)
        self._name = name

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]: instr {self._name} has status error"


class FunctionExecutionError(ErrorHandler):
    def __init__(self, *args: Any, fn_name: Any, reason: str):
        super().__init__(ErrorCodes.FUNCTION_EXECUTION_ERROR)
        self._name = fn_name
        self._args = args
        self._reason = reason

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: function {self._name} with args {self.args}"
            f" failed due to: {self._reason}"
        )


class DataOverflowError(ErrorHandler):
    def __init__(self, data: Any, data_type: Any, expected_type: Any):
        super().__init__(ErrorCodes.DATA_OVERFLOW_ERROR)
        self._data_type = data_type
        self._expected_type = expected_type
        self._data = data

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: data {self._data} of type {self._data_type},"
            f" but attempted to cast into type {self._expected_type} (data overflow)."
        )


class EvaluatorCastDataError(ErrorHandler):
    def __init__(self, data: Any):
        super().__init__(ErrorCodes.EVALUATOR_CAST_DATA_ERROR)
        self._name = type(data)
        self._data = data

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: data {self._data} should be container"
            f" or literal, but got {self._name} instead."
        )


class EvaluatorCastWildcardBuiltinTypeError(ErrorHandler):
    def __init__(self, t_name: Any):
        super().__init__(ErrorCodes.EVALUATOR_CAST_WILDCARD_BUILTIN_TYPE_ERROR)
        self._name = t_name

    def __call__(self) -> str:
        return (
            f"[[{self.__class__.__name__}]]: a precise type should be known, but"
            f" a wildcard type was given ({self._name})."
        )


class InterpreterEvaluationError(ErrorHandler):
    def __init__(self, error_where: str, msg: str):
        super().__init__(ErrorCodes.INTERPRETER_EVALUATION_ERROR)
        self._msg = msg
        self._err = error_where

    def __call__(self) -> str:
        return f"[[{self.__class__.__name__}]]<{self._err} error]>: {self._msg}"
