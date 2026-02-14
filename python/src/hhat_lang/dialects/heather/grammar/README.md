# Grammar

Defines the Heather dialect's syntax using a PEG (Parsing Expression Grammar), processed by the [Arpeggio](https://github.com/textX/Arpeggio) parser library.

## Overview

Heather uses a declarative PEG grammar file to specify its syntax. The Arpeggio parser reads this grammar at runtime and produces a parse tree, which the [`../parsing/`](../parsing/) module then converts into AST nodes.

## Directory Structure

```
grammar/
  __init__.py      # WHITESPACE definition
  grammar.peg      # Complete PEG grammar for the Heather dialect
```

## Module Details

### `__init__.py`

Defines `WHITESPACE = "\n\t ,;"`. In Heather, commas and semicolons are treated as whitespace alongside newlines, tabs, and spaces. This is an intentional design choice: by making commas and semicolons part of whitespace, they become optional separators everywhere. You can write `fn(a b c)` or `fn(a, b, c)` -- both are valid. This reduces syntactic noise and avoids common "missing comma" errors, while still allowing programmers who prefer delimiters to use them.

### grammar.peg

The full PEG grammar, organized into these rule groups:

**Program structure**
- `program` -- Top-level: imports, type definitions, functions, and an optional `main` block
- `imports` -- `use(type: ... fn: ...)` import declarations
- `main` -- `main { ... }` entry point block

**Type definitions**
- `type_file` -- `type` keyword followed by one of four forms:
  - `typesingle` -- `name : type` (single-member alias)
  - `typestruct` -- `name { member1: type1  member2: type2 }` (struct with named members)
  - `typeenum` -- `name { Variant1  Variant2 }` (enum with variants)
  - `typeunion` -- `name union { member1: type1 }` (tagged union)
- `type_trait` -- `trait name { fns }` (trait definition)
- `typespace` -- `typespace name { fns }` (type namespace)

**Functions**
- `fns` -- `fn name (args) return_type? { body }`
- `fnargs` -- `(arg_name: arg_type ...)`
- `return` -- `= expr` (return expression)

**Expressions and statements**
- `body` -- `{ declare | assign | declareassign | expr ... }`
- `expr` -- One of: cast, call, callwithbody, callwithbodyoptions, callwithargsbodyoptions, array, id, literal
- `declare` -- `name<modifier>?: type` (variable declaration)
- `assign` -- `id = expr` (assignment)
- `declareassign` -- `name<modifier>?: type = expr` (combined declare+assign)
- `cast` -- `expr * type` (type casting, e.g., `u32*@2`)

**Function calls**
- `call` -- `trait#id.fn(args)` or `fn(args)` (basic call)
- `callwithbody` -- `fn { body }` (call with closure)
- `callwithbodyoptions` -- `fn(args) { body }` (call with args and closure)
- `callwithargsbodyoptions` -- `fn(expr { body } ...)` (call with expression-body pairs)

**Identifiers**
- `simple_id` -- `@?[a-zA-Z][a-zA-Z0-9\-_]*` (optional `@` prefix for quantum)
- `composite_id` -- `a.b.c` (dotted identifier)
- `composite_id_with_closure` -- `a.{b c d}` (grouped attribute access)
- `modifier` -- `<value ...>` or `<name: value ...>` (angle-bracket modifiers)
- `trait_id` -- `Type#trait` (trait accessor)

**Literals**
- Classical: `null`, `bool` (`true`/`false`), `str` (`"..."`), `int`, `float`, `imag`, `complex` (`[real imag]`)
- Quantum: `q__bool` (`@true`/`@false`), `q__int` (`@42`, `@0`)

**Comments**
- Single-line: `// ...`
- Multi-line: `/- ... -/`

## Connections

- **[`../parsing/run.py`](../parsing/run.py)**: Loads `grammar.peg` via `read_grammar()` and creates an Arpeggio `ParserPEG` instance with `program` as the root rule and `comment` as the comment rule
- **[`../parsing/visitor.py`](../parsing/visitor.py)**: Each grammar rule maps to a `visit_*` method in `ParserVisitor`

## Modifying the Grammar

The grammar is loaded at runtime by `parsing/run.py` via `read_grammar()`. To add or modify syntax rules:

1. Edit `grammar.peg` following PEG syntax (ordered choice with `/`, sequences with spaces, optional with `?`, repetition with `*`/`+`)
2. Add a corresponding `visit_<rule_name>` method in `parsing/visitor.py` that converts the parse tree node to a Heather AST node
3. If the rule produces a new AST node type, define it in `code/ast.py`

Arpeggio processes the grammar top-down from the `program` root rule. The `comment` rule is automatically handled as a comment pattern and stripped from the parse tree.

## Current Status

The grammar covers the current feature set: imports, type definitions (single/struct/enum), function definitions, variable declarations and assignments, casting, and literals. Some corresponding visitor methods are not yet implemented (function calls, arrays, trait identifiers, union types).
