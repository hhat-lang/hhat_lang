from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, NoReturn

from rich.console import Console

console = Console()


def sys_exit(*args: Any, error_fn: ErrorHandler) -> NoReturn:
    """
    System exit with pretty print message on terminal. The exit status is equivalent
    to ``ErrorHandler``'s instance corresponding ``ErrorCodes`` enum member value.

    Args:
        *args: the arguments to be placed when calling `error_fn` instance
        error_fn: a callable ``ErrorHandler`` instance
    """

    console.print(error_fn(*args))
    sys.exit(error_fn.error_code.value)


class ErrorCodes(Enum):
    """
    Enum listing all possible error codes for the H-hat language system.

    This is the user facing error messaging logic, given the user should not get
    Python's error messages for H-hat written code.

    Error values are reserved and divided into categories containing their own value
    range, such as: base error (generic errors for literal, symbols and paradigms
    checks, 3 to 99), index errors (101 to 199), type errors, data errors, cast
    errors, function errors, memory errors, instruction errors, evaluator errors,
    compiler errors, etc. Subcategories may exist depending on specific needs. Check
    this class source code for more information.
    """

    FEATURE_NOT_IMPLEMENTED_ERROR = 1
    """Feature not implemented reserved error value is always 1."""

    BASE_ERROR = 2
    """
    Base generic reserved error values from 3 to 99. It includes literal, symbols,
    classical/quantum paradigm checks. Value number 2 reserved for itself.
    """
    LITERAL_TYPE_MISMATCH_ERROR = auto()
    ARRAY_QUANTUM_CLASSICAL_MIXED_ERROR = auto()
    ARRAY_ELEMS_NOT_SAME_ERROR = auto()

    INDEX_ERROR = 100
    """Index related reserved error values from 101 to 199."""
    INDEX_UNKNOWN_ERROR = auto()
    INDEX_ALLOC_ERROR = auto()
    INDEX_VAR_HAS_INDEXES_ERROR = auto()
    INDEX_INVALID_VAR_ERROR = auto()

    TYPE_ERROR = 200
    """Type related reserved error values from 201 to 299."""
    TYPE_INVALID_MEMBER_ERROR = auto()
    TYPE_INVALID_INDEX_ON_CONTENT_ERROR = auto()
    TYPE_MEMBER_OVERFLOW_ERROR = auto()
    TYPE_QUANTUM_ON_CLASSICAL_ERROR = auto()
    TYPE_AND_MEMBER_NO_MATCH = auto()
    TYPE_ADD_MEMBER_ERROR = auto()
    TYPE_SINGLE_ASSIGN_ERROR = auto()
    TYPE_STRUCT_ASSIGN_ERROR = auto()
    TYPE_ENUM_ASSIGN_ERROR = auto()
    TYPE_MEMBER_NOT_RESOLVED_ERROR = auto()
    TYPE_MEMBER_ALREADY_EXISTS_ERROR = auto()
    TYPE_MEMBER_EMPTY_ERROR = auto()

    COLLECTION_INSERT_WRONG_TYPE_ERROR = auto()

    TYPE_NOT_FOUND = auto()
    TYPE_SYMBOL_CONVERSION_ERROR = auto()

    DATA_ERROR = 300
    """Data related reserved error values from 301 to 399."""
    RETRIEVE_APPENDABLE_DATA_ERROR = auto()
    CONTAINER_VAR_ASSIGN_ERROR = auto()
    CONTAINER_EMPTY_USAGE_ERROR = auto()
    CONTAINER_VAR_IS_IMMUTABLE_ERROR = auto()
    QUANTUM_DATA_NOT_APPENDABLE_ERROR = auto()

    VARIABLE_WRONG_MEMBER_ERROR = auto()
    VARIABLE_CREATION_ERROR = auto()
    VARIABLE_FREEING_BORROWED_ERROR = auto()

    IMMUTABLE_DATA_REASSIGNMENT_ERROR = auto()
    INVALID_CONTENT_DATA_ERROR = auto()
    USING_DATA_BEFORE_INITIALIZATION_ERROR = auto()
    DATA_INITIALIZATION_WRONG_ARGUMENTS_ERROR = auto()

    DATA_OVERFLOW_ERROR = auto()

    VAR_CONTAINER_PARAMS_TYPE_ERROR = auto()

    INVALID_DATA_STORAGE_ERROR = auto()
    INVALID_DATA_TYPE_COLLECTION_ERROR = auto()
    LAZY_SEQUENCE_CONSUMED_ERROR = auto()

    CAST_ERROR = 400
    """Cast related reserved error value from 401 to 499."""
    CAST_NEG_TO_UNSIGNED_ERROR = auto()
    CAST_INT_OVERFLOW_ERROR = auto()

    INVALID_DATA_CONTAINER_CAST_ERROR = auto()
    INVALID_TYPE_CAST_ERROR = auto()

    FN_ERROR = 500
    """Function related reserved error value from 501 to 599."""
    FUNCTION_WRONG_ARGS_TYPES_ERROR = auto()
    FUNCTION_WRONG_DATA_ERROR = auto()
    FUNCTION_EXECUTION_ERROR = auto()

    MEMORY_ERROR = 600
    """Memory related reserved error values from 601 to 699."""
    STACK_FRAME_GET_ERROR = auto()
    STACK_FRAME_NOT_FN_ERROR = auto()
    STACK_EMPTY_ERROR = auto()
    STACK_OVERFLOW_ERROR = auto()

    HEAP_INVALID_KEY_ERROR = auto()
    HEAP_EMPTY_ERROR = auto()

    SYMBOLTABLE_INVALID_KEY_ERROR = auto()

    INSTR_ERROR = 700
    """Instructions related reserved error values from 701 to 799."""
    INVALID_QUANTUM_COMPUTED_RESULT = auto()

    INSTR_NOTFOUND_ERROR = auto()
    INSTR_STATUS_ERROR = auto()

    EVALUATOR_ERROR = 800
    """Evaluator related reserved error values from 801 to 899."""
    EVALUATOR_CAST_DATA_ERROR = auto()
    EVALUATOR_CAST_WILDCARD_BUILTIN_TYPE_ERROR = auto()

    INTERPRETER_EVALUATION_ERROR = auto()

    COMPILER_ERROR = 900
    """Compiler related reserved error values from 901 to 999."""


