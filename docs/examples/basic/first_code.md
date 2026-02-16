# Basic Examples: First Code

Your first H-hat programs explained step by step.

!!! tip "Start Here"
    This is a great place to start if you're new to H-hat!

## Hello, World!

The traditional first program:

```heather
main {
    print("Hello, World!")
}
```

### Running

```bash
hhat run hello.hat
```

### Output

```
Hello, World!
```

### Explanation

- `main` is the entry point of every H-hat program
- `print()` outputs text to the console
- No semicolons needed in Heather dialect!

## Hello with Variables

Adding variables to the mix:

```heather
main {
    let message:str = "Hello, H-hat!"
    print(message)
}
```

### Explanation

- `let` declares a new variable
- `message` is the variable name
- `:str` specifies the type (string)
- `=` assigns the value

## Simple Calculation

Performing basic arithmetic:

```heather
main {
    let a:i32 = 10
    let b:i32 = 32
    let sum:i32 = add(a, b)
    
    print("Sum: ")
    print(sum)
}
```

### Explanation

- Variables hold integer values
- `add()` is a function that adds numbers
- Multiple print statements output sequentially

## Next Steps

<div class="grid cards" markdown>

-   **Variables & Types**

    Learn about different types

    [:octicons-arrow-right-24: Continue](variables.md)

-   **Functions**

    Define your own functions

    [:octicons-arrow-right-24: Learn More](functions.md)

-   **Quantum Examples**

    Start quantum programming

    [:octicons-arrow-right-24: Explore](../quantum/quantum_types.md)

</div>
