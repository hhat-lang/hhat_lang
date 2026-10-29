use lasso::Spur;
use crate::ir::hir::behavioral::lex::Span;


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Program {
    imports: Vec<Import>,
    behavioral: Vec<Behavioral>,
    main: Option<Main>,
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Import {
    Type(ImportEntity),
    Fn(ImportEntity),
    MetaFn(ImportEntity),
    Modifier(ImportEntity),
    SuperType(ImportEntity),
    Const(ImportEntity),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct ImportEntity {
    path: Vec<SimpleId>,
    entity: SimpleId,
    span: Span,
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Behavioral {
    Fn(FnDef),
    MetaFn(),
    Modifier(),
    SuperType(),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Main {
    body: Vec<Body>,
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Body {
    DeclareAssign(),
    DeclareAssignDS(),
    Declare(),
    Assign(),
    AssignDS(),
    Expr(),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct FnDef {
    pub name: SimpleId,
    pub args: FnArgs,
    pub ty: Option<TyId>,
    pub body: Vec<FnBody>,
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct FnArgs {
    pub args: Vec<ArgType>,
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct CallArgs {
    pub name: SimpleId,
    pub value: ValOnly,
    pub span: Span,
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum ValOnly {
    Array(),
    Literal(Literal),
    FullId(FullId),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Modifier {
    pub values: Vec<(ModifierValue, Option<Modifier>)>,
    pub span: Span,
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum ModifierValue {
    Ref,
    Pointer,
    Variadic,
    CallArgs(CallArgs),
    Id(SimpleId),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct SimpleId(pub Spur, pub Span);

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum TyId {
    ArrayId(FullId),
    Id(FullId),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum FnBody {
    Return(Expr),
    DeclareAssign(DeclareAssign),
    DeclareAssignDS(DeclareAssignDS),
    Declare(Declare),
    Assign(Assign),
    AssignDS(AssignDS),
    Expr(Expr),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Expr {
    Cast(Cast),
    Literal(Literal),
    Array(Array),
    Access(Access),
    CallOptn(CallOptn),
    CallOptBdn(CallOptBdn),
    CallBdn(CallBdn),
    Call(Call),
    FullId(FullId),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct DeclareAssign {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct DeclareAssignDS {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Declare {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Assign {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct AssignDS {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Cast {
    pub value: CastValue,
    pub ty: TyId,
    pub modifier: Option<Modifier>,
    pub span: Span,
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum CastValue {
    Access(Access),
    Call(Call),
    Literal(Literal),
    FullId(FullId),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Array {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Access {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct CallOptn {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct CallOptBdn {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct CallBdn {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Call {

}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Literal {
    pub value: LiteralT,
    pub modifier: Option<Modifier>,
    pub span: Span,
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum LiteralT {
    Bool(Spur, Span),
    Int(Spur, Span),
    Float { whole: (Spur, Span), mantissa: (Spur, Span), span: Span },
    Str(Vec<StrSeq>, Span),
}

impl LiteralT {
    pub fn into_index(self) -> Option<IdField> {
        match self {
            LiteralT::Int(s, sp) => Some(IdField::Index(s, sp)),
            _ => None,
        }
    }
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum StrSeq {
    Text(Spur, Span),
    Var(SimpleId),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct FullId {
    pub root: SimpleId,
    pub fields: Vec<IdField>,
    pub modifier: Option<Modifier>,
    pub span: Span,
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum IdField {
    Name(SimpleId),
    Index(Spur, Span),
}


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct ArgType {
    pub name: SimpleId,
    pub ty: SimpleId,
    pub modifier: Option<Modifier>,
    pub span: Span,
}