class ErrorHandler(BaseException, ABC):
    err_code: ErrorCodes

    def __init__(self, *_args: Any, **_kwargs: Any):
        pass

    @classmethod
    @property
    def error_code(cls) -> ErrorCodes:
        return cls.err_code

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> str: ...

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"error [bold]{self.err_code.name}[[red]{self.err_code.value}[/red]][/bold]"


#################
# ERROR CLASSES #
#################


class FeatureNotImplementedError(ErrorHandler):
    err_code = ErrorCodes.FEATURE_NOT_IMPLEMENTED_ERROR

    def __init__(self, name: Any, descr: str):
        """
        Class to handle feature not implemented errors. The text will appear to the user as::

            FEATURE_NOT_IMPLEMENTED_ERROR[1]: feature '<feature name>' which is \
            '<feature description>' is not implemented on this H-hat version.

        Args:
            name: name of the method, function, class, obj, etc.
            descr: text description of its functionality
        """

        self.name = name
        self.descr = descr
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: feature '{self.name}' which is '{self._lit_type}'"
            f" is not implemented on this H-hat version."
        )


class LiteralTypeMismatchError(ErrorHandler):
    err_code = ErrorCodes.LITERAL_TYPE_MISMATCH_ERROR

    def __init__(self, lit: Any, lit_type: Any):
        self._lit = lit
        self._lit_type = lit_type
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: literal {self._lit} and type {self._lit_type}"
            f" mismatched paradigms; both need be classical or quantum."
        )


class ArrayQuantumClassicalMixedError(ErrorHandler):
    err_code = ErrorCodes.ARRAY_QUANTUM_CLASSICAL_MIXED_ERROR

    def __init__(self, array: Any):
        self._array = array
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: array {self._array} has quantum "
            f"and classical data, which is invalid behavior."
        )


class ArrayElemsNotSameError(ErrorHandler):
    err_code = ErrorCodes.ARRAY_ELEMS_NOT_SAME_ERROR

    def __init__(self, array: Any):
        self._array = array
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: array {self._array} has not the same type, which is invalid behavior."


class IndexUnknownError(ErrorHandler):
    err_code = ErrorCodes.INDEX_UNKNOWN_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Index unknown error."


class IndexAllocationError(ErrorHandler):
    err_code = ErrorCodes.INDEX_ALLOC_ERROR

    def __init__(self, requested_idxs: int, max_idxs: int):
        self._req_idxs = requested_idxs
        self._max_idxs = max_idxs
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Requested {self._req_idxs}," f" but maximum is {self._max_idxs}"


