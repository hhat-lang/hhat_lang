# Behavioral HIR

The Behavioral HIR is part of Heather compiler's first pass, transforming source code (hat file) to a structured intermediate representation through the lexing and parsing steps. It covers only the behavioral files, containing definitions of functions, metafunctions, casts, modifiers, and super-types.


## Grammar

The grammar reference is found below, as a [PEG](https://en.wikipedia.org/wiki/Parsing_expression_grammar) description. The [lex](lex.rs) and [parse](parse.rs) files were developed using this grammar as reference, and should reflect it accordingly.

```peg

program                     = imports* group_fns* main? EOF
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
main                        = "main" body
body                        = "{" ( declareassign | declareassign_ds | declare | assign | assign_ds | expr )* "}"
declareassign               = simple_id modifier? ":" type_id "=" expr
declareassign_ds            = simple_id modifier? ":" type_id "=" "." "{" ( assign+ | expr+ ) "}"
declare                     = simple_id modifier? ":" type_id
assign                      = full_id "=" expr
assign_ds                   = full_id "." "{" ( assign+ | expr+ ) "}"
expr                        = cast | literal | array | access | call_optn | call_optbdn | call_bdn | call | full_id
cast                        = ( access | call | literal | full_id ) "*" modifier? type_id
access                      = callable member+
callable                    = call_optn | call_optbdn | call_bdn | call
member                      = "." ( simple_id | int_t | ( "(" args* ")" ) )
call_optn                   = full_id "(" option+ ")"
call_optbdn                 = full_id "(" args* ")" "{" option+ "}" modifier?
call_bdn                    = full_id "(" args* ")" fn_body modifier?
option                      = expr ":" ( fn_return | fn_body )
call                        = full_id "(" args* ")" modifier?
args                        = ( cast | literal | array | access | call | valonly )
group_fns                   = fn_def | metafn_def | modifier_def | supertype_def
fn_def                      = "fn" simple_id fn_args type_id? fn_body
fn_args                     = "(" argtype* ")"
argtype                     = simple_id modifier? ":" type_id
type_id                     = ( "[" full_id "]" ) | full_id
fn_body                     = "{" ( fn_return | declareassign | declareassign_ds | declare | assign | assign_ds | expr )* "}"
fn_return                   = "::" expr
metafn_def                  = "metafn" simple_id fn_args type_id? metafn_body
metafn_body                 = "{" ( fn_return | declareassign | declareassign_ds | declare | assign_ds | assign | option | expr )* "}"
modifier_def                = "modifier" ( simple_id | pointer | ref | variadic ) modifier_args type_id modifier_body
modifier_args               = "(" "self" argtype* ")"
modifier_body               = "{" modifier_item+ "}"
modifier_item               = modifier_directive ":" ( fn_body | fn_return | expr )
modifier_directive          = "#ct_init" | "#rt_init" | "#ct_read" | "#rt_read" | "#ct_write" | "#rt_write" | "#ct_drop" | "#rt_drop"
supertype_def               = "super-type" simple_id supertype_body
supertype_body              = "{" full_id* "}"

```