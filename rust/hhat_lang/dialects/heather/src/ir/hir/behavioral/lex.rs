use std::fmt::{Debug, Formatter};
use std::ops::Range;
use logos;
use lasso;
use logos::{Lexer, Logos, SpannedIter};
use lasso::{Rodeo, Spur};
use chumsky;
use chumsky::span::Span as SpanTrait;

#[derive(Copy, Clone, PartialEq, Eq, Hash)]
pub struct Span {
    pub start: usize,
    pub end: usize,
}

impl Span {
    pub fn from_range(range: Range<usize>) -> Span {
        Span { start: range.start, end: range.end }
    }
}

impl Debug for Span {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        self.start.fmt(f)?;
        write!(f, "..")?;
        self.end.fmt(f)?;
        Ok(())
    }
}

impl SpanTrait for Span {
    type Context = ();
    type Offset = usize;

    fn new(context: Self::Context, range: Range<Self::Offset>) -> Self {
        Span::from_range(range)
    }

    fn context(&self) -> Self::Context {}

    fn start(&self) -> Self::Offset {
        self.start
    }

    fn end(&self) -> Self::Offset {
        self.end
    }
}


#[derive(Debug, Clone, PartialEq, Default)]
pub enum LexError {
    #[default]
    Unexpected,
    UnterminatedString,
    InvalidString,
}


/// Token for behavioral entities: functions, modifiers, metafunctions and super-types.
///
#[derive(Logos, Clone, Debug, PartialEq)]
#[logos(extras = Rodeo, error = LexError)]
#[logos(skip(r"[ \t\r\n,;]+"))]
pub enum Token {
    #[token("use")]
    Use,
    #[token("type")]
    Type,
    #[token("fn")]
    Fn,
    #[token("metafn")]
    MetaFn,
    #[token("modifier")]
    Modifier,
    #[token("super-type")]
    SuperType,
    #[token("const")]
    Const,
    #[token("main")]
    Main,

    #[token("#ct_init")]
    CTInit,
    #[token("#rt_init")]
    RTInit,
    #[token("#ct_read")]
    CTRead,
    #[token("#rt_read")]
    RTRead,
    #[token("#ct_write")]
    CTWrite,
    #[token("#rt_write")]
    RTWrite,
    #[token("#ct_drop")]
    CTDrop,
    #[token("#rt_drop")]
    RTDrop,

    #[token("(")]
    LParen,
    #[token(")")]
    RParen,
    #[token("[")]
    LBracket,
    #[token("]")]
    RBracket,
    #[token("{")]
    LCurl,
    #[token("}")]
    RCurl,
    #[token("<")]
    LAngle,
    #[token(">")]
    RAngle,

    #[token("=")]
    Equal,
    #[token(":")]
    Colon,
    #[token("::")]
    Return,
    /// `:::` must disambiguate to `:` (option) + `::` (return).
    /// Example:
    ///
    /// ```
    /// some-metafn {
    ///     some-expr: { block }  // clear syntax (expr + option + block)
    ///     other-expr: ::val  // clear syntax (expr + option + return)
    ///     another-expr:::val  // must be expr + option + return
    /// }
    /// ```
    ///
    #[token(":::")]
    OptionAndReturn,

    #[token(".")]
    Dot,
    /// `...` token.
    #[token("...")]
    Ellipsis,
    #[token("&")]
    Ref,
    /// `*` token is either a pointer or a cast (syntax sugar).
    #[token("*")]
    Star,

    #[regex(r"(\@)?[a-zA-Z_][a-zA-Z0-9\-_]*", set_spur)]
    Ident(Spur),
    #[regex(r"\?(\@)?[A-Z_][a-zA-Z0-9\-_]*", set_spur)]
    Generic(Spur),

    #[regex(r"(\@)?(true|false)", set_spur)]
    BoolT(Spur),
    #[regex(r"(\@)?(-)?(0([xX][a-fA-F0-9]+)?|[1-9][0-9]*)", set_spur)]
    IntT(Spur),
    // #[regex(r"(\@)?(-)?(0|[1-9][0-9]*)\.[0-9]+", set_spur)]
    // FloatT(Spur),
    /// Float tokens are tricky: they can mean float numbers (`1.2`)
    /// or chained fields (`var.1.2`). For this reason, float needs
    /// to be disambiguated during parsing time. Token data is kept
    /// separated so it is easier to reason about it at the right time.
    ///
    #[regex(r"(\@)?(-)?(0|[1-9][0-9]*)\.[0-9]+", set_float)]
    FloatT(FloatToken),
    /// As with the float tokens, string tokens are tricky because they
    /// can have variables (`"this is a text"`, `"this has {value}"`).
    /// Keeping a separate lexer for strings and token data help to resolve
    /// them a clear the distinctions right on the beginning, lowering the
    /// burden for later compilation passes.
    ///
    #[token("\"", set_str_block)]
    StrT(Vec<(StrToken, Span)>),
}


