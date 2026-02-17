use crate::ir::ids::{ExprId, LiteralId, SymbolId};


pub enum MetaCallKind {
    /// Option (cases) meta-function
    Optn,
    /// Body (blocks) meta-function
    Bdn,
    /// Option-body (cases-blocks) meta-function
    OptBdn,
}


pub enum MIRStmt {
    Declare {
        name: SymbolId,
        ty: MIRTypeName,
        modifiers: MIRModifiers,
    },
    Assign(MIRAssign),
    DeclareAssign {
        name: SymbolId,
        ty: MIRTypeName,
        modifiers: MIRModifiers,
        assign: MIRAssign,
    },
    Expr(MIRExpr),
    Return(MIRExpr),
}


/// Keep kinds of types enumerated:
/// - plain
/// - array
/// - generic
/// - generic array
///
pub enum MIRTypeKind {
    /// Usual simple and plain type with no extra annotations, ex: `u32`
    Plain,
    /// Type as in `[u32]`
    Array,
    /// Type as in `?T`
    Generic,
    /// Type as in `[?V]`
    GenericArray,
}


pub struct MIRTypeName {
    name: SymbolId,
    ty_kind: MIRTypeKind,
    modifiers: MIRModifiers,
}


/// Hold MIR modifiers:
/// ```
/// some-instance<some-mdfr other-mdfr=some-value>
/// ```
///
pub struct MIRModifiers {
    value: Vec<MIRExpr>,
}


pub enum MIRExpr {
    Id(SymbolId, Option<MIRModifiers>),
    Literal(LiteralId, Option<MIRModifiers>),
    Call {
        name: SymbolId,
        args: thin_vec::ThinVec<Box<MIRExpr>>,
        modifiers: Option<MIRModifiers>,
    },
    MetaCall(SymbolId, MetaCallKind),
    Cast {
        value: Box<MIRExpr>,
        to_ty: MIRTypeName,
        modifiers: Option<MIRModifiers>,
    },
    DataMember(Box<MIRExpr>, Option<MIRModifiers>),
}


pub enum MIRAssign {
    /// ```
    /// x = y
    /// ```
    Simple { name: SymbolId, value: MIRExpr },
    /// ```
    /// x.a = y
    /// x.a.{A=z B=w}
    /// ```
    /// etc.
    Member { name: SymbolId, member_value: Box<MIRAssign> },
    /// ```
    /// x.{a=y b=z}
    /// x.{a.{A=z1 B=z2} b.{C=z3 D=z4}}
    /// ```
    /// etc.
    Struct(Vec<MIRAssign>),
}


pub enum MIRTypeDef {
    Struct {
        ty: SymbolId,
        members: Vec<MIRStructMember>,
    },
    Enum {
        ty: SymbolId,
        variants: MIREnumVariants,
    }
}


pub struct MIRStructMember(SymbolId, MIRTypeName);

pub enum MIREnumVariants {
    SingleValue(SymbolId),
    StructValue { name: SymbolId, members: Vec<MIRStructMember> },
}
