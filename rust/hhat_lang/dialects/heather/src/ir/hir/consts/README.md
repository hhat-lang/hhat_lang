# Constants HIR

The Constants HIR is part of Heather compiler's first pass, transforming source code (hat file) to a structured intermediate representation through the lexing and parsing steps. It covers only the constants files.


## Grammar

The grammar reference is found below, as a [PEG](https://en.wikipedia.org/wiki/Parsing_expression_grammar) description. The [lex](lex.rs) and [parse](parse.rs) files are developed using this grammar as reference, and should reflect it accordingly.

```peg
program                     = imports* consts* EOF
imports                     = "use" "(" ( type_import | fn_import | metafn_import | modifier_import | supertype_import | const_import )+ ")"
type_import                 = "type" ":" ( single_import | many_imports )
fn_import                   = "fn" ":" ( single_import | many_imports )
metafn_import               = "metafn" ":" ( single_import | many_imports )
modifier_import             = "modifier" ":" ( single_import | many_imports )
supertype_import            = "super-type" ":" ( single_import | many_imports )
const_import                = "const" ":" ( single_import | many_imports )
single_import               = composite_id_with_closure | full_id
many_imports                = "[" single_import+ "]"
composite_id_with_closure   = full_id "." "{" ( composite_id_with_closure | full_id )+ "}"
full_id                     = simple_id ( "." ( int_t | simple_id ) )* modifier?
simple_id                   = r"(\?)?(\@)?[a-zA-Z_][a-zA-Z0-9\-_]*"
modifier                    = "<" ( ( ref | pointer | variadic | callargs | simple_id ) modifier?)+ ">"
ref                         = "&"
pointer                     = "*"
variadic                    = "..."
callargs                    = simple_id "=" valonly
valonly                     = array | literal | full_id
array                       = "[" valonly* "]"
literal                     = (bool_t | float_t | int_t | str_t ) modifier?
bool_t                      = r"(\@)?(true|false)"
int_t                       = r"(\@)?(-)?(0|[1-9][0-9]*)"
float_t                     = r"(\@)?(-)?(0|[1-9][0-9]*)\.[0-9]+"
str_t                       = "\"" ( str_char | "{" simple_id "}" )* "\""
str_char                    = r"[^\"\\{}\n]" | r"\\."
consts                      = "const" simple_id ":" type_id "=" expr
body                        = "{" ( declareassign | declareassign_ds | declare | assign | assign_ds | expr )* "}"
expr                        = cast | literal | array | access | call_optn | call_optbdn | call_bdn | call | full_id
cast                        = ( access | call | literal | full_id ) "*" modifier? type_id
access                      = callable member+
callable                    = call_optn | call_optbdn | call_bdn | call
member                      = "." ( simple_id | int_t | ( "(" args* ")" ) )
call_optn                   = full_id "(" option+ ")"
call_optbdn                 = full_id "(" args* ")" "{" option+ "}" modifier?
call_bdn                    = full_id "(" args* ")" body modifier?
option                      = expr ":" body
call                        = full_id "(" args* ")" modifier?
args                        = ( cast | literal | array | access | call | valonly )
type_id                     = ( "[" full_id "]" ) | full_id
return                      = "::" expr
```