class IndexVarHasIndexesError(ErrorHandler):
    err_code = ErrorCodes.INDEX_VAR_HAS_INDEXES_ERROR

    def __init__(self, var_name: Any):
        self._var = var_name
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Var '{self._var}' already has indexes."


class IndexInvalidVarError(ErrorHandler):
    err_code = ErrorCodes.INDEX_INVALID_VAR_ERROR

    def __init__(self, var_name: Any):
        self._var = var_name
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Var '{self._var}' not in IndexManager."


class TypeInvalidMemberError(ErrorHandler):
    """Invalid member on type, e.g. enum member inside struct."""

    err_code = ErrorCodes.TYPE_INVALID_MEMBER_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, name: Any, member: Any) -> str:
        return f"{self}: type '{name}' had invalid member added ('{member}')."


class TypeInvalidIndexOnContentError(ErrorHandler):
    """Invalid index type on type's content. Should be symbol or integer."""

    err_code = ErrorCodes.TYPE_INVALID_INDEX_ON_CONTENT_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, name: Any, item: Any) -> str:
        return (
            f"{self}: content type '{name}' had invalid index"
            f" type '{item}' ({type(item)}) to retrieve its actual content."
        )


class TypeMemberOverflowError(ErrorHandler):
    """More members to be added than it was defined."""

    err_code = ErrorCodes.TYPE_MEMBER_OVERFLOW_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, type_name: Any, type_type: Any) -> str:
        return f"{self}: too many members for type {type_name} ({type_type})."


class TypeQuantumOnClassicalError(ErrorHandler):
    """Cannot have quantum data inside classical data type. The opposite is valid."""

    err_code = ErrorCodes.TYPE_QUANTUM_ON_CLASSICAL_ERROR

    def __init__(self, q: Any, c: Any):
        super().__init__()
        self._q = q
        self._c = c

    def __call__(self, *_args: Any) -> str:
        return f"{self}: '{self._q}' cannot be inside '{self._c}'."


class TypeAndMemberNoMatchError(ErrorHandler):
    err_code = ErrorCodes.TYPE_AND_MEMBER_NO_MATCH

    def __init__(self, m_type: Any, m_member: Any):
        super().__init__()
        self.m_type = m_type
        self.m_member = m_member

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: '{self.m_type}' type and '{self.m_member}'"
            f" member are not of the same paradigm."
        )


class TypeAddMemberError(ErrorHandler):
    err_code = ErrorCodes.TYPE_ADD_MEMBER_ERROR

    def __init__(self, member_name: Any):
        self._member = member_name
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Member of '{self._member}' could not be added."


class TypeSingleError(ErrorHandler):
    err_code = ErrorCodes.TYPE_SINGLE_ASSIGN_ERROR

    def __init__(self, type_name: Any):
        super().__init__()
        self._type_name = type_name

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Type '{self._type_name}'" f" cannot contain more than one member."


class TypeStructError(ErrorHandler):
    err_code = ErrorCodes.TYPE_STRUCT_ASSIGN_ERROR

    def __init__(self, type_name: Any):
        super().__init__()
        self._type_name = type_name

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Attempting to add wrong member" f" types to type '{self._type_name}'."


class TypeEnumError(ErrorHandler):
    err_code = ErrorCodes.TYPE_ENUM_ASSIGN_ERROR

    def __init__(self, type_name: Any):
        super().__init__()
        self._type_name = type_name

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Attempting to add wrong member" f" types to type '{self._type_name}'."


class TypeMemberNotResolvedError(ErrorHandler):
    err_code = ErrorCodes.TYPE_MEMBER_NOT_RESOLVED_ERROR

    def __init__(self, type_name: Any, type_member: Any):
        super().__init__()
        self._type_name = type_name
        self._type_member = type_member

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: member {self._type_member} cannot"
            f" be resolved for type '{self._type_name}'."
        )


class TypeMemberAlreadyExistsError(ErrorHandler):
    err_code = ErrorCodes.TYPE_MEMBER_ALREADY_EXISTS_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, name: Any, member_name: Any) -> str:
        return f"{self}: member {member_name} already exists on type {name}."


class TypeMemberEmptyError(ErrorHandler):
    err_code = ErrorCodes.TYPE_MEMBER_EMPTY_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, name: Any) -> str:
        return f"{self}: type {name} has empty member (not added any member yet)."


class CollectionInsertWrongTypeError(ErrorHandler):
    err_code = ErrorCodes.COLLECTION_INSERT_WRONG_TYPE_ERROR

    def __init__(self, name: Any):
        super().__init__()
        self.name = name

    def __call__(self, member: Any) -> str:
        return (
            f"{self}: collection '{self.name}' member received an invalid member"
            f" '{member}' ({type(member)}) to be inserted into its content."
        )


