use chumsky;
use chumsky::error::Rich;
use chumsky::{extra, Parser, select, IterParser};
use chumsky::input::{MappedInput, ValueInput};
use chumsky::prelude::recursive;
use chumsky::primitive::{just, choice, todo};
use lasso::Spur;
use crate::ir::hir::behavioral::base::{Access, ArgType, Array, Assign, AssignDS, Call, CallArgs, CallBdn, CallOptBdn, CallOptn, Cast, CastValue, Declare, DeclareAssign, DeclareAssignDS, Expr, FnArgs, FnBody, FnDef, FullId, IdField, Literal, LiteralT, Modifier, ModifierValue, SimpleId, StrSeq, TyId, ValOnly};
use crate::ir::hir::behavioral::lex::{Span, StrToken, Token};


//=======================================
//
// Start of Definitions
//
// - to avoid repetition

type Extra<'t> = extra::Err<Rich<'t, Token, Span>>;
type In<'t> = MappedInput<'t, Token, Span, &'t [(Token, Span)]>;

trait Rule<'t, O>: Parser<'t, In<'t>, O, Extra<'t>> + Clone {}
impl<'t, O, P: Parser<'t, In<'t>, O, Extra<'t>> + Clone> Rule<'t, O> for P {}


//
// End of Definitions
//
//=======================================


//=======================================
//
// Start of Parser
//


fn bool_t<'t>() -> impl Rule<'t, LiteralT> {
    select! { Token::BoolT(t) = e => LiteralT::Bool(t, e.span()) }
        .labelled("bool_t")
}

fn int_t<'t>() -> impl Rule<'t, LiteralT>{
    select! { Token::IntT(t) = e => LiteralT::Int(t, e.span()) }
        .labelled("int_t")
}

fn float_t<'t>() -> impl Rule<'t, LiteralT> {
    select! { Token::FloatT(f) = e => {
        LiteralT::Float {
            whole: f.whole,
            mantissa: f.mantissa,
            span: e.span()
        }}}.labelled("int_t")
}

fn str_t<'t>() -> impl Rule<'t, LiteralT> {
    select! { Token::StrT(t) = e => LiteralT::Str(
        t.into_iter()
            .map(|(stok, s)| match stok {
                StrToken::Text(p) => StrSeq::Text(p, s),
                StrToken::Ident(p) => StrSeq::Var(SimpleId(p, s)),
                StrToken::EndQuote => unreachable!("lexer should not store quotes."),
            }).collect::<Vec<StrSeq>>(),
            e.span()
    )}.labelled("str_t")
}


/// ```
/// literal = (bool_t | float_t | int_t | str_t ) modifier?
/// ```
///
fn literal<'t>() -> impl Rule<'t, Literal> {
    literal_modifier(modifier())
}


/// To be used when literal is called inside the modifier function
/// and avoid infinite recursion.
///
/// ```
/// literal = (bool_t | float_t | int_t | str_t ) modifier?
/// ```
///
fn literal_modifier<'t>(modifier: impl Rule<'t, Modifier>) -> impl Rule<'t, Literal> {
    choice((bool_t(), int_t(), float_t(), str_t()))
    .then(modifier.or_not())
    .map_with(|(value, m), e| Literal { value,  modifier: m, span: e.span() } )
    .labelled("literal")
}


/// ```
/// simple_id = r"(\@)?[a-zA-Z_][a-zA-Z0-9\-_]*"
/// ```
///
fn simple_id<'t>() -> impl Rule<'t, SimpleId> {
    select! { Token::Ident(s) => s }
        .map_with(|s, e| SimpleId(s, e.span()))
        .labelled("simple_id")
}


/// ```
/// full_id = simple_id ( "." ( int_t | simple_id ) )* modifier?
/// ```
///
fn full_id<'t>() -> impl Rule<'t, FullId> {
    full_id_modifier(modifier())
}


