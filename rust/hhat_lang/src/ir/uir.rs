//! Unresolved Intermediate Representation (IR) for H-hat's Heather dialect.
//! This is the first IR generated out of the raw text.
//!

use crate::ir::ids::Paradigm;


/// Identifier for unresolved IR.
///
pub struct Id {
    pub value: String,
    pub paradigm: Paradigm,
}

impl Id {
    pub fn new(value: String, paradigm: Paradigm) -> Self {
        Self { value, paradigm }
    }
}


/// Composite identifier for unresolved IR.
///
pub struct CompositeId {
    pub value: Vec<Id>,
    pub paradigm: Paradigm
}

impl CompositeId {
    pub fn new(value: Vec<Id>, paradigm: Paradigm) -> Self {
        Self { value, paradigm }
    }
}


/// Unresolved imports.
/// Includes constants, types, functions, modifiers, meta-functions.
///
/// Imports cannot have alias for now, so constants and types
/// must have unique names.
///
pub enum UnresolvedImports {
    Consts(Vec<CompositeId>),
    Types(Vec<CompositeId>),
    Fns(Vec<CompositeId>),
    Modifiers(Vec<CompositeId>),
    MetaFns(Vec<CompositeId>),
}


/// Constant definition for unresolved IR.
///
/// It must exist in a constants-only file.
///
pub struct UConstDef {
    pub name: Id,
    pub ty: UTypeName,
    pub modifiers: Vec<UModifier>,
}


/// Unresolved literal object.
///
/// Any given platform can define its own literals:
/// ```rust
/// Int(7, Paradigm::CPU)  // 7 on CPU
/// Int(3, Paradigm::QPU)  // @3, syntax sugar for 3 on QPU
/// ```
pub enum ULiteral {
    Bool(bool, Paradigm),
    Int(i64, Paradigm),
    Float(f64, Paradigm),
    Str(String, Paradigm),
}


/// Expression for unresolved IR.
///
pub enum UExpr {
    Id(Id),
    CompositeId(CompositeId),
    Literal(ULiteral),
    Call {
        callee: CompositeId,
        args: Vec<UExpr>,
        modifiers: Vec<UModifier>,
    },
    MetaCall(MetaCall),
    Cast {
        value: Box<UExpr>,
        to_ty: UTypeName,
        modifiers: Vec<UModifier>,
    },
}


pub enum MetaCall {
    /// Option functions (cases).
    ///
    /// Syntax: `name(option:{body} ...)`
    Optn {
        name: Id,
        options: Vec<UOptionBody>,
        modifiers: Vec<UModifier>,
    },
    /// Body functions (blocks).
    ///
    /// Syntax: `name(args*){body}`
    Bdn {
        name: Id,
        args: Vec<UExpr>,
        body: UBlock,
        modifiers: Vec<UModifier>,
    },
    /// Option-body functions (case-blocks).
    ///
    /// Syntax: `name(args*){option:{body} ...}`
    OptBdn {
        name: Id,
        args: Vec<UExpr>,
        body: Vec<UOptionBody>,
        modifiers: Vec<UModifier>,
    },
}


pub struct UOptionBody {
    pub opt: UExpr,
    pub body: UBlock,
}


/// Modifiers calls for unresolved IR.
///
/// It can be no-arg modifiers (`<&>`, `<mut>`) or
/// single-arg modifiers (`<shots=1000>`, `<device=qiskit.aer-sim>`).
///
pub struct UModifier {
    pub name: Id,
    pub value: Option<UExpr>,
}

pub struct UStruct {
    pub name: Id,
    pub members: Vec<UStructMember>,
    pub modifiers: Vec<UModifier>,
}


pub struct UStructMember {
    pub name: Id,
    pub ty: UTypeName
}


/// Type name for unresolved IR.
/// It contains the name (as a [`CompositeId`]) and its
/// paradigm (as a [`Paradigm`]).
///
pub struct UTypeName {
    pub name: CompositeId,
    pub paradigm: Paradigm,
}


pub enum UEnumMember {
    /// Enum member as a single value: `enum status { ON, OFF }`
    KindMember { name: Id },
    StructMember(UStruct),
}


/// Type definition for unresolved IR.
///
/// It must exist in a types-only file.
///
pub enum UTypeDef {
    Struct(UStruct),
    Enum {
        name: Id,
        members: Vec<UEnumMember>,
        modifiers: Vec<UModifier>,
    },

}


/// Group of definitions for unresolved IR.
///
/// They are: functions (including `cast` functions),
/// modifiers and meta-functions definitions. They can
/// co-exist in the same file.
///
pub enum UGroupsDef {
    UFnDef(UFnDef),
    UModifierDef(UModifierDef),
    UMetaFnDef(UMetaFnDef),
}


/// Function definition for unresolved IR.
///
pub struct UFnDef {
    pub name: Id,
    pub params: Vec<UParam>,
    pub ty: UTypeName,
    pub modifiers: Vec<UModifier>,
    pub body: UBlock,
}


pub struct UParam {
    pub name: Id,
    pub ty: UTypeName,
    pub modifiers: Vec<UModifier>,
}


/// Block of code for unresolved IR.
///
pub struct UBlock(Vec<UStmt>);


/// Statements for unresolved IR.
///
pub enum UStmt {
    Declare {},
    Assign {},
    DeclareAssign {},
    Expr(UExpr),
    Return(Option<UExpr>),
}


/// Modifier definition for unresolved IR.
///
pub struct UModifierDef {

}


/// Meta-function definition for unresolved IR.
///
pub struct UMetaFnDef {

}


/// File content for unresolved IR.
///
/// It can be either constants ([`UConstDef`]), types ([`UTypeDef`])
/// or groups ([`UGroupsDef`]). Each one of these contents must not
/// be mixed with the others within the same file.
///
pub enum UContent {
    Consts(Vec<UConstDef>),
    Types(Vec<UTypeDef>),
    Groups(Vec<UGroupsDef>),
}
