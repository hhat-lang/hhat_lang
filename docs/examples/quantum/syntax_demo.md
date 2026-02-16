# Syntax Highlighting Demo

This page demonstrates the H-hat Heather syntax highlighting capabilities.

## Basic Program

```heather
main {
    let x:i32 = 42
    let y:f64 = 3.14
    print(x, y)
}
```

## Quantum Computing

```heather
main {
    // Create a qubit in |0> state
    let q:qubit = |0>
    
    // Apply Hadamard gate
    let q2:qubit = h(q)
    
    // Measure the qubit
    let result:bool = cast(q2, bool)
    print(result)
}
```

## Bell State

```heather
fn create_bell_state(q1:qubit, q2:qubit) -> @bell_t {
    // Apply Hadamard to first qubit
    let q1_super:qubit = h(q1)
    
    // Apply CNOT gate
    let bell:@bell_t = cnot(q1_super, q2)
    
    :: bell
}

main {
    let q1:qubit = |0>
    let q2:qubit = |0>
    let entangled:@bell_t = create_bell_state(q1, q2)
    print(entangled)
}
```

## Type Definitions

```heather
type Point {
    x:f64,
    y:f64
}

type QuantumRegister {
    qubits:array<@qubit>,
    size:u32
}

fn distance(p1:Point, p2:Point) -> f64 {
    let dx:f64 = p2.x - p1.x
    let dy:f64 = p2.y - p1.y
    let dist_sq:f64 = dx * dx + dy * dy
    :: sqrt(dist_sq)
}
```

## Traits and Modifiers

```heather
type MyType #[Printable Debug] {
    value:i32 <mut>
}

fn modify_value<T #Printable>(item:&T <mut>) {
    item.value = item.value + 1
}

main {
    let obj:MyType = MyType { value: 10 }
    modify_value(&obj)
    print(obj)
}
```

## Pattern Matching

```heather
fn classify_number(x:i32) -> str {
    match x {
        0 => "zero",
        1 | 2 | 3 => "small",
        n if n < 0 => "negative",
        _ => "large"
    }
}

fn process_quantum_state(q:@qubit) -> str {
    match cast(q, bool) {
        @true => "measured |1>",
        @false => "measured |0>",
        _ => "superposition"
    }
}
```

## Advanced Quantum Operations

```heather
fn quantum_teleportation(alice:@qubit, bob:@qubit, message:@qubit) -> @qubit {
    // Create entangled pair
    let alice_had:@qubit = h(alice)
    let entangled:@bell_t = cnot(alice_had, bob)
    
    // Alice's operations
    let cx_result:@bell_t = cnot(message, alice)
    let alice_measured:@qubit = h(message)
    
    // Measure Alice's qubits
    let m1:bool = cast(alice_measured, bool)
    let m2:bool = cast(alice, bool)
    
    // Bob's corrections
    let bob_corrected:@qubit = if m2 { x(bob) } else { bob }
    let final_bob:@qubit = if m1 { z(bob_corrected) } else { bob_corrected }
    
    :: final_bob
}
```

## Control Flow

```heather
fn fibonacci(n:u32) -> u32 {
    if n <= 1 {
        :: n
    }
    
    let mut a:u32 = 0
    let mut b:u32 = 1
    
    for i in 2..=n {
        let temp:u32 = a + b
        a = b
        b = temp
    }
    
    :: b
}

fn quantum_loop() {
    let mut qubits:array<@qubit> = []
    
    for i in 0..10 {
        let q:@qubit = |0>
        let q_super:@qubit = h(q)
        qubits.push(q_super)
    }
    
    pipe qubits 
        |> measure_all 
        |> print
}
```

## Meta-programming

```heather
meta-fn generate_adder(type_name:str) {
    // Generate code at compile time
    fn add_{type_name}(a:{type_name}, b:{type_name}) -> {type_name} {
        :: a + b
    }
}

modifier inline {
    // Apply optimization
    #[inline(always)]
}

@inline
fn fast_multiply(a:i32, b:i32) -> i32 {
    :: a * b
}
```

## Complex Types

```heather
type Circuit {
    gates:array<fn_t>,
    qubits:@u32,
    depth:u32
}

type Measurement<T> {
    state:T,
    probability:f64,
    samples:array<sample_t>
}

fn apply_circuit(circuit:Circuit, input:array<@qubit>) -> array<@qubit> {
    let mut qubits:array<@qubit> = input
    
    for gate in circuit.gates {
        qubits = gate(qubits)
    }
    
    :: qubits
}
```

## Comments and Documentation

```heather
// This is a single-line comment

/*
 * Multi-line comment
 * for detailed explanations
 */

/// Documentation comment
/// Describes the function below
fn documented_function(x:i32) -> i32 {
    :: x * 2
}

main {
    // Initialize quantum state
    let q:@qubit = |+>  // Superposition state
    
    /* Apply quantum operations
       to demonstrate interference */
    let result:@qubit = pipe q
        |> h
        |> x
        |> h
    
    print(result)
}
```

## Error Handling

```heather
type Result<T, E> {
    ok:option<T>,
    err:option<E>
}

fn safe_divide(a:f64, b:f64) -> Result<f64, str> {
    if b == 0.0 {
        :: Result { ok: none, err: some("division by zero") }
    }
    
    :: Result { ok: some(a / b), err: none }
}

main {
    match safe_divide(10.0, 2.0) {
        Result { ok: some(value), err: none } => print(value),
        Result { ok: none, err: some(msg) } => print("Error:", msg),
        _ => print("Unknown error")
    }
}
```

This demonstrates the comprehensive syntax highlighting for H-hat Heather code, including quantum computing constructs, types, control flow, and advanced features.
