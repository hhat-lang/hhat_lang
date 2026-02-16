# Your First H-hat Program

Let's write and understand your first H-hat program using the Heather dialect.

## Prerequisites

Before starting, make sure you have:

- [ ] H-hat installed (see [Getting Started](../getting_started.md))
- [ ] A text editor or IDE
- [ ] Basic understanding of programming concepts

## Hello, Quantum World!

Create a file named `hello.hat` with the following content:

```heather
main {
    print("Hello, quantum world!")
}
```

### Running Your Program

=== "Rust Implementation"

    ```bash
    hhat run hello.hat
    ```

=== "Python Implementation"

    ```bash
    python -m hhat_lang run hello.hat
    ```

**Output:**
```
Hello, quantum world!
```

## Understanding the Code

Let's break down what's happening:

### The `main` Function

```heather
main { ... }
```

- `main` is the entry point of every H-hat program
- The program execution starts here
- Everything between `{` and `}` is the function body

### The `print` Function

```heather
print("Hello, quantum world!")
```

- `print` is a built-in function that outputs to the console
- The text in quotes is a string literal
- No semicolons needed in Heather!

## Your First Quantum Program

Now let's create something more interesting—a program that uses quantum operations:

Create `quantum_hello.hat`:

```heather
main {
    // Create a qubit in state |0>
    let q:qubit = |0>
    
    // Apply Hadamard gate for superposition
    let q_super:qubit = h(q)
    
    // Measure the qubit
    let result:bool = cast(q_super, bool)
    
    // Print the result
    print("Measurement result: ")
    print(result)
}
```

### Running the Quantum Program

```bash
hhat run quantum_hello.hat
```

**Output** (random, either):
```
Measurement result: true
```
or
```
Measurement result: false
```

## Understanding Quantum Code

### Variable Declaration

```heather
let q:qubit = |0>
```

- `let` declares a new variable
- `q` is the variable name
- `:qubit` specifies the type (a quantum bit)
- `|0>` initializes it to the |0⟩ state

### Quantum Operations

```heather
let q_super:qubit = h(q)
```

- `h()` is the Hadamard gate function
- It creates superposition: |0⟩ → (|0⟩ + |1⟩)/√2
- Result is stored in `q_super`

### The Cast Operation

```heather
let result:bool = cast(q_super, bool)
```

- `cast` is H-hat's special operation
- It executes accumulated quantum operations
- Measures the qubit and converts to classical type
- Returns `true` or `false` (representing |1⟩ or |0⟩)

## A More Complex Example

Let's create a simple quantum circuit:

```heather
// quantum_circuit.hat

main {
    // Initialize two qubits
    let q1:qubit = |0>
    let q2:qubit = |0>
    
    // Create entanglement
    let q1_h:qubit = h(q1)              // Hadamard on first qubit
    let pair:tuple = cnot(q1_h, q2)     // CNOT to entangle
    
    // Unpack the entangled pair
    let (qa:qubit, qb:qubit) = pair
    
    // Measure both qubits
    let a:bool = cast(qa, bool)
    let b:bool = cast(qb, bool)
    
    // Print results
    print("Qubit A: ")
    print(a)
    print("Qubit B: ")
    print(b)
    print("Correlated: ")
    print(eq(a, b))  // Should be true due to entanglement
}
```

### Key Concepts Demonstrated

**Multiple Variables**
:   Declare and use multiple quantum states

**Function Composition**
:   Chain quantum operations (`h` then `cnot`)

**Tuple Types**
:   Multi-qubit gates return tuples

**Pattern Matching**
:   Unpack tuple results with `let (a, b) = tuple`

**Entanglement**
:   Create and measure correlated quantum states

## Classical and Quantum Together

H-hat seamlessly mixes classical and quantum code:

```heather
fn prepare_state(angle:f64) -> qubit {
    let q:qubit = |0>
    let rotated:qubit = rx(q, angle)
    rotated
}

main {
    // Classical computation
    let angle:f64 = pi / 4.0
    
    // Prepare quantum state
    let state:qubit = prepare_state(angle)
    
    // Classical loop
    let i:i32 = 0
    while(lt(i, 10)) {
        let result:bool = cast(state, bool)
        print(result)
        i = add(i, 1)
    }
}
```

## Common Patterns

### 1. Initialize-Transform-Measure

```heather
let q:qubit = |0>           // Initialize
let q2:qubit = x(q)         // Transform
let result:bool = cast(q2, bool)  // Measure
```

### 2. Function Definition

```heather
fn apply_rotation(q:qubit, angle:f64) -> qubit {
    rx(q, angle)
}
```

### 3. Type Annotations

```heather
let x:i32 = 42              // Integer
let y:f64 = 3.14            // Float
let z:bool = true           // Boolean
let q:qubit = |0>           // Qubit
let s:str = "hello"         // String
```

### 4. Lazy Evaluation

```heather
// Operations are accumulated, not executed
let q:qubit = |0>
let q2:qubit = h(q)         // Not executed yet
let q3:qubit = x(q2)        // Still not executed
let result:bool = cast(q3, bool)  // Now everything executes
```

## Next Steps

Congratulations! You've written your first H-hat programs. Here's what to explore next:

<div class="grid cards" markdown>

-   **📚 Language Concepts**

    Learn about types, ownership, and advanced features

    [Explore Concepts →](../core/index.md)

-   **💡 More Examples**

    See more code samples and patterns

    [View Examples →](../examples/index.md)

-   **🔧 Tools & CLI**

    Master the H-hat toolchain

    [Toolchain Guide →](../toolchain.md)

-   **🎯 Dialects**

    Understand Heather syntax in depth

    [Heather Syntax →](../dialects/heather/syntax.md)

</div>

## Troubleshooting

### Program won't compile

- Check that file has `.hat` extension
- Verify H-hat is installed: `hhat --version`
- Look for syntax errors in the output

### Quantum operations not working

- Ensure backend is configured properly
- Check that quantum types are annotated correctly
- Verify cast operations are present

### Getting help

- Check the [Community page](../community/index.md)
- Ask on [Discord](http://discord.unitary.foundation) in `#h-hat`
- Search [GitHub Issues](https://github.com/hhat-lang/hhat_lang/issues)

---

**Happy coding!** 🚀 Feel free to experiment and explore the language. The best way to learn is by doing.
