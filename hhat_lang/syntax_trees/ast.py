from abc import ABC
from typing import Any, Callable, Iterable, Union
from hhat_lang.syntax_trees.literal_define import (
    literal_bool_define,
    literal_int_define
)
from enum import Enum, auto, unique


################
# ENUM CLASSES #
################

@unique
class ExprParadigm(Enum):
    NONE = auto()
    SINGLE = auto()
    SEQUENTIAL = auto()
    CONCURRENT = auto()
    PARALLEL = auto()


@unique
class ASTType(Enum):
    NONE        = auto()
    LITERAL     = auto()
    ID          = auto()
    BUILTIN     = auto()
    OPERATION   = auto()
    CALL        = auto()
    ARGS        = auto()
    Q_OPERATION = auto()
    EXPR        = auto()
    ARRAY       = auto()
    MAIN        = auto()
    PROGRAM     = auto()


@unique
class DataTypeEnum(Enum):
    NULL = auto()
    BOOL = auto()
    INT = auto()
    Q_ARRAY = auto()


operations_or_id = [ASTType.OPERATION, ASTType.Q_OPERATION, ASTType.ID]

literal_dict = {
    DataTypeEnum.BOOL: literal_bool_define,
    DataTypeEnum.INT: literal_int_define
}

ato_types = Union[DataTypeEnum, ASTType]


####################
# ABSTRACT OBJECTS #
####################

class ATO(ABC):
    """Abstract tree object

    """
    def __init__(self, token: str, ato_type: ato_types):
        self.token = token
        self.type = ato_type

    def __repr__(self) -> str:
        return self.token


class AST(ABC):
    """Abstract syntax tree object

    """
    def __init__(
            self,
            node: ATO | None = None,
            ast_type: ASTType = ASTType.NONE,
            paradigm: ExprParadigm = ExprParadigm.NONE,
            args: Any | None = None,
    ):
        self.node = node or ""
        self.type = ast_type
        self.edges = args
        self.paradigm = paradigm

    def match_paradigm(self, args: str) -> str:
        match self.paradigm:
            case ExprParadigm.SINGLE:
                paradigm_name = args
            case ExprParadigm.SEQUENTIAL:
                paradigm_name = "'seq[" + args + "]"
            case ExprParadigm.CONCURRENT:
                paradigm_name = "'conc(" + args + ")"
            case ExprParadigm.PARALLEL:
                paradigm_name = "'par{" + args + "}"
            case ExprParadigm.NONE:
                paradigm_name = ""
            case _:
                paradigm_name = "?"
        return paradigm_name

    def __len__(self) -> int:
        return len(self.edges)

    def __iter__(self) -> Iterable:
        yield from self.edges

    def __repr__(self) -> str:
        token = self.node.token if self.node else ""
        if len(self.edges) > 0:
            args = " ".join(str(k) for k in self.edges)
            paradigm_name = self.match_paradigm(args)
            if self.type == ASTType.EXPR:
                edges = f"({paradigm_name})"
            else:
                edges = paradigm_name

            if token:
                return token + "(" + edges + ")"
            return edges
        return token


###############
# AST OBJECTS #
###############

class Literal(ATO):
    def __init__(self, token: str, lit_type: DataTypeEnum):
        super().__init__(token, lit_type)
        self.value = literal_dict[self.type](self.token)


class Id(ATO):
    def __init__(self, token: str, ato_type: ASTType = ASTType.ID):
        super().__init__(token=token, ato_type=ato_type)
        self.value = self.token


class Expr(AST):
    def __init__(self, *values: Any):
        super().__init__(
            node=None,
            ast_type=ASTType.EXPR,
            paradigm=ExprParadigm.SINGLE,
            args=values
        )


class Array(AST):
    def __init__(self, paradigm: ExprParadigm, *values: Any):
        super().__init__(
            node=None,
            ast_type=ASTType.ARRAY,
            paradigm=paradigm,
            args=values
        )


class Operation(AST):
    def __init__(self, oper_token: ATO | str, args: Array | None):
        new_type = self.get_oper_type(oper_token)
        oper_token = self.set_oper_token(oper_token, new_type)
        super().__init__(
            node=oper_token,
            ast_type=new_type,
            paradigm=(ExprParadigm.SINGLE if args is None else args.paradigm),
            args=args or ()
        )

    @staticmethod
    def get_oper_type(oper_token: ATO) -> ASTType:
        if oper_token.token.startswith("@"):
            return ASTType.Q_OPERATION
        return ASTType.OPERATION

    @staticmethod
    def set_oper_token(oper_token: ATO | str, new_type: ASTType) -> ATO:
        if isinstance(oper_token, Id):
            oper_token.type = new_type
        else:
            oper_token = Id(token=oper_token, ato_type=new_type)
        return oper_token


class Main(AST):
    def __init__(self, exprs: AST):
        super().__init__(
            node=None,
            ast_type=ASTType.MAIN,
            paradigm=exprs.paradigm,
            args=exprs
        )


class Program(AST):
    def __init__(self, *super_exprs: Any):
        super().__init__(
            node=None,
            ast_type=ASTType.PROGRAM,
            paradigm=ExprParadigm.NONE,
            args=super_exprs
        )
