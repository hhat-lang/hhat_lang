
Heather is a H-hat's regular syntax dialect intended to provide the first steps for programmers to explore the language features and possibilities in this new paradigm.


A (classical) "hello world" program looks like (inside `main.hat`):

```
main { print("hoi quantum") }  // a "hello world" program
```

Heather has no need for `;` to separate between statements or `,` to separate between items. ` `, `\t`, `\n`, `;` and `,` are all treated as whitespaces and are ignored. You may use them if you prefer though. Because of Heather's regular syntax, statements and expressions can be organized in what fits better the programmer's or a particular project style. We expect that it can provide some freedom for people to experiment and define what works better for a particular situation, rather than enforcing that without a real reason. Comments are: `// comment goes here`  for line comments, and `/* comment body goes inside here */` for multiline comments.

#### 1. Constants

Constants are defined inside `consts.hat` files. They have the following syntax:

```
const <name>:<type> = <value>
```

##### Examples

- `math/consts.hat`:

  ```
  const pi32:f32 = 3.14159265
  const pi64:f64 = 3.141592653589793
  ```

- `io/consts.hat`:

  ```
  const localhost:str = "localhost"
  ```

##### Importing

You can import constants in functions kinds and other constants files.

- For single imports:

  ```
  use(const:<path.constant-name>)
  ```

- For multiple imports:

  ```
  use(
    const:<path.constant-name1>
    const:<path.constant-name2>
  )
  ```

- For multiple imports inside a single `const`:

  ```
  use(
    const:[
      <path.constant-name1>
      <path.constant-name2>
    ]
  )
  ```


#### 2. Types

Types are defined inside custom files located on `src/hat_types/` path. There are basically two types of user types: structs and enums. A quantum type can contain classical types as its members/named values, but the opposite is not valid.

##### Structs

- _Definition_: a composite data structure, holding a collection of members (or fields) that may have different data types.

- Syntax:

  ```
  type <name> { <member>:<type> ... }
  ```

- Examples:

    * Defining struct type:

      ```
      type point { x:i32 y:i32 }
      ```

    * Using struct type:

      ```
      // assigning to variable p while declaring it
      p:point =.{x=34 y=43}

      // assigning to variable already declared
      p2:point
      p2.{x=15 y=51}
  
      // (re)assigning to individual members
      p3<mut>:point
      p3.{x=143 y=331}
      p3.y=341
  
      // calling it
      print(p.x)
      ```

    * Importing:

      ```
      // single import
      use(type:<path.type-name>)
      ```
      ```
      // multiple imports:
      use(
        type:<path.type-name1>
        type:<path.type-name2>
      )
      ```
      ```
      // multiple imports, single call:
      use(
        type:[
          <path.type-name1>
          <path.type-name2>
        ]
      ) 
      ```


##### Enums

- _Definition_: a tagged union (or enumerated) data structure that can contain a collection of named values, those being simple identifiers or structs, but only one can be in use at any one time. By convention, identifiers are all caps.

- Syntax:

  ```
  type <name> { <enumerator?> <struct?> ... }
  ```

- Examples:

    * Defining enum type:

      ```
      type status_t { ON OFF }
      
      type result_t { 
        data{
          value:sample_t
        }
        NONE
      }
      ``` 

    * Using enum type:

      ```
      // declaring and assigning on a variable
      status:status_t = status_t.ON
      res:result_t = result_t.data.value=...
      res2:result_t = result_t.NONE
  
      // assigning on a declared variable
      status2:status_t
      status2 = status_t.ON
  
      // calling it
      print(status_t.OFF)
      print(status)
      ```

#### 3. Functions

- Syntax:

  ```
  fn <name> (<args?>) <type?> { <body?> }
  ```
  Return has a special syntax sugar: `::` prefixed on an expression.

- Examples:

    * Defining a type:

      ```
      fn sum(a:i64 b:i64) i64 { ::add(a b) }
      ```
      ```
      fn print-gt(a:u64 b:u64) {
        if(
          gt(a b): print(a)
          true: print(b)
        )
      }
      ```

#### 4. Meta-funcions

- _Definition_: a function that defines the code behavior assigned to it. There are three kinds of meta-functions: _option_ (or _cases_), _body_ (or _blocks_), and _option-body_ (or _case-blocks_). They have the types associated with them as `optn_t`, `bdn_t` and `optbdn_t` respectively.

- Syntax:

  ```
  meta-fn <name> (args) <type?> { <body> }
  ```

- Examples:

    * `if` meta-function (option type):

      Defining:

      ```
      meta-fn if(options:[opt-body_t]) ir_t { ... }
      ```

      Calling:

      ```
      if(gt(a b):a true:b)
      ```

    * `pipe` meta-function (body type):

      Defining:

      ```
      meta-fn pipe(args:[expr_t] body:ir_t) ir_t { ... }
      ```

      Calling:

      ```
      pipe(var) { double print }  // applies double on var and then print on double's result
      ```

    * `match` meta-function (option-body type):

      Defining:

      ```
      meta-fn match(arg:[expr_t] options:[opt-body_t]) ir_t { ... }
      ```

      Calling:

      ```
      match(status) {
          status_t.ON:print("on!")
          status_t.OFF:print("off!")
      }
      ```

#### 5. Modifiers

- _Definition_: a function that can change the semantics and properties of its holder.

- Syntax:

  ```
  modifier <name> (self <arg?>) <type> { <body> }
  ```
  the `<type>` must be the same of self.

- Examples:

    * `&` (reference) modifier

      ```
      modifier &(self) u32 { ... }  // for u32 type
      modifier &(self) [u32] { ... }  // for array of u32 type
      modifier &(self) status_t { ... }  // for status_t type
      ```
      ```
      // usage
      var:status_t<&>
      ```

#### 6. Cast

- *Definition*: a type of reflective function and semantics that convert one data into another type. If data is eagerly evaluated (strict), it should convert to target type calling a given function with given `cast` name and the appropriate argument types signature. If data is lazily evaluated (lazy), it will evoke its evaluation and then the result value to be cast into the target type. It has a syntax sugar `*` when called, as in: `data * type`, meaning "cast data into type".

- Syntax:

    ```
    fn cast (data:<type> to:<type>) <to type> { <body> }
    ```

- Examples:
    - casting strict data
        ```
        v1:u32 = 42
        v2:u64 = v1 * u64  // now v1 data is cast into u64 and stored in v2
        ```

    - casting lazy data
        ```
        @q:@bell_t =.{@s=@false @t=@false}
        @sync(@q)
        res:hashmap = @q * hashmap  // evaluate lazy data from @q and convert its result as hashmap, storing at res
        ```