/// `FullId` for modifier recursion.
///
/// ```
/// full_id = simple_id ( "." ( int_t | simple_id ) )* modifier?
/// ```
///
fn full_id_modifier<'t>(modifier: impl Rule<'t, Modifier>) -> impl Rule<'t, FullId> {
    simple_id()
        .then(just(Token::Dot)
            .ignore_then(choice((
                int_t().filter_map(|lit| lit.into_index().map(|f| vec![f])),
                float_fields(),
                simple_id().map(|id| vec![IdField::Name(id)]),
            )))
            .repeated()
            .fold(Vec::new(), |mut acc, v| { acc.extend(v); acc }))
        .then(modifier.or_not())
        .map_with(|((root, fields), m), e|
            FullId {
                root,
                fields,
                modifier: m,
                span: e.span()
            }
        )
        .labelled("full_id")
}


fn float_fields<'t>() -> impl Rule<'t, Vec<IdField>> {
    select! {
        Token::FloatT(f) => vec![
            IdField::Index(f.whole.0, f.whole.1),
            IdField::Index(f.mantissa.0, f.mantissa.1)
        ]
    }.labelled("int_fields")
}


fn ref_rule<'t>() -> impl Rule<'t, ModifierValue> {
    just(Token::Ref).to(ModifierValue::Ref).labelled("ref")
}


fn ptr_rule<'t>() -> impl Rule<'t, ModifierValue> {
    just(Token::Star).to(ModifierValue::Pointer).labelled("pointer")
}


fn variadic_rule<'t>() -> impl Rule<'t, ModifierValue> {
    just(Token::Ellipsis).to(ModifierValue::Variadic).labelled("variadic")
}


/// ```
/// modifier = "<" ( ( ref | pointer | variadic | callargs | simple_id ) modifier?)+ ">"
/// ```
///
fn modifier<'t>() -> impl Rule<'t, Modifier>{
    recursive(|modif| {
        let value = choice(
            (
                ref_rule(),
                ptr_rule(),
                variadic_rule(),
                callargs_modifier(modif.clone()).map(ModifierValue::CallArgs),
                simple_id().map(ModifierValue::Id)
            )
        );
        value.then(modif.or_not())
            .repeated()
            .at_least(1)
            .collect::<Vec<(ModifierValue, Option<Modifier>)>>()
            .delimited_by(just(Token::LAngle), just(Token::RAngle))
            .map_with(|values, e| Modifier { values, span: e.span() })
        }
    ).labelled("modifier")
}


/// ```
/// callargs = simple_id "=" valonly
/// ```
///
fn callargs<'t>() -> impl Rule<'t, CallArgs> {
    callargs_modifier(modifier())
}


fn callargs_modifier<'t>(modifier: impl Rule<'t, Modifier>) -> impl Rule<'t, CallArgs> {
    simple_id().then_ignore(just(Token::Equal))
        .then(valonly_modifier(modifier))
        .map_with(|(name, value), e| CallArgs { name, value, span: e.span() } )
        .labelled("callargs")
}


/// ```
/// valonly = array | literal | full_id
/// ```
///
fn valonly<'t>() -> impl Rule<'t, ValOnly> {
    valonly_modifier(modifier())
}


fn valonly_modifier<'t>(modifier: impl Rule<'t, Modifier>) -> impl Rule<'t, ValOnly> {
    choice((
        literal_modifier(modifier).map_with(|l, _| ValOnly::Literal(l)),
        full_id().map_with(|f, _| ValOnly::FullId(f))
    )).labelled("valonly")
}

/// ```
/// fn_def = "fn" simple_id fn_args type_id? fn_body
/// ```
///
fn fn_def<'t>() -> impl Rule<'t, FnDef> {
    just(Token::Fn).ignore_then(simple_id())
        .then(fn_args().then(type_id().or_not()))
        .then(fn_body())
        .map_with(|((name, (args, ty)), body), _|
            FnDef { name, args: FnArgs { args }, ty, body }
        ).labelled("fn_def")
}


