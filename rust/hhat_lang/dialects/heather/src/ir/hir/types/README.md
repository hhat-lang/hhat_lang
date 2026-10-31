# Types HIR

The Types HIR is part of Heather compiler's first pass, transforming source code (hat file) to a structured intermediate representation through the lexing and parsing steps. It covers only the types files, containing definitions of structs and enums, from classical and quantum paradigms.


## Grammar

The grammar reference is found below, as a [PEG](https://en.wikipedia.org/wiki/Parsing_expression_grammar) description. The [lex](lex.rs) and [parse](parse.rs) files are developed using this grammar as reference, and should reflect it accordingly.