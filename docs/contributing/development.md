# Development Setup

Set up your development environment for contributing to H-hat.

## Prerequisites

### General Requirements

* **Git**: Version control
* **Text Editor/IDE**: Your choice (VS Code, Vim, IntelliJ, etc.)
* **Terminal**: Command-line access

### Language-Specific Requirements

=== "Rust"

    * **Rust**: 1.70 or later
    * **Cargo**: Comes with Rust
    * **Build tools**: Platform-specific (see below)

=== "Python"

    * **Python**: 3.9 or later
    * **pip**: Package installer
    * **Virtual environment**: venv or similar

## Installation

### 1. Install Rust (Primary Implementation)

#### Linux/macOS

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

#### Windows

Download and run [rustup-init.exe](https://rustup.rs/)

#### Verify Installation

```bash
rustc --version
cargo --version
```

### 2. Install Python (Reference Implementation)

#### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora
sudo dnf install python3 python3-pip
```

#### macOS

```bash
# Using Homebrew
brew install python3
```

#### Windows

Download from [python.org](https://www.python.org/downloads/)

#### Verify Installation

```bash
python3 --version
pip3 --version
```

## Clone the Repository

### Fork on GitHub

1. Visit [github.com/hhat-lang/hhat_lang](https://github.com/hhat-lang/hhat_lang)
2. Click "Fork" button
3. Clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/hhat_lang.git
cd hhat_lang
```

### Add Upstream Remote

```bash
git remote add upstream https://github.com/hhat-lang/hhat_lang.git
git remote -v
```

## Rust Development Setup

### Build the Project

```bash
cd rust/hhat_lang

# Development build
cargo build

# Release build
cargo build --release
```

### Run Tests

```bash
# All tests
cargo test

# Specific test
cargo test test_name

# With output
cargo test -- --nocapture

# Specific package
cargo test -p hhat_lang
```

### Code Quality Tools

#### Install Additional Tools

```bash
# Clippy (linter)
rustup component add clippy

# Rustfmt (formatter)
rustup component add rustfmt

# Cargo audit (security)
cargo install cargo-audit
```

#### Run Quality Checks

```bash
# Format code
cargo fmt

# Check formatting
cargo fmt -- --check

# Run linter
cargo clippy

# With all warnings
cargo clippy -- -W clippy::all

# Security audit
cargo audit
```

### IDE Setup

#### VS Code

Install extensions:

```bash
code --install-extension rust-lang.rust-analyzer
code --install-extension vadimcn.vscode-lldb
code --install-extension serayuzgur.crates
```

#### IntelliJ/CLion

Install the Rust plugin from the marketplace.

### Development Workflow

```bash
# 1. Create a branch
git checkout -b feature/my-feature

# 2. Make changes
# ... edit files ...

# 3. Check your code
cargo check
cargo clippy
cargo fmt

# 4. Run tests
cargo test

# 5. Commit
git add .
git commit -m "feat: add feature X"

# 6. Push
git push origin feature/my-feature
```

## Python Development Setup

### Create Virtual Environment

```bash
cd python

# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### Install Dependencies

```bash
# Development mode
pip install -e .

# Development dependencies
pip install -r requirements-dev.txt

# Pre-commit hooks
pip install pre-commit
pre-commit install
```

### Run Tests

```bash
# All tests
pytest

# Specific test
pytest tests/test_file.py::test_name

# With coverage
pytest --cov=hhat_lang

# Coverage report
pytest --cov=hhat_lang --cov-report=html
```

### Code Quality Tools

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy src/

# Linting
flake8 src/
pylint src/

# All checks (pre-commit)
pre-commit run --all-files
```

### IDE Setup

#### VS Code

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.black-formatter
```

#### PyCharm

Python support is built-in.

### Development Workflow

```bash
# 1. Activate venv
source venv/bin/activate

# 2. Create branch
git checkout -b feature/my-feature

# 3. Make changes
# ... edit files ...

# 4. Run checks
black .
mypy src/
pytest

# 5. Commit
git add .
git commit -m "feat: add feature X"

# 6. Push
git push origin feature/my-feature
```

## Documentation Setup

### Install MkDocs

```bash
pip install mkdocs-material
pip install mkdocs-material[recommended]
```

### Serve Documentation Locally

```bash
cd /path/to/hhat_lang
mkdocs serve
```

Visit [http://localhost:8000](http://localhost:8000)

### Build Documentation

```bash
mkdocs build
```

Output in `site/` directory.

## Project Structure

Understanding the project layout:

```
hhat_lang/
├── rust/                   # Rust implementation (primary)
│   └── hhat_lang/
│       ├── src/           # Source code
│       ├── tests/         # Integration tests
│       └── Cargo.toml     # Rust manifest
├── python/                # Python implementation (reference)
│   ├── src/
│   │   └── hhat_lang/     # Python package
│   ├── tests/             # Tests
│   └── pyproject.toml     # Python manifest
├── docs/                  # Documentation
│   ├── index.md           # Homepage
│   ├── getting_started.md
│   └── ...
├── mkdocs.yml             # Docs configuration
└── README.md              # Project readme
```

## Environment Configuration

### Rust Environment Variables

```bash
# Build with backtrace
export RUST_BACKTRACE=1

# Logging
export RUST_LOG=debug

# Optimization level for dev builds
export CARGO_PROFILE_DEV_OPT_LEVEL=1
```

### Python Environment Variables

```bash
# Development mode
export PYTHONPATH="${PYTHONPATH}:$(pwd)/python/src"

# Show deprecation warnings
export PYTHONWARNINGS=default
```

## Troubleshooting

### Rust Issues

**Problem**: Compilation fails with linker errors

**Solution**: Install platform-specific build tools

=== "Linux"

    ```bash
    # Ubuntu/Debian
    sudo apt install build-essential
    
    # Fedora
    sudo dnf groupinstall "Development Tools"
    ```

=== "macOS"

    ```bash
    xcode-select --install
    ```

=== "Windows"

    Install Visual Studio Build Tools

**Problem**: Cargo commands are slow

**Solution**: 
* Use `cargo check` instead of `cargo build` for quick checks
* Enable incremental compilation (default in dev)
* Use `sccache` for caching

### Python Issues

**Problem**: Import errors

**Solution**: 
```bash
# Ensure package is installed
pip install -e .

# Check PYTHONPATH
echo $PYTHONPATH
```

**Problem**: Pre-commit hooks fail

**Solution**:
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Update hooks
pre-commit autoupdate
```

## Performance Tips

### Faster Rust Builds

```bash
# Use mold linker (Linux)
cargo install mold

# Or lld
sudo apt install lld
```

Add to `.cargo/config.toml`:

```toml
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=lld"]
```

### Faster Python Tests

```bash
# Run tests in parallel
pytest -n auto

# Only run failed tests
pytest --lf
```

## Next Steps

<div class="grid cards" markdown>

-   __Start Contributing__

    Learn the contribution workflow

    [:octicons-arrow-right-24: Contributing Guide](guide.md)

-   __Submit a PR__

    Ready to contribute code?

    [:octicons-arrow-right-24: PR Guide](pull_requests.md)

-   __Read Architecture__

    Understand the codebase

    [:octicons-arrow-right-24: Compiler Framework](../core/compiler_framework.md)

-   __Get Help__

    Join the community

    [:octicons-arrow-right-24: Discord](http://discord.unitary.foundation)

</div>

---

**Development environment ready?** Start contributing! 🚀
