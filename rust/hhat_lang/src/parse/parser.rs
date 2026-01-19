//! Parser structure and logic for functions, types and constants grammars.
//!

use peg;


peg::parser!(
    /// Function grammar
    pub grammar fn_program() for str {
        pub rule whitespace() -> String
            = w:[' ' | '\t' | '\n' | ';' | ',']* { w.into_iter().collect() }

        pub rule vals() -> String
            = v:$(['a'..='z'|'A'..='Z']['a'..='z'|'A'..='Z'|'0'..='9']*) { v.to_owned() }

        pub rule start() -> Vec<String>
            = "[" l:(vals() ** whitespace()) "]" { l }
    }

);


peg::parser!(
    /// Type grammar
    pub grammar type_program() for str {

    }
);


peg::parser!(
    /// Const grammar
    pub grammar const_program() for str {

    }
);