class TypeNotFoundError(ErrorHandler):
    err_code = ErrorCodes.TYPE_NOT_FOUND

    def __init__(self, type_type: Any):
        super().__init__()
        self._type_type = type_type

    def __call__(self, *_args: Any) -> str:
        return f"{self}: type '{self._type_type}' not found."


class TypeSymbolConversionError(ErrorHandler):
    err_code = ErrorCodes.TYPE_SYMBOL_CONVERSION_ERROR

    def __init__(self, type_type: Any):
        super().__init__()
        self._type_type = type_type

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: symbol could not be converted; "
            f"expected str or array of strs and got {self._type_type}."
        )


class RetrieveAppendableDataError(ErrorHandler):
    err_code = ErrorCodes.RETRIEVE_APPENDABLE_DATA_ERROR

    def __init__(self, value: Any):
        super().__init__()
        self.value = value

    def __call__(self, *_args: Any) -> str:
        return f"{self}: cannot retrieve data appendable collection using '{self.value}'"


class ContainerVarError(ErrorHandler):
    err_code = ErrorCodes.CONTAINER_VAR_ASSIGN_ERROR

    def __init__(self, var_name: Any):
        super().__init__()
        self._var_name = var_name

    def __call__(self, value: Any) -> str:
        return f"{self}: Error assigning value(s) '{value}' to data container '{self._var_name}'"


class ContainerEmptyUsageError(ErrorHandler):
    err_code = ErrorCodes.CONTAINER_EMPTY_USAGE_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, value: Any, action: str) -> str:
        return f"{self}: trying to use an variable empty container to {action } '{value}'."


class ContainerVarIsImmutableError(ErrorHandler):
    err_code = ErrorCodes.CONTAINER_VAR_IS_IMMUTABLE_ERROR

    def __init__(self, var_name: Any):
        super().__init__()
        self._var_name = var_name

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Variable '{self._var_name}' is immutable."


class QuantumDataNotAppendableError(ErrorHandler):
    err_code = ErrorCodes.QUANTUM_DATA_NOT_APPENDABLE_ERROR

    def __init__(self, var_name: Any, kind: Enum):
        super().__init__()
        self._var_name = var_name
        self._kind = kind

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: quantum data '{self._var_name}' must be an "
            f"appendable, but got [bold]{self._kind.name}[/bold]."
        )


class VariableWrongMemberError(ErrorHandler):
    err_code = ErrorCodes.VARIABLE_WRONG_MEMBER_ERROR

    def __init__(self, var_name: Any):
        super().__init__()
        self._var_name = var_name

    def __call__(self, value: Any) -> str:
        return f"{self}: Variable '{self._var_name}' member is wrong ({value})."


class VariableCreationError(ErrorHandler):
    err_code = ErrorCodes.VARIABLE_CREATION_ERROR

    def __init__(self, var_name: Any, var_type: Any):
        super().__init__()
        self._var_name = var_name
        self._var_type = var_type

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: Could not create variable '{self._var_name}'" f" of type '{self._var_type}'."
        )


class VariableFreeingBorrowedError(ErrorHandler):
    err_code = ErrorCodes.VARIABLE_FREEING_BORROWED_ERROR

    def __init__(self, var_name: Any):
        super().__init__()
        self._var_name = var_name

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: Could not freeing variable '{self._var_name}'," f" it's borrowing its data."
        )


class ImmutableDataReassignmentError(ErrorHandler):
    err_code = ErrorCodes.IMMUTABLE_DATA_REASSIGNMENT_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, name: Any) -> str:
        return f"{self}: '{name}' is being reassigned," f" but it is an immutable data."


class InvalidContentDataError(ErrorHandler):
    err_code = ErrorCodes.INVALID_CONTENT_DATA_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, name: Any, data: Any) -> str:
        return f"{self}: '{name}' had assigned invalid data {data}."


class UsingDataBeforeInitializationError(ErrorHandler):
    err_code = ErrorCodes.USING_DATA_BEFORE_INITIALIZATION_ERROR

    def __init__(self, name: Any = None, member: Any = None):
        super().__init__()
        self.name = name
        self.member = member

    def __call__(self, *_args: Any) -> str:
        if self.name and self.member:
            msg = (
                f"{self.name} has member {self.member} being used before"
                f" initialization (assign a value to it before use)."
            )

        else:
            msg = "data being used before initialization (assign a value to it before use)."

        return f"{self}: {msg}"


