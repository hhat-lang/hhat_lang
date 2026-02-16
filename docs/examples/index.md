# Examples

Learn H-hat through practical code examples.

## Quick Start Examples

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Basic Examples__

    ---

    Start with the fundamentals

    * [First Code](basic/first_code.md)
    * [Variables & Types](basic/variables.md)
    * [Functions](basic/functions.md)

-   :material-atom:{ .lg .middle } __Quantum Examples__

    ---

    Explore quantum programming

    * [Quantum Types](quantum/quantum_types.md)
    * [Casting Quantum](quantum/casting.md)
    * [Quantum Operations](quantum/operations.md)

-   :material-star:{ .lg .middle } __Advanced Examples__

    ---

    Master complex patterns

    * [Custom Types](advanced/custom_types.md)
    * [Calling Functions](advanced/calling_functions.md)

</div>

## Example Categories

### Basic Examples

Perfect for beginners to H-hat:

- **Hello World**: Your first H-hat program
- **Variables**: Declaration and types
- **Functions**: Defining and calling functions
- **Control Flow**: if/match expressions
- **Data Structures**: Structs and enums

### Quantum Examples

Learn quantum programming with H-hat:

- **Quantum States**: Creating and manipulating qubits
- **Gates**: Applying quantum gates
- **Measurement**: Casting quantum to classical
- **Superposition**: Creating quantum superposition states
- **Entanglement**: Creating and using entangled states

### Advanced Examples

For experienced developers:

- **Custom Types**: Defining complex types
- **Function Overloading**: Multiple function definitions
- **Generic Programming**: Type parameters
- **Memory Management**: Ownership and borrowing
- **Error Handling**: Result and Option types

## Learning by Example

### By Complexity

#### Level 1: Basics
- Hello World
- Simple variables
- Basic functions

#### Level 2: Intermediate
- Control flow
- Data structures
- Quantum basics

#### Level 3: Advanced
- Generic types
- Memory patterns
- Complex quantum circuits

### By Topic

#### Classical Programming
- Variables and constants
- Functions and modules
- Data structures
- Error handling

#### Quantum Programming
- Qubit manipulation
- Gate operations
- Measurement and casting
- Quantum algorithms

#### System Features
- Type system
- Ownership model
- Module system
- Overloading

## Example Format

Each example follows this structure:

### 1. Overview
Brief description of what the example demonstrates

### 2. Code
Complete, runnable code example

### 3. Explanation
Line-by-line breakdown

### 4. Output
Expected output when running

### 5. Key Concepts
Important takeaways

### 6. Try It Yourself
Modifications to experiment with

## Running Examples

### Save and Run

```bash
# Save example to a file
echo 'main { print("Hello!") }' > example.hat

# Run with H-hat
hhat run example.hat
```

### Using the REPL (Future)

```bash
# Interactive mode (planned feature)
hhat repl
> main { print("Hello!") }
Hello!
```

## Complete Examples

### Example Projects

Check out complete example projects:

- **Quantum Teleportation**: Demonstrating entanglement and measurement
- **Grover's Algorithm**: Quantum search algorithm
- **Quantum Fourier Transform**: Core component of many algorithms
- **Variational Algorithm**: Hybrid quantum-classical optimization

(Note: These will be added as H-hat development progresses)

## Contributing Examples

Help grow the example collection!

### What Makes a Good Example

✅ **Good examples**:
- Self-contained and complete
- Well-commented
- Show one concept clearly
- Include expected output
- Are actually tested

❌ **Avoid**:
- Complex examples for basic concepts
- Examples that don't run
- Unclear or missing explanations
- Multiple unrelated concepts

### Submit Your Example

1. Create your example file
2. Test that it works
3. Add comments and explanation
4. Submit a PR to the docs
5. Add to the examples index

[Contributing guide →](../contributing/guide.md)

## Example Index

### Basic Examples

<div class="grid" markdown>

:material-code-braces: **[First Code](basic/first_code.md)**
:   Your first H-hat program

:material-variable: **[Variables & Types](basic/variables.md)**
:   Declaring and using variables

:material-function: **[Functions](basic/functions.md)**
:   Defining and calling functions

</div>

### Quantum Examples

<div class="grid" markdown>

:material-atom-variant: **[Quantum Types](quantum/quantum_types.md)**
:   Working with quantum data types

:material-creation: **[Casting Quantum](quantum/casting.md)**
:   Converting between quantum and classical

:material-gate: **[Quantum Operations](quantum/operations.md)**
:   Applying quantum gates and operations

</div>

### Advanced Examples

<div class="grid" markdown>

:material-shape: **[Custom Types](advanced/custom_types.md)**
:   Defining structs and enums

:material-phone: **[Calling Functions](advanced/calling_functions.md)**
:   Function overloading and generics

</div>

## Code Snippets

### Quick Reference

Common patterns for copy-paste:

#### Hello World
```heather
main {
    print("Hello, world!")
}
```

#### Variable Declaration
```heather
let x:i32 = 42
let y:f64 = 3.14
let z:bool = true
```

#### Function Definition
```heather
fn add(a:i32, b:i32) -> i32 {
    add(a, b)
}
```

#### Quantum State
```heather
let q:qubit = |0>
let q2:qubit = h(q)
let result:bool = cast(q2, bool)
```

#### Struct Definition
```heather
type Point {
    x:f64
    y:f64
}
```

## External Resources

### Community Examples

Check out examples from the community:

- GitHub repositories using H-hat
- Blog posts with code samples
- Tutorial videos (coming soon)
- Research papers implementing algorithms

### Related Documentation

- [Heather Syntax](../dialects/heather/syntax.md) - Complete syntax guide
- [Language Concepts](../core/index.md) - Core concepts explained
- [Getting Started](../getting_started.md) - Installation and basics

## Next Steps

<div class="grid cards" markdown>

-   __Start with Basics__

    Learn fundamental concepts

    [:octicons-arrow-right-24: First Code](basic/first_code.md)

-   __Try Quantum__

    Explore quantum programming

    [:octicons-arrow-right-24: Quantum Types](quantum/quantum_types.md)

-   __Go Advanced__

    Master complex patterns

    [:octicons-arrow-right-24: Custom Types](advanced/custom_types.md)

-   __Join Community__

    Share your examples

    [:octicons-arrow-right-24: Discord](http://discord.unitary.foundation)

</div>

---

**Learn by doing!** Try modifying the examples and see what happens. The best way to learn H-hat is through experimentation. 🚀
