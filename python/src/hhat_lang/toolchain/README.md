# Toolchain

The `toolchain/` module provides development tools, command-line interface, project management, and configuration for the H-hat language ecosystem.

## Overview

Provides developer tooling:
- Command-line interface (CLI)
- Project management
- Configuration system
- Notebook integration
- Build tools

## Structure

```
toolchain/
├── __init__.py     # Module exports
├── cli/            # Command-line interface
├── config/         # Configuration management
├── notebooks/      # Jupyter notebook support
└── project/        # Project management
```

## Key Components

### cli/ - Command-Line Interface

**hhat CLI:**
- Build commands
- Run commands
- Test commands
- REPL
- Package management

**Commands:**
```bash
hhat new <project>         # Create new project
hhat build                 # Build project
hhat run [file]            # Run H-hat code
hhat test                  # Run tests
hhat repl                  # Start REPL
hhat check                 # Type checking
hhat fmt                   # Code formatting
hhat doc                   # Generate documentation
```

### config/ - Configuration

**Configuration System:**
- Project configuration
- User preferences
- Backend settings
- Build options
- Environment management

**Configuration Files:**
- `hhat.toml` - Project config
- `.hhatrc` - User preferences
- `hhat.lock` - Dependency lock

### project/ - Project Management

**Project Structure:**
```
my_project/
├── hhat.toml          # Project manifest
├── src/
│   └── main.hat       # Main source
├── tests/             # Test files
├── docs/              # Documentation
└── build/             # Build artifacts
```

**Project Types:**
- Binary applications
- Libraries
- Quantum algorithms
- Mixed classical-quantum

### notebooks/ - Jupyter Integration

**Jupyter Support:**
- H-hat kernel
- Magic commands
- Interactive execution
- Visualization

**Magic Commands:**
```python
%%hhat                  # Execute Heather code
%load_hhat file.hat     # Load file
%time                   # Time execution
%visualize             # Visualize quantum circuit
```

## CLI Usage

### Create Project
```bash
$ hhat new quantum_app
Created quantum_app/
  src/main.hat
  hhat.toml
  README.md
```

### Build Project
```bash
$ cd quantum_app
$ hhat build
   Compiling quantum_app v0.1.0
   Finished release build in 2.3s
```

### Run Project
```bash
$ hhat run
Hello from H-hat!
Quantum result: |+⟩
```

### Interactive REPL
```bash
$ hhat repl
H-hat REPL v0.3.0
>>> let q = |0>
>>> let q2 = h(q)
>>> print(q2)
|+⟩
```

## Configuration

### Project Configuration (hhat.toml)
```toml
[project]
name = "quantum_app"
version = "0.1.0"
dialect = "heather"

[dependencies]
quantum_lib = "1.0"

[build]
optimization = 2
target = "native"

[backend]
default = "qiskit"
shots = 1024
```

### User Configuration (.hhatrc)
```toml
[user]
editor = "vscode"

[backend]
ibmq_token = "your_token_here"

[repl]
auto_import = ["quantum_lib"]
```

## Project Management

### Dependency Management
```bash
# Add dependency
$ hhat add quantum_lib

# Update dependencies
$ hhat update

# Show dependencies
$ hhat deps
```

### Building
```bash
# Debug build
$ hhat build

# Release build
$ hhat build --release

# Check without building
$ hhat check
```

### Testing
```bash
# Run all tests
$ hhat test

# Run specific test
$ hhat test test_quantum

# Show test coverage
$ hhat test --coverage
```

## Jupyter Notebooks

### Install Kernel
```bash
$ hhat jupyter-install
Installing H-hat Jupyter kernel...
Done! Use 'H-hat' kernel in Jupyter.
```

### Notebook Example
```python
# Cell 1: Load H-hat
%load_ext hhat

# Cell 2: Write H-hat code
%%hhat
main {
    let q = |0>
    let q2 = h(q)
    print(q2)
}

# Cell 3: Visualize circuit
%visualize_circuit
```

## Build System

### Build Pipeline
```
Source Files (.hat)
        ↓
Parsing & AST
        ↓
Type Checking
        ↓
IR Generation
        ↓
Optimization
        ↓
Code Generation
        ↓
Backend Compilation
        ↓
Executable / Library
```

### Build Options
- Optimization levels (0-3)
- Target backends
- Debug symbols
- Warnings as errors

## Integration

- **core.compiler**: Compilation pipeline
- **dialects.heather.compiler**: Heather compilation
- **low_level.target_backend**: Backend configuration
- **core.execution**: Execution environment

## Development Workflow

### Typical Workflow
```bash
# 1. Create project
$ hhat new my_quantum_app
$ cd my_quantum_app

# 2. Write code
$ $EDITOR src/main.hat

# 3. Check code
$ hhat check

# 4. Run tests
$ hhat test

# 5. Build
$ hhat build --release

# 6. Run
$ hhat run
```

## Extensions

### Plugin System
Support for extensions:
- Custom linters
- Formatters
- Build tools
- IDE integrations

## Related Documentation
- [CLI Documentation](../../../docs/cli.md)
- [Getting Started](../../../docs/getting_started.md)
- [Toolchain Guide](../../../docs/toolchain.md)
- [Project Configuration](../../../docs/project_config.md)