class DataInitializationArgumentsError(ErrorHandler):
    err_code = ErrorCodes.DATA_INITIALIZATION_WRONG_ARGUMENTS_ERROR

    def __init__(self, var_name: Any, var_type: Any, **kwargs: Any):
        super().__init__()
        self.var_name = var_name
        self.var_type = var_type
        self.kwargs = kwargs

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: could not initialize '{self.var_name}',"
            f" wrong arguments: {', '.join(f'{k}={v} ({type(v)})' for k, v in self.kwargs.items())}"
        )


class CastNegToUnsignedError(ErrorHandler):
    err_code = ErrorCodes.CAST_NEG_TO_UNSIGNED_ERROR

    def __init__(self, neg_value: Any, unsigned_value: Any):
        super().__init__()
        self._neg_value = neg_value
        self._unsigned_value = unsigned_value

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: Cannot cast negative {self._neg_value} "
            f"to unsigned {self._unsigned_value}."
        )


class CastIntOverflowError(ErrorHandler):
    err_code = ErrorCodes.CAST_INT_OVERFLOW_ERROR

    def __init__(self, int_value: Any, limit: Any):
        super().__init__()
        self._int_value = int_value
        self._limit = limit

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: Cannot cast integer {self._int_value}" f" on {self._limit}; overflow error."
        )


class CastError(ErrorHandler):
    err_code = ErrorCodes.CAST_ERROR

    def __init__(self, type_cast: Any, data: Any):
        super().__init__()
        self._type_cast = type_cast
        self._data = data

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Cannot cast {self._data} into {self._type_cast}."


class FnWrongArgsTypesError(ErrorHandler):
    err_code = ErrorCodes.FUNCTION_WRONG_ARGS_TYPES_ERROR

    def __init__(self, values: Any, expected: Any):
        self._values = values
        self._expected = expected
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: wrong args types; expected {self._expected}," f" but got {self._values}."


class FnWrongDataError(ErrorHandler):
    err_code = ErrorCodes.FUNCTION_WRONG_DATA_ERROR

    def __init__(self, values: Any):
        self._values = values
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: wrong args types; expected literal or data container,"
            f" but got {self._values}."
        )


class InvalidDataContainerCastError(ErrorHandler):
    err_code = ErrorCodes.INVALID_DATA_CONTAINER_CAST_ERROR

    def __init__(self, dc_type: Any, from_type: Any, to_type: Any):
        self._dc_type = dc_type
        self._from_type = from_type
        self._to_type = to_type
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: invalid data container {self._dc_type} when"
            f" casting from {self._from_type} to {self._to_type}."
        )


class InvalidTypeCastError(ErrorHandler):
    err_code = ErrorCodes.INVALID_TYPE_CAST_ERROR

    def __init__(self, current: Any, expected: Any):
        self._current = current
        self._expected = expected
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: invalid type cast; expected type {self._expected},"
            f" but got {self._current}."
        )


class StackFrameGetError(ErrorHandler):
    err_code = ErrorCodes.STACK_FRAME_GET_ERROR

    def __init__(self, data: Any):
        self._data = data
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Stack frame could not retrieve data {self._data}."


class StackFrameNotFnError(ErrorHandler):
    err_code = ErrorCodes.STACK_FRAME_NOT_FN_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Stack frame is not defined for functions," f" but tried to used as if."


class StackEmptyError(ErrorHandler):
    err_code = ErrorCodes.STACK_EMPTY_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Stack is empty."


class StackOverflowError(ErrorHandler):
    err_code = ErrorCodes.STACK_OVERFLOW_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Stack overflow."


class HeapEmptyError(ErrorHandler):
    err_code = ErrorCodes.HEAP_EMPTY_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, *_args: Any) -> str:
        return f"{self}: Heap is empty."


class HeapInvalidKeyError(ErrorHandler):
    err_code = ErrorCodes.HEAP_INVALID_KEY_ERROR

    def __init__(self, key: Any):
        super().__init__()
        self._key = key

    def __call__(self, *_args: Any) -> str:
        return f"{self}: key '{self._key}' is invalid."


class SymbolTableInvalidKeyError(ErrorHandler):
    err_code = ErrorCodes.SYMBOLTABLE_INVALID_KEY_ERROR

    def __init__(self, key: Any, key_type: str):
        super().__init__()
        self._key = key
        self._key_type = key_type

    @classmethod
    def Type(cls) -> str:
        return "type"

    @classmethod
    def Fn(cls) -> str:
        return "fn"

    def __call__(self, *_args: Any) -> str:
        return f"{self}: key '{self._key}' is invalid for {self._key_type}."


