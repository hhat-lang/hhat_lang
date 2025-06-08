from __future__ import annotations

from arpeggio import NonTerminal, PTNodeVisitor, SemanticActionResults, Terminal

from hhat_lang.core.code.ast import AST
from hhat_lang.dialects.heather.code.ast import (
    ArgTypePair,
    ArgValuePair,
    CompositeId,
    CompositeIdWithClosure,
    CompositeLiteral,
    EnumTypeMember,
    FnDef,
    FnImport,
    Id,
    Imports,
    Literal,
    Main,
    ManyTypeImport,
    ModifiedId,
    Modifier,
    Program,
    SingleTypeMember,
    TypeDef,
    TypeImport,
    TypeMember,
)


class ParserVisitor(PTNodeVisitor):
    def visit_program(self, _: NonTerminal, child: SemanticActionResults) -> AST:
        imports: Imports | None = None
        types: tuple | tuple[TypeDef] = ()
        fns: tuple | tuple[FnDef] = ()
        main: Main | None = None

        for k in child:
            match k:
                case Imports():
                    imports = k

                case TypeDef():
                    types += (k,)

                case FnDef():
                    fns += (k,)

                case Main():
                    main = k

                case _:
                    raise ValueError(f"something went wrong! {k} ({type(k)})")

        return Program(
            main=main,
            imports=imports,
            types=types or None,
            fns=fns or None,
        )

    def visit_type_file(self, _: NonTerminal, child: SemanticActionResults) -> AST:
        if all(isinstance(k, TypeDef) for k in child):
            return child[0]

        raise ValueError("types must be TypeDef instance.")

    def visit_typesingle(self, _: NonTerminal, child: SemanticActionResults) -> AST:
        if isinstance(child[0], Id) and isinstance(child[1], Id):
            return TypeDef(
                SingleTypeMember(child[1]), type_name=child[0], type_ds=Id("single")
            )

        raise ValueError("type single wrong value")

    def visit_typemember(self, _: NonTerminal, child: SemanticActionResults) -> AST:
        if isinstance(child[0], Id) and isinstance(
            child[1], Id | CompositeId | ModifiedId
        ):
            return TypeMember(member_name=child[0], member_type=child[1])

        raise ValueError("type single wrong value")

    def visit_typestruct(self, _: NonTerminal, child: SemanticActionResults) -> AST:
        name, *members = child
        return TypeDef(*members, type_name=name, type_ds=Id("struct"))

    def visit_typeenum(self, _: NonTerminal, child: SemanticActionResults) -> AST:
        name, *members = child
        return TypeDef(*members, type_name=name, type_ds=Id("enum"))

    def visit_typeunion(self, _: NonTerminal, child: SemanticActionResults) -> AST:
        raise NotImplementedError()

    def visit_enummember(self, _: NonTerminal, child: SemanticActionResults) -> AST:
        return EnumTypeMember(member_name=child[0])

    def visit_id_composite_value(
        self, _: NonTerminal, child: SemanticActionResults
    ) -> AST:
        """Get the value to form the type member for arguments and type definitions"""
        return child[0]

    def visit_imports(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        """
        Take the tuple of optional type imports and function imports and place
        inside the `Imports` object, to be properly handled later by the type and
        function checkers and importers.
        """

        type_import: tuple | tuple[TypeImport] = ()
        fn_import: tuple | tuple[FnImport] = ()

        for k in child:
            match k:
                case TypeImport():
                    type_import += (k,)

                case FnImport():
                    fn_import += (k,)

        return Imports(type_import=type_import, fn_import=fn_import)

    def visit_typeimport(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        types: tuple | tuple[Id | CompositeId | CompositeIdWithClosure] = ()

        for k in child:
            match k:
                case Id() | CompositeId() | CompositeIdWithClosure():
                    types += (k,)

                case _:
                    raise ValueError("something went wrong when defining type import.")

        return TypeImport(type_list=types)

    def visit_fnimport(
        self, node: NonTerminal | None, child: SemanticActionResults
    ) -> AST:
        fns: tuple | tuple[Id | CompositeId | CompositeIdWithClosure] = ()

        for k in child:
            match k:
                case Id() | CompositeId() | CompositeIdWithClosure():
                    fns += (k,)

                case _:
                    raise ValueError("something went wrong when defining type import.")

        return FnImport(fn_list=fns)

    def visit_single_import(
        self, node: NonTerminal | Terminal, child: SemanticActionResults
    ) -> AST:
        """simply return the import AST"""

        return tuple(k for k in child)[0]

    def visit_many_import(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        return ManyTypeImport(*child)

    def visit_main(self, _: NonTerminal, child: SemanticActionResults) -> AST:
        return Main(*child)

    def visit_composite_id_with_closure(
        self, _: NonTerminal | Terminal, child: SemanticActionResults
    ) -> AST:
        """
        Get an Id and its dependencies, ex:

        ```python
        math.{add sub mul div}
        ```

        """

        name, *deps = tuple(k for k in child)
        return CompositeIdWithClosure(*deps, name=name)

    def visit_id(
        self, node: NonTerminal | Terminal, child: SemanticActionResults
    ) -> AST:
        if len(child) == 2 and isinstance(child[1], Modifier):
            return ModifiedId(name=child[0], modifier=child[1])

        return child[0]

    def visit_modifier(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        if all(isinstance(k, ArgValuePair) for k in child):
            return Modifier(*child)

        raise ValueError(
            f"Modifier should have had ArgValuePair, got {set(type(k) for k in child)} instead."
        )

    def visit_trait_id(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        raise NotImplementedError()

    def visit_call(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        raise NotImplementedError()

    def visit_args(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        raise NotImplementedError()

    def visit_callargs(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        raise NotImplementedError()

    def visit_valonly(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        raise NotImplementedError()

    def visit_array(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        raise NotImplementedError()

    def visit_composite_id(
        self, node: NonTerminal, child: SemanticActionResults
    ) -> AST:
        if all(isinstance(k, Id) for k in child):
            return CompositeId(*child)

        raise ValueError(
            f"CompositeId must contain Id values; got {set(type(k) for k in child)} instead."
        )

    def visit_simple_id(self, node: Terminal, _: SemanticActionResults) -> AST:
        return Id(node.value)

    def visit_literal(self, _: Terminal, child: SemanticActionResults) -> AST:
        return child[0]

    def visit_null(self, node: Terminal, _: None) -> AST:
        return Literal(value=node.value, value_type="null")

    def visit_bool(self, node: Terminal, _: None) -> AST:
        return Literal(value=node.value, value_type="bool")

    def visit_str(self, node: Terminal, _: None) -> AST:
        return Literal(value=node.value, value_type="str")

    def visit_int(self, node: Terminal, _: None) -> AST:
        return Literal(value=node.value, value_type="int")

    def visit_float(self, node: Terminal, _: None) -> AST:
        return Literal(value=node.value, value_type="float")

    def visit_imag(self, node: Terminal, _: None) -> AST:
        return Literal(value=node.value, value_type="imag")

    def visit_complex(self, node: Terminal, child: SemanticActionResults) -> AST:
        return CompositeLiteral(*child, value_type="complex")

    def visit_q__bool(self, node: Terminal, _: None) -> AST:
        return Literal(value=node.value, value_type="@bool")

    def visit_q__int(self, node: Terminal, _: None) -> AST:
        return Literal(value=node.value, value_type="@int")