fn type_id<'t>() -> impl Rule<'t, TyId> {
    choice((
        full_id()
            .delimited_by(just(Token::LBracket), just(Token::RBracket))
            .map_with(|x, _| TyId::ArrayId(x)),
        full_id().map_with(|x, _| TyId::Id(x))
    )).labelled("type_id")
}


fn fn_body<'t>() -> impl Rule<'t, Vec<FnBody>> {
    choice((
        fn_return().map(FnBody::Return),
        declareassign().map(FnBody::DeclareAssign),
        declareassign_ds().map(FnBody::DeclareAssignDS),
        declare().map(FnBody::Declare),
        assign_ds().map(FnBody::AssignDS),
        assign().map(FnBody::Assign),
        expr().map(FnBody::Expr),
    ))
        .repeated()
        .collect::<Vec<FnBody>>()
        .delimited_by(just(Token::LCurl), just(Token::RCurl))
        .labelled("fn_body")
}


/// ```
/// return = :: expr
/// ```
///
fn fn_return<'t>() -> impl Rule<'t, Expr> {
    just(Token::Return).ignore_then(expr().map(|x| x)).labelled("return")
}


fn declareassign<'t>() -> impl Rule<'t, DeclareAssign> {

    todo()
}


fn declareassign_ds<'t>() -> impl Rule<'t, DeclareAssignDS> {

    todo()
}


fn declare<'t>() -> impl Rule<'t, Declare> {

    todo()
}


fn assign_ds<'t>() -> impl Rule<'t, AssignDS> {

    todo()
}


fn assign<'t>() -> impl Rule<'t, Assign> {

    todo()
}


/// ```
/// expr = cast | literal | array | access | call_optn | call_optbdn | call_bdn | call | full_id
/// ```
///
fn expr<'t>() -> impl Rule<'t, Expr> {
    choice((
        cast().map(Expr::Cast),
        literal().map(Expr::Literal),
        array().map(Expr::Array),
        access().map(Expr::Access),
        call_optn().map(Expr::CallOptn),
        call_optbdn().map(Expr::CallOptBdn),
        call_bdn().map(Expr::CallBdn),
        call().map(Expr::Call),
        full_id().map(Expr::FullId),
    )).labelled("expr")
}


fn cast<'t>() -> impl Rule<'t, Cast> {
    cast_value()
        .then_ignore(just(Token::Star))
        .then(modifier().or_not())
        .then(type_id())
        .map_with(|((value, m), ty), e| 
            Cast { value, ty, modifier: m, span: e.span() }
        )
        .labelled("cast")
}


fn cast_value<'t>() -> impl Rule<'t, CastValue> {
    choice((
        access().map(CastValue::Access),
        call().map(CastValue::Call),
        literal().map(CastValue::Literal),
        full_id().map(CastValue::FullId),
    ))
        .labelled("cast_value")
}


fn array<'t>() -> impl Rule<'t, Array> {

    todo()
}


fn access<'t>() -> impl Rule<'t, Access> {

    todo()
}


fn call_optn<'t>() -> impl Rule<'t, CallOptn> {

    todo()
}


fn call_optbdn<'t>() -> impl Rule<'t, CallOptBdn> {

    todo()
}


fn call_bdn<'t>() -> impl Rule<'t, CallBdn> {

    todo()
}


fn call<'t>() -> impl Rule<'t, Call> {

    todo()
}


/// ```
/// fn_args = "(" argtype* ")"
/// ```
///
fn fn_args<'t>() -> impl Rule<'t, Vec<ArgType>>{
    argtype()
        .repeated()
        .collect::<Vec<ArgType>>()
        .delimited_by(just(Token::LParen), just(Token::RParen))
        .labelled("fn_args")
}


/// ```
/// argtype = simple_id modifier? ":" type_id
/// ```
///
fn argtype<'t>() -> impl Rule<'t, ArgType> {
    simple_id().then(modifier().or_not())
        .then_ignore(just(Token::Colon))
        .then(simple_id())
        .map_with(
            |((name, m), ty), e|
                ArgType { name, ty, span: e.span(), modifier: m }
        ).labelled("argtype")
}


//
// End of Parser
//
//=======================================
