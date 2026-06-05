# Heather Grammar

*Heather uses [PEG grammar](https://en.wikipedia.org/wiki/Parsing_expression_grammar).*

---

## Grammar features

* Grammar on `program`.
* Each aggregatable definition has its own grammar.
* Some portions of the grammar are common between them.
* Whitespaces are: ` \t\n,;` (space, tab, new line, comma, semi-colon). Those are completely ignored throughout the code.
* Comments are: `// text ` for single line comments; `/- block ... -/` for multi-line comments.

### 1. Group functions

Grammar for main file (`main.hat`) as well as functions, meta-functions, casts, super-types and modifiers:

```
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
composite_id_with_closure   = full_id "." "{" ( composite_id_with_closure | composite_id | full_id )+ "}"
composite_id                = simple_id ( "." simple_id )+
full_id                     = ( composite_id | simple_id ) modifier?
simple_id                   = r"(\#\!\%\@)?[a-zA-Z][a-zA-Z0-9\-_]*"
modifier                    = "<" ( ref | pointer | variadic | (callargs | simple_id)+ ) ">"
ref                         = "&"
pointer                     = "*"
variadic                    = "..."
callargs                    = full_id "=" valonly
valonly                     = array | full_id | literal
array                       = "[" ( literal | composite_id_with_closure | full_id )* "]"
literal                     = (bool_t | int_t | float_t | str_t ) modifier?
bool_t                      = r"(\#\!\%\@)?(true|false)"
int_t                       = r"(\#\!\%\@)?(-)?([1-9][0-9]*|0)"
float_t                     = r"(\#\!\%\@)?(-)?(0|[1-9][0-9]*[.][0-9]+)"
str_t                       = r"(\#\!\%\@)?\"([^]*)\""
main                        = "main" body
body                        = "{" ( declareassign | declareassign_ds | declare | assign | expr )* "}"
declareassign               = simple_id modifier? ":" type_id "=" expr
declareassign_ds            = simple modifier? ":" type_id "=" "." "{" assign+ "}"
declare                     = simple_id modifier? ":" type_id
assign                      = full_id "=" expr
assign_ds                   = full_id "." "{" ( assign+ | expr+ ) "}"
expr                        = cast | assign_ds | call_optn | call_optbdn | call_bdn | call | array | full_id | literal
cast                        = ( call | literal | full_id ) "*" type_id
call_optn                   = full_id "(" option+ ")"
call_optbdn                 = full_id "(" args* ")" "{" option+ "}"
call_bdn                    = full_id "(" args* ")" body
call                        = full_id "(" args* ")" modifier?
args                        = ( callargs | cast | call | valonly )
group_fns                   = fn_def | metafn_def | modifier_def | supertype_def
fn_def                      = "fn" ( simple_id | pointer ) fn_args type_id? fn_body
fn_args                     = "(" argtype* ")"
argtype                     = full_id ":" type_id
type_id                     = ( "[" full_id "]" ) | full_id
fn_body                     = "{" ( fn_return | declareassign | declareassign_ds | declare | assign_s | assign | expr )* "}"
fn_return                   = "::" expr
metafn_def                  = "metafn" simple_id fn_args type_id? metafn_body
metafn_body                 = "{" ( fn_return | option | declareassign | declareassign_ds | declare | assign_ds | assign | expr )* "}"
modifier_def                = "modifier" ( simple_id | pointer | ref | variadic ) modifier_args type_id metafn_body
modifier_args               = "(" "self" argtype* ")"
supertype_def               = "super-type" simple_id supertype_body
supertype_body              = "{" full_id* "}"
```

### 2. Types

Grammar for types:

```
program                     = imports* type_def* EOF
imports                     = "use" "(" ( type_import | fn_import | metafn_import | modifier_import | supertype_import | const_import )+ ")"
type_import                 = "type" ":" ( single_import | many_imports )
fn_import                   = "fn" ":" ( single_import | many_imports )
metafn_import               = "metafn" ":" ( single_import | many_imports )
modifier_import             = "modifier" ":" ( single_import | many_imports )
supertype_import            = "super-type" ":" ( single_import | many_imports )
const_import                = "const" ":" ( single_import | many_imports )
single_import               = composite_id_with_closure | full_id
many_imports                = "[" single_import+ "]"
composite_id_with_closure   = full_id "." "{" ( composite_id_with_closure | composite_id | full_id )+ "}"
composite_id                = simple_id ( "." simple_id )+
full_id                     = ( composite_id | simple_id ) modifier?
simple_id                   = r"(\#\!\%\@)?[a-zA-Z][a-zA-Z0-9\-_]*"
modifier                    = "<" ( ref | pointer | variadic | (callargs | simple_id)+ ) ">"
ref                         = "&"
pointer                     = "*"
variadic                    = "..."
callargs                    = full_id "=" valonly
valonly                     = array | full_id | literal
array                       = "[" ( literal | composite_id_with_closure | full_id )* "]"
literal                     = (bool_t | int_t | float_t | str_t ) modifier?
bool_t                      = r"(\#\!\%\@)?(true|false)"
int_t                       = r"(\#\!\%\@)?(-)?([1-9][0-9]*|0)"
float_t                     = r"(\#\!\%\@)?(-)?(0|[1-9][0-9]*[.][0-9]+)"
str_t                       = r"(\#\!\%\@)?\"([^]*)\""
type_def                    = "type" ( type_struct | type_enum )
type_struct                 = simple_id "{" struct_member+ "}"
struct_member               = simple_id ":" type_id
type_enum                   = simple_id "{" enum_member+ "}"
enum_member                 = simple_id | type_struct
type_id                     = ( "[" full_id "]" ) | full_id
```

### 3. Constants

Grammar for constants:

```
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
composite_id_with_closure   = full_id "." "{" ( composite_id_with_closure | composite_id | full_id )+ "}"
composite_id                = simple_id ( "." simple_id )+
full_id                     = ( composite_id | simple_id ) modifier?
simple_id                   = r"(\#\!\%\@)?[a-zA-Z][a-zA-Z0-9\-_]*"
modifier                    = "<" ( ref | pointer | variadic | (callargs | simple_id)+ ) ">"
ref                         = "&"
pointer                     = "*"
variadic                    = "..."
callargs                    = full_id "=" valonly
valonly                     = array | full_id | literal
array                       = "[" ( literal | composite_id_with_closure | full_id )* "]"
literal                     = (bool_t | int_t | float_t | str_t ) modifier?
bool_t                      = r"(\#\!\%\@)?(true|false)"
int_t                       = r"(\#\!\%\@)?(-)?([1-9][0-9]*|0)"
float_t                     = r"(\#\!\%\@)?(-)?(0|[1-9][0-9]*[.][0-9]+)"
str_t                       = r"(\#\!\%\@)?\"([^]*)\"" 
consts                      = "const" simple_id ":" type_id "=" expr
expr                        = cast | assign_ds | call_optn | call_optbdn | call_bdn | call | array | full_id | literal
cast                        = ( call | literal | full_id ) "*" type_id
call_optn                   = full_id "(" option+ ")"
call_optbdn                 = full_id "(" args* ")" "{" option+ "}"
call_bdn                    = full_id "(" args* ")" body
call                        = full_id "(" args* ")" modifier?
args                        = ( callargs | cast | call | valonly )
assign                      = full_id "=" expr
assign_ds                   = full_id "." "{" ( assign+ | expr+ ) "}"
type_id                     = ( "[" full_id "]" ) | full_id
```
