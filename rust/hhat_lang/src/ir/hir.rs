//! High-level Intermediate Representation (HIR) for H-hat's Heather dialect.
//! This is the first IR generated out of the raw text.
//!

use std::borrow::Borrow;
use std::fmt::{Display, Formatter};
use crate::ir::ids::{BackendKind, ExprId, Path};
use itertools::Itertools;


/// Identifier for HIR.
///
pub struct Symbol {
    pub value: String,
    pub backend_kind: BackendKind,
}

impl Display for Symbol {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}{}", self.backend_kind.sugar_fmt(), self.value)
    }
}

impl Symbol {
    pub fn new(value: String, backend_kind: BackendKind) -> Self {
        Self { value, backend_kind }
    }
}


/// Composite identifier for HIR.
///
/// Can be used for calling enums, for instance.
///
pub struct CompositeSymbol {
    pub value: Vec<Symbol>,
}

impl Display for CompositeSymbol {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.value
            .iter()
            .map(|x| format!("{}{}", x.backend_kind.sugar_str(), x.value.as_str()))
            .format(".")
        )
    }
}


impl CompositeSymbol {
    pub fn new(value: Vec<Symbol>) -> Self {
        Self { value }
    }
}


/// Symbols with path for importing purposes for HIR.
///
pub struct ImportPathSymbol {
    pub name: Symbol,
    pub path: Path,
}

impl Display for ImportPathSymbol {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let glue_path_name: String = String::from(
            if self.path.len() > 0 { "." } else { "" }
        );
        write!(f, "{}{}{}", self.path, glue_path_name, self.name)
    }
}

impl ImportPathSymbol {
    pub fn new(name: Symbol, path: Path) -> Self {
        Self { name, path }
    }
}


/// HIR imports.
///
/// Includes constants, types, functions, modifiers, meta-functions.
///
/// Imports cannot have alias for now, so constants and types
/// must have unique names.
///
pub enum Imports {
    Consts(Vec<ImportPathSymbol>),
    Types(Vec<ImportPathSymbol>),
    Fns(Vec<ImportPathSymbol>),
    Modifiers(Vec<ImportPathSymbol>),
    MetaFns(Vec<ImportPathSymbol>),
}


/// Constant definition for HIR.
///
/// It must exist in a constants-only file.
///
pub struct ConstDef {
    pub name: Symbol,
    pub ty: TypeName,
    pub modifiers: Vec<Modifier>,
}


/// HIR literal object.
///
/// Any given platform can define its own literals:
/// ```rust
/// Int(7, BackendKind::CPU)  // 7 on CPU
/// Int(3, BackendKind::QPU)  // @3, syntax sugar for 3 on QPU
/// ```
pub enum Literal {
    Bool(bool, BackendKind),
    Int(i64, BackendKind),
    Float(f64, BackendKind),
    Str(String, BackendKind),
}


/// Expression for HIR.
///
pub enum Expr {
    Id(Symbol),
    Literal(Literal),
    /// Function call
    Call {
        callee: Symbol,
        args: Vec<Expr>,
        modifiers: Vec<Modifier>,
    },
    /// Meta-function call
    MetaCall(MetaCall),
    /// Cast call
    Cast {
        value: Box<Expr>,
        to_ty: Box<TypeName>,
        modifiers: Vec<Modifier>,
    },
    /// Get value from struct/enum: `var.member1`, `var.{member1 member2}`, so on
    DataMemberAccess(CompositeSymbol),
}


/// Meta-function calls:
/// - [`MetaCall::Optn`] (option/cases functions)
/// - [`MetaCall::Bdn`] (body/blocks functions)
/// - [`MetaCall::OptBdn`] (option-body/case-block functions)
///
pub enum MetaCall {
    /// Option functions (cases).
    ///
    /// Syntax: `name(option:{body} ...)`
    Optn {
        name: Symbol,
        options: Vec<OptionBody>,
        modifiers: Vec<Modifier>,
    },
    /// Body functions (blocks).
    ///
    /// Syntax: `name(args*){body}`
    Bdn {
        name: Symbol,
        args: Vec<Expr>,
        body: Block,
        modifiers: Vec<Modifier>,
    },
    /// Option-body functions (case-blocks).
    ///
    /// Syntax: `name(args*){option:{body} ...}`
    OptBdn {
        name: Symbol,
        args: Vec<Expr>,
        body: Vec<OptionBody>,
        modifiers: Vec<Modifier>,
    },
}


/// Option + body for HIR.
///
/// Syntax: `opt:{body}`
///
pub struct OptionBody {
    pub opt: Expr,
    pub body: Block,
}


