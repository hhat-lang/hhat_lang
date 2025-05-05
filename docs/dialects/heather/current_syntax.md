

!!! note
    The syntax development is in continuous development and will have more features added.


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
   var:type = value     // declare+assign
   var = value          // assign

   // quantum
   @var:@type = @value  // declare+assign
   @var = @value        // assign
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
