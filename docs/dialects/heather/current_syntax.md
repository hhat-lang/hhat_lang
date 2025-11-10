

!!! note
    The syntax is in development and will have more features added continuously.


The H-hat's Heather dialect syntax works as follows:

## 1. Main
There is a main file that will be used for program execution. Its name can be anything, but it must contain a `main` keyword with brackets:

```
main {}
```

Code to be executed must live inside `main` body, e.g. anything inside the brackets will be executed.

## 2. Comments

```
// single line comment here

/- multiple
lines comment
here
-/
```

## 3. Variables

1. Variable declaration:
   ```
   var:some-type    // for classical data

   @var:@some-type  // for quantum data
   ```
      All quantum literals, types, functions, variables (and so on) start with `@`. This is the universal identifier for quantum-related things.

2. Variable assignment:
   ```
   // classical
   var1:some-type = value     // declare+assign
   var2 = value          // assign

   // quantum
   @var1:@some-type = @value  // declare+assign
   @var2 = @value        // assign
   ```

## 4. Calls

```
do_smt()               // empty call
print("hoi")           // one-argument call
add(1 2)               // multiple-anonymous argument call
range(start:0 end:10)  // multiple-named argument call
```

- Multiple-argument call arguments can be separated by [any Heather-defined whitespaces](index.md#features)

- Calls with named argument will have the `argument-name` followed by colon `:` and its value, e.g. `arg:val`

1. Classical variable assignment:
   ```
   var:some-type = data    // assign value
   var = other-data   // assign a new data
   ```
      - Assigning data more than once to a classical variable may be possible if it is mutable. More on that at the [language core system page](../../core/index.md). If the variable is immutable, an error will happen.

2. Quantum variable assignment:
   ```
   @var:@some-type = @first_value  // assign the first value
   @fn(@var)                  // @fn will be appended to @var data
   @other-fn(@var params)     // @other-fn will be appended next
   ```
      - A quantum data is an _appendable data container_, that is a data container that appends instructions applied to it in order. In the case above, the content of `@var` will be an array of elements: `[first_value, @fn(%self), @other-fn(%self params)]` that will be transformed and executed in order. More on what appendable data container is at the [language core system page](../../core/index.md).

## 5. Casting

```
// classical data to classical data casting
16*u32      // casts 16 to u32 type

// quantum data to classical data casting
@2*u32      // casts @2 to u32 type
```
   - Casting is a special property in the H-hat logic system. There is the usual classical to classical data casting, but also the quantum to classical data casting. The quantum to classical is special due to the nature of quantum data/variables. More on that in the [rule system page](../../rule_system.md). The syntax is `literal*type` or `variable*type`. In a similar fashion when declaring a variable one uses `variable:type`, with a different syntax sugar, `*`, to connect the data with the type.

## 6. Types

There are 4 types of type definitions: `single`, `struct`, `enum` and `union`. Below you can find how to define them:

```
type lines:u32
/- a single type called 'lines' that is
defined by u32. -/

type point { x:u32 y:u32 }
/- a struct type called 'point' with
members 'x ' of type u32 and 'y' of type u32. -/


type result {
  ok{ msg:str }
  err
}
/- a enum type called 'result' with
members 'ok', a struct data with member 'msg',
and 'err', a simple identifier. -/


type code union {
   number:u64
   text:str
}
/- a union type called 'code' with
members 'number' of type u64 and 'text' of type str. -/
```

Some key aspects of each type:

 - Single types can be thought as a "label" for a given type, but it has its own properties and checks

 - Structs are always defined by members with a name and type

 - Enums can be either identifiers or structs

 - Unions have the `union` keyword before the body and can hold members with name and type, structs or enums; they behave like usual unions in C, for instance

## 7. Functions


```
fn sum (a:u32 b:u32) u32 { =add(a b) }
```

- The `fn` keyword followed by the function name, `sum`, followed by the arguments between parenthesis, `a` and `b` of type `u32`, followed by the function type, `u32`, followed by the function body between brackets, `=add(a b)`. If the function has no return value, the `null` type can be left empty.

- The last expression to be return must contain a `=` syntax sugar to indicate it is the "return" expression.

## 8. Conditional statements (`if`)


```
if(
   eq(a b): some-result
   lt(a b): { some-bracket-body-result }
   true: else-result
)
```

An `if` statement is a call with options: each option is one condition with its result. If the result contains multiple expressions, it must be inside a bracket body. The last condition can be a `true` option, representing the `else` clause in other programming languages, or a fallback `default`.

## 9. Pattern matching (`match`)


```
match (something) {
   option1: some-result
   option2: { some-bracket-body-result }
   default: fallback-result
}
```

In a similar fashion to `if`, pattern matching `match` will have options containing their respective instructions. However, `match` requires a variable, function call, literal, etc. to be matched against. This something is placed inside parenthesis after `match` and a bracket body is defined with the options.


### 10. Modifiers

```
id<keyword>

id<property=value>

id<keyword property=value ...>
```

Modifiers provide an extensive way to complement, define or modify the data it is attached to, a literal, variable, type, function call, etc.


### 11. Generics


### 12. Type trait


### 13. `typespace`


### 14. Function traits and `fnspace`

#### 14.1 call with options


#### 14.2 call with body


#### 14.3 call with body options
