

!!! note
    The syntax is in development and will have more features added continuously.


The H-hat's Heather dialect syntax works as follows:

1. There is a main file that will be used for program execution. Its name can be anything, but it must contain a `main` keyword with brackets:

    ```
    main {}
    ```

2. Code to be executed must live inside `main` body, e.g. anything inside the brackets will be executed.
3. Comments are:
    - `// comment here` for oneliner
    - `/- big comment here... -/` for multiple lines
4. Variable declaration:
   ```
   var:type    // for classical data

   @var:@type  // for quantum data
   ```
5. Variable assignment:
   ```
   // classical
   var1:type = value     // declare+assign
   var2 = value          // assign

   // quantum
   @var1:@type = @value  // declare+assign
   @var2 = @value        // assign
   ```
6. Call:
   ```
   do_smt()               // empty call
   print("hoi")           // one-argument call
   add(1 2)               // multiple-anonymous argument call
   range(start:0 end:10)  // multiple-named argument call
   ```
    - Multiple-argument call arguments can be separated by [any Heather-defined whitespaces](index.md#features)
    - Calls with named argument will have the `argument-name` followed by colon `:` and its value, e.g. `arg:val`
7. Classical variable assignment:
   ```
   var:type = data    // assign value
   var = other-data   // assign a new data
   ```
      - Assigning data more than once to a classical variable may be possible if it is mutable. More on that at the [language core system page](../../core/index.md). If the variable is immutable, an error will happen.
8. Quantum variable assignment:
   ```
   @var:@type = @first_value  // assign the first value
   @fn(@var)                  // @fn will be appended to @var data
   @other-fn(@var params)     // @other-fn will be appended next
   ```
      - A quantum data is an _appendable data container_, that is a data container that appends instructions applied to it in order. In the case above, the content of `@var` will be an array of elements: `[first_value, @fn(%self), @other-fn(%self params)]` that will be transformed and executed in order. More on what appendable data container is at the [language core system page](../../core/index.md).
9. Casting:
   ```
   // classical data to classical data casting
   u32*16      // casts 16 to u32 type
   
   // quantum data to classical data casting
   u32*@2      // casts @2 to u32 type
   ```
      - Casting is a special property in the H-hat logic system. There is the usual classical to classical data casting, but also the quantum to classical data casting. The quantum to classical is special due to the nature of quantum data/variables. More on that in the [rule system page](../../rule_system.md). The syntax is `type*literal` or `type*variable`. In a similar fashion when declaring a variable one uses `variable:type`, it can be thought as the "other way around" process, that is why it was chosen to define the type first on casting (with a different syntax sugar, `*`, to connect the type with the data).