/// Modifiers calls for HIR.
///
/// It can be no-arg modifiers (`<&>`, `<mut>`) or
/// single-arg modifiers (`<shots=1000>`, `<device=qiskit.aer-sim>`).
///
pub struct Modifier {
    pub name: Symbol,
    pub value: Option<Expr>,
}

pub struct StructDef {
    pub name: Symbol,
    pub members: Vec<StructMember>,
    pub modifiers: Vec<Modifier>,
}


pub struct StructMember {
    pub name: Symbol,
    pub ty: TypeName
}


/// Type name for HIR.
///
/// It contains the name (as a [`Symbol`]) and its
/// backend kind (as a [`BackendKind`]).
///
pub struct TypeName {
    pub name: Symbol,
    pub modifiers: Modifier,
}


pub enum EnumMember {
    /// Enum member as a single value:
    ///
    /// `enum status { ON, OFF }` -> `status.ON`, `status.OFF`
    KindMember(Symbol),
    /// Enum member as a struct:
    ///
    /// `enum color { rgb{r:u8 g:u8 b:u8} hex{value:u32} }` ->
    /// `color.rgb`, `color.hex` ->
    /// `color.rgb.r`, `color.rgb.g`, `color.rgb.b`, etc.
    StructMember(StructDef),
}

pub enum PrimitiveDef {
    BOOL,
    U32,
    U64,
    I32,
    I64,
    F32,
    F64,
    STR
}


/// Type definition for HIR.
///
/// It must exist in a types-only file.
///
pub enum TypeDef {
    PrimitiveDef(PrimitiveDef),
    StructDef(StructDef),
    EnumDef {
        name: Symbol,
        members: Vec<EnumMember>,
        modifiers: Vec<Modifier>,
    },
    /// Possibly to use for function types (`fn_t`,
    /// `optn_t`, `bdn_t`, `optbdn_t`), variable
    /// type (`var_t`), etc.
    NamedType {
        name: Symbol
    },
}


/// Group of definitions for HIR.
///
/// They are: functions (including `cast` functions),
/// modifiers and meta-functions definitions. They can
/// co-exist in the same file.
///
pub enum GroupsDef {
    FnDef(FnDef),
    ModifierDef(ModifierDef),
    MetaFnDef(MetaFnDef),
}


/// Function definition for HIR.
///
pub struct FnDef {
    pub name: Symbol,
    pub params: Vec<Param>,
    pub ty: TypeName,
    pub modifiers: Vec<Modifier>,
    pub body: Block,
}


pub struct Param {
    pub name: Symbol,
    pub ty: TypeName,
    pub modifiers: Vec<Modifier>,
}


/// Block of code for HIR.
///
pub struct Block(Vec<Stmt>);


pub enum Assign {
    Single {
        name: Symbol,
        value: Expr,
        modifiers: Vec<Modifier>,
    },
    Struct {
        ty: Option<Symbol>,
        members: Vec<StructMembersInit>,
    },
    Enum {
        ty: Symbol,
        members: EnumMembersInit,
    },
}

pub struct DeclareAssign {
    name: Symbol,

}


pub struct StructMembersInit {
    name: Symbol,
    value: Expr,
}


pub enum EnumMembersInit {
    EnumMember(),
    StructMember(),
}


pub enum AssignDef {
    SingleMemberAssign,
    FullAssign,
}


/// Statements for HIR.
///
pub enum Stmt {
    Declare {
        name: Symbol,
        ty: TypeName,
        modifiers: Vec<Modifier>,
    },
    Assign(Assign),
    DeclareAssign {
        name: Symbol,
        ty: TypeName,
        modifiers: Vec<Modifier>,
        value: Expr,
    },
    Expr(Expr),
    Return(Expr),
}


/// Modifier definition for HIR.
///
pub struct ModifierDef {
    pub name: Symbol,
    pub params: [Option<Param>; 2],
    pub modifiers: Vec<Modifier>,
    pub body: Block,

}


/// Meta-function definition for HIR.
///
pub struct MetaFnDef {
    pub name: Symbol,
    pub params: Vec<Param>,
    pub modifiers: Vec<Modifier>,
    pub body: Block,
}


/// File content for HIR.
///
/// It can be either constants ([`ConstDef`]), types ([`TypeDef`])
/// or groups ([`GroupsDef`]). Each one of these contents must not
/// be mixed with the others within the same file.
///
pub enum Content {
    Consts(Vec<ConstDef>),
    Types(Vec<TypeDef>),
    Groups(Vec<GroupsDef>),
}