fn set_spur(lex: &mut Lexer<Token>) -> Spur {
    lex.extras.get_or_intern(lex.slice())
}


fn set_str_block(lex: &mut Lexer<Token>) -> Result<Vec<(StrToken, Span)>, LexError>{
    let mut str_token = lex.clone().morph::<StrToken>();
    let mut tokens: Vec<(StrToken, Span)> = Vec::new();
    while let Some(token) = str_token.next() {
        match token {
            Ok(t @ StrToken::Ident(_)) => {
                let span = str_token.span();
                tokens.push((t, Span::from_range( span.start + 1 .. span.end - 1 )))
            },
            Ok(t @ StrToken::Text(_)) => {
                tokens.push((t, Span::from_range(str_token.span())))
            },
            Ok(StrToken::EndQuote) => {
                set_bump_extras(lex, str_token);
                return Ok(tokens)
            },
            Err(_) => {
                set_bump_extras(lex, str_token);
                return Err(LexError::InvalidString)
            },
        }
    }
    set_bump_extras(lex, str_token);
    Err(LexError::UnterminatedString)
}


#[inline]
fn set_bump_extras(lex: &mut Lexer<Token>, str_lex: Lexer<StrToken>) {
    lex.bump(str_lex.span().end - lex.span().end);
    lex.extras = str_lex.extras;
}


#[derive(Debug, Copy, Clone, PartialEq)]
pub struct FloatToken {
    pub whole: (Spur, Span),
    pub mantissa: (Spur, Span),
}


fn set_float(lex: &mut Lexer<Token>) -> FloatToken {
    let ls = lex.slice();
    let Range { start, end } = lex.span();
    let dot = ls.find('.').unwrap();
    let whole = lex.extras.get_or_intern(&ls[..dot - start]);
    let mantissa = lex.extras.get_or_intern(&ls[dot - start + 1 ..]);
    FloatToken {
        whole: (whole, Span { start, end: dot }),
        mantissa: (mantissa, Span { start: dot + 1, end }),
    }
}


/// Token for strings
///
/// It may be `"simple text"` or `"text with {value}"`,
/// where `value` is a variable.
///
#[derive(Logos, Copy, Clone, Debug, PartialEq)]
#[logos(extras = Rodeo)]
pub enum StrToken {
    /// End find a quote, quits back to main [`Token`]
    #[token("\"")]
    EndQuote,
    #[regex(r#"[^"\\{}\r\n]+"#, set_str_spur)]
    Text(Spur),
    /// Identity with stripped curly braces.
    ///
    /// - input: `{value}`
    /// - output: `value` -> Spur
    #[regex(r"\{(\@)?[a-zA-Z_][a-zA-Z0-9\-_]*\}", set_id_spur)]
    Ident(Spur),
}

fn set_str_spur(lex: &mut Lexer<StrToken>) -> Spur {
    lex.extras.get_or_intern(lex.slice())
}

fn set_id_spur(lex: &mut Lexer<StrToken>) -> Spur {
    let s = lex.slice();
    lex.extras.get_or_intern(&s[1..s.len() - 1])
}


/// Lex tokens from behavioral entity file content string.
///
pub fn lex(src: &str) -> (Vec<(Token, Span)>, Vec<(LexError, Span)>, Rodeo) {
    let mut lexer: Lexer<Token> = Token::lexer_with_extras(src, Rodeo::new());
    let mut tokens: Vec<(Token, Span)> = Vec::new();
    let mut errors: Vec<(LexError, Span)> = Vec::new();
    while let Some(res) = lexer.next() {
        let span = Span::from_range(lexer.span());
        match res {
            Ok(t) => tokens.push((t, span)),
            Err(e) => errors.push((e, span)),
        }
    }
    (tokens, errors, lexer.extras)
}

