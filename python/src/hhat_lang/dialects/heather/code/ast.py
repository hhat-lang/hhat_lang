from __future__ import annotations

from hhat_lang.core.code.ast import AST, Node, Terminal

###############
# AST CLASSES #
###############


class Id(Terminal):
    def __init__(self, value: str):
        self._value = (value,)
        self._name = value


class CompositeId(Node):
    def __init__(self, *names: Id):
        self._value = names
        self._name = self.__class__.__name__


class CompositeIdWithClosure(Node):
    """
    Used for calling many attributes/properties from the same Id root, for instance:

    ```
    user-info.{host port}
    dataset.{obj-name pos.{x y}}
    ```

    As showed above, it can be nested.
    """

    def __init__(self, *values: Id | CompositeId, name: Id | CompositeId):
        self._value = (name, values)
        self._name = self.__class__.__name__


class ArgValuePair(Node):
    def __init__(self, arg: Id, value: ValueType):
        self._value = (arg, value)
        self._name = self.__class__.__name__


class OnlyValue(Node):
    def __init__(self, value: ValueType):
        self._value = (value,)
        self._name = self.__class__.__name__


class Modifier(Node):
    def __init__(self, *modifiers: ArgValuePair):
        self._values = modifiers
        self._name = self.__class__.__name__


class ModifiedId(Node):
    """
    A modifier is in the form of `< value ... >` or `< arg:value ... >`.
    It is intended to change the behavior of the modified, which can be a
    variable, a type or a function call.
    """

    def __init__(self, name: Id | CompositeId, modifier: Modifier):
        self._value = (name, modifier)
        self._name = self.__class__.__name__


class Literal(Terminal):
    def __init__(self, value: str, value_type: str):
        self._value = (value,)
        self._name = value_type


class Array(Node):
    pass


class Hash(Node):
    pass


class Cast(Node):
    """
    A special syntax sugar that is intended to change the type of what it is
    being applied to (usually a variable). The most important use case is to
    cast a quantum data to a classical type.
    """

    def __init__(self, name: TypeType, cast_to: TypeType):
        self._value = (name, cast_to)
        self._name = self.__class__.__name__


class Expr(Node):
    def __init__(self, *expr: AST):
        self._value = expr
        self._name = self.__class__.__name__


class Declare(Node):
    def __init__(self, var_name: Id, var_type: TypeType):
        self._value = (var_name, var_type)
        self._name = self.__class__.__name__


class Assign(Node):
    def __init__(self, var_name: TypeType, expr: Expr):
        self._value = (var_name, expr)
        self._name = self.__class__.__name__


class DeclareAssign(Node):
    def __init__(
        self,
        var_name: Id,
        var_type: TypeType,
        expr: Expr,
    ):
        self._value = (var_name, var_type, expr)
        self._name = self.__class__.__name__


class CallArgs(Node):
    def __init__(self, *args: ArgValuePair | OnlyValue):
        self._values = args
        self._name = self.__class__.__name__


class Call(Node):
    def __init__(self, caller: TypeType, args: CallArgs):
        self._value = (caller, args)
        self._name = self.__class__.__name__


class MethodCallArgs(Node):
    def __init__(self, *args: ArgValuePair | OnlyValue):
        self._values = args
        self._name = self.__class__.__name__


class MethodCall(Node):
    def __init__(self, self_caller: TypeType, args: CallArgs):
        self._value = (self_caller, args)
        self._name = self.__class__.__name__


class InsideOption(Node):
    def __init__(self, option: Expr, body: Body):
        self._value = (option, body)
        self._name = self.__class__.__name__


class CallWithBodyOptions(Node):
    def __init__(
        self,
        *call_options: InsideOption,
        caller: TypeType,
        args: CallArgs,
    ):
        self._value = (caller, args, call_options)
        self._name = self.__class__.__name__


class CallWithArgsBodyOptions(Node):
    def __init__(self, *arg_options: InsideOption, caller: TypeType):
        self._value = (caller, arg_options)
        self._name = self.__class__.__name__


class CallWithBody(Node):
    def __init__(self, caller: TypeType, args: CallArgs, body: Body):
        self._value = (caller, args, body)
        self._name = self.__class__.__name__


class ArgTypePair(Node):
    def __init__(self, arg_name: Id, arg_type: TypeType):
        self._value = (arg_name, arg_type)
        self._name = self.__class__.__name__


class FnArgs(Node):
    def __init__(self, *args: ArgTypePair):
        self._values = args
        self._name = self.__class__.__name__


class FnDef(Node):
    def __init__(
        self,
        fn_name: Id,
        fn_type: TypeType,
        args: FnArgs,
        body: Body,
    ):
        self._value = (fn_name, fn_type, args, body)
        self._name = self.__class__.__name__


class TypeMember(Node):
    def __init__(self, member_name: Id, member_type: TypeType):
        self._value = (member_name, member_type)
        self._name = self.__class__.__name__


class SingleTypeMember(Node):
    def __init__(self, member_type: TypeType):
        self._value = (member_type,)
        self._name = self.__class__.__name__


class EnumTypeMember(Node):
    def __init__(self, member_name: Id):
        self._value = (member_name,)
        self._name = self.__class__.__name__


class TypeDef(Node):
    def __init__(
        self,
        *members: TypeMember | SingleTypeMember | EnumTypeMember,
        type_name: TypeType,
        type_ds: Id,
    ):
        self._value = (type_name, type_ds, members)
        self._name = self.__class__.__name__


class TypeImport(Node):
    def __init__(self, type_list: tuple[Id | CompositeId | CompositeIdWithClosure]):
        self._value = type_list
        self._name = self.__class__.__name__


class FnImport(Node):
    def __init__(self, fn_list: tuple[Id | CompositeId | CompositeIdWithClosure]):
        self._value = fn_list
        self._name = self.__class__.__name__


class Imports(Node):
    """
    Importing types and then functions to the program.
    """

    def __init__(
        self, *, type_import: tuple[TypeImport, ...], fn_import: tuple[FnImport, ...]
    ):
        self._value = (type_import, fn_import)
        self._name = self.__class__.__name__


class Body(Node):
    """
    Body of a closure.
    """

    def __init__(self, *body: BodyType):
        self._values = body
        self._name = self.__class__.__name__


class Main(Node):
    """
    The `main` closure, where the main execution lives.
    """

    def __init__(self, *body: AST):
        self._value = body
        self._name = self.__class__.__name__


class Program(Node):
    def __init__(self, *, main: Main, imports: Imports):
        self._value = (imports, main)
        self._name = self.__class__.__name__


#####################
# DESCRIPTIVE TYPES #
#####################

ValueType = Id | CompositeId | ModifiedId | Literal | Array | Hash

TypeType = Id | CompositeId | ModifiedId

BodyType = (
    Call
    | CallWithBody
    | CallWithBodyOptions
    | Expr
    | MethodCall
    | Declare
    | Assign
    | DeclareAssign
    | Array
    | Hash
    | Literal
    | Id
)
