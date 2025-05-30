# Core Features


## Core implementation

Some core features provide wide range of possibilities for the dialect implementation.


### 1. Call with options

It has the structure:

```
id (
    option1: body
    option2: body
    ...
)
```

It can be used to define an identifier `id` to hold some transformation through the options that are functions call (and not identifiers, as usually in function calls with arguments) with values being the body that is executed for that particular option.

Example: [`if` statement](../dialects/heather/current_syntax.md#8-conditional-statements-if).


### 2. Call with body

It has the structure:

```
id (args) { body }
```


### 3. Call with body options

It has the structure:

```
id (arg) {
    option1: body
    option2: body
    ...
}
```

Example: [pattern matching `match`](../dialects/heather/current_syntax.md#9-pattern-matching-match).


### 4. Modifier

It has the structure:

```
id<keyword>
id<property=value>
id<keyword property=value ...>
```

Example: []