class InvalidQuantumComputedResult(ErrorHandler):
    err_code = ErrorCodes.INVALID_QUANTUM_COMPUTED_RESULT

    def __init__(self, qdata: Any):
        super().__init__()
        self._qdata = qdata

    def __call__(self, *_args: Any) -> str:
        return f"{self}: quantum data {self._qdata} produced invalid result."


class InstrNotFoundError(ErrorHandler):
    err_code = ErrorCodes.INSTR_NOTFOUND_ERROR

    def __init__(self, name: Any):
        super().__init__()
        self._name = name

    def __call__(self, *_args: Any) -> str:
        return f"{self}: instr {self._name} not found"


class InstrStatusError(ErrorHandler):
    err_code = ErrorCodes.INSTR_STATUS_ERROR

    def __init__(self, name: Any):
        super().__init__()
        self._name = name

    def __call__(self, *_args: Any) -> str:
        return f"{self}: instr {self._name} has status error"


class FunctionExecutionError(ErrorHandler):
    err_code = ErrorCodes.FUNCTION_EXECUTION_ERROR

    def __init__(self, *args: Any, fn_name: Any, reason: str):
        super().__init__()
        self._name = fn_name
        self._args = args
        self._reason = reason

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: function {self._name} with args {self.args}" f" failed due to: {self._reason}"
        )


class DataOverflowError(ErrorHandler):
    err_code = ErrorCodes.DATA_OVERFLOW_ERROR

    def __init__(self, data: Any, data_type: Any, expected_type: Any):
        super().__init__()
        self._data_type = data_type
        self._expected_type = expected_type
        self._data = data

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: data {self._data} of type {self._data_type},"
            f" but attempted to cast into type {self._expected_type} (data overflow)."
        )


class VarContainerParamsTypeError(ErrorHandler):
    err_code = ErrorCodes.VAR_CONTAINER_PARAMS_TYPE_ERROR

    def __init__(self, var_name: Any):
        super().__init__()
        self._name = var_name

    def __call__(self, params: Any) -> str:
        return (
            f"{self}: variable {self._name} has an error when converting params"
            f" type '{params}': invalid type {type(params)}."
        )


class InvalidDataTypeCollectionError(ErrorHandler):
    err_code = ErrorCodes.INVALID_DATA_TYPE_COLLECTION_ERROR

    def __init__(self, name: Any):
        super().__init__()
        self._name = name

    def __call__(self, *_args: Any) -> str:
        return f"{self}: {self._name} is not a valid data type collection key."


class InvalidDataStorageError(ErrorHandler):
    err_code = ErrorCodes.INVALID_DATA_STORAGE_ERROR

    def __init__(self, name: Any):
        super().__init__()
        self._name = name

    def __call__(self, *_args: Any) -> str:
        return f"{self}: {self._name} is not a valid data storage key."


class LazySequenceConsumedError(ErrorHandler):
    err_code = ErrorCodes.LAZY_SEQUENCE_CONSUMED_ERROR

    def __init__(self):
        super().__init__()

    def __call__(self, name) -> str:
        return f"{self}: {name} has a lazy storage and it's already consumed."


class EvaluatorCastDataError(ErrorHandler):
    err_code = ErrorCodes.EVALUATOR_CAST_DATA_ERROR

    def __init__(self, data: Any):
        super().__init__()
        self._name = type(data)
        self._data = data

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: data {self._data} should be container"
            f" or literal, but got {self._name} instead."
        )


class EvaluatorCastWildcardBuiltinTypeError(ErrorHandler):
    err_code = ErrorCodes.EVALUATOR_CAST_WILDCARD_BUILTIN_TYPE_ERROR

    def __init__(self, t_name: Any):
        super().__init__()
        self._name = t_name

    def __call__(self, *_args: Any) -> str:
        return (
            f"{self}: a precise type should be known, but"
            f" a wildcard type was given ({self._name})."
        )


class InterpreterEvaluationError(ErrorHandler):
    err_code = ErrorCodes.INTERPRETER_EVALUATION_ERROR

    def __init__(self, error_where: str, msg: str):
        super().__init__()
        self._msg = msg
        self._err = error_where

    def __call__(self, *_args: Any) -> str:
        return f"{self}<{self._err} error]>: {self._msg}"
