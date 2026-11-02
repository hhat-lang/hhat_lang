use lasso::Spur;
use crate::ir::hir::behavioral::lex::Span;


pub struct Module {

}


/// For the unresolved HIR. Contains the lowest 
/// representation of a code after the source is tokenized.
/// 
pub mod unresolved {
    use lasso::Spur;
    use crate::ir::hir::behavioral::lex::Span;

    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct Program {
        pub imports: Vec<Import>,
        pub behavioral: Vec<Behavioral>,
        pub main: Option<Main>,
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


    /// Behavioral is either function, metafunction, modifier, super-type.
    /// 
    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub enum Behavioral {
        Fn(FnDef),
        MetaFn(MetaFnDef),
        Modifier(ModifierDef),
        SuperType(SuperTypeDef),
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct Main {
        pub body: Vec<Body>,
        pub span: Span,
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub enum Body {
        DeclareAssign(DeclareAssign),
        DeclareAssignDS(DeclareAssignDS),
        Declare(Declare),
        Assign(Assign),
        AssignDS(AssignDS),
        Expr(Expr),
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct FnDef {
        pub name: SimpleId,
        pub args: FnArgs,
        pub ty: Option<TyId>,
        pub body: Vec<FnBody>,
        pub span: Span,
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
    pub enum DSInit {
        Named(Vec<Assign>),
        Positional(Vec<Expr>),
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct DeclareAssign {
        pub name: SimpleId,
        pub ty_id: TyId,
        pub expr: Expr,
        pub modifier: Option<Modifier>,
        pub span: Span,
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct DeclareAssignDS {
        pub name: SimpleId,
        pub ty_id: TyId,
        pub init: DSInit,
        pub modifier: Option<Modifier>,
        pub span: Span,
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct Declare {
        pub name: SimpleId,
        pub ty_id: TyId,
        pub modifier: Option<Modifier>,
        pub span: Span,
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct Assign {
        pub name: FullId,
        pub expr: Expr,
        pub span: Span,
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct AssignDS {
        pub name: FullId,
        pub init: DSInit,
        pub span: Span,
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
        pub value: Vec<ValOnly>,
        pub span: Span,
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct Access {
        pub callable: Callable,
        pub member: Vec<Member>,
        pub span: Span,
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub enum Callable {
        CallOptn(CallOptn),
        CallOptBdn(CallOptBdn),
        CallBdn(CallBdn),
        Call(Call),
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub enum Member {
        SimpleId(SimpleId),
        IntT(Literal),
        Args(Vec<Args>),
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct CallOptn {}


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct CallOptBdn {}


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct CallBdn {}


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct Call {
        pub name: FullId,
        pub args: Vec<Args>,
        pub modifier: Option<Modifier>,
        pub span: Span,
    }


    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub enum Args {
        Cast(Cast),
        Literal(Literal),
        Array(Array),
        Access(Access),
        Call(Call),
        ValOnly(ValOnly),
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


}