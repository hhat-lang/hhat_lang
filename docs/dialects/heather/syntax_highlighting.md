# Syntax Highlighting Setup

This document explains how to enable H-hat Heather syntax highlighting in various contexts.

## MkDocs Documentation

The H-hat Heather Pygments lexer is automatically registered when the `hhat-lang` package is installed with the `heather` extras:

```bash
pip install -e ".[heather]"
```

### Supported Language Identifiers

In your markdown code blocks, you can use any of these identifiers:

- `heather` (recommended)
- `hhat`
- `hhat-heather`
- `h-hat`

### Example Usage

````markdown
```heather
main {
    let q:qubit = |0>
    let q2:qubit = h(q)
    let result:bool = cast(q2, bool)
    print(result)
}
```
````

### How It Works

The lexer is registered via `pyproject.toml` entry points:

```toml
[project.entry-points."pygments.lexers"]
heather = "hhat_lang.dialects.heather.toolchain.pygments:HeatherLexer"
hhat = "hhat_lang.dialects.heather.toolchain.pygments:HeatherLexer"
```

When Pygments (used by MkDocs Material's highlight extension) encounters a code block with one of the registered language identifiers, it automatically uses the HeatherLexer for syntax highlighting.

## Supported Syntax Elements

The lexer recognizes and highlights:

### Keywords
- `main`, `fn`, `type`, `const`, `let`, `use`
- `meta-fn`, `metafn`, `modifier`, `metamod`
- `cast`, `if`, `match`, `while`, `for`, `return`, `pipe`

### Types
- **Classical**: `i32`, `u64`, `f32`, `f64`, `bool`, `str`, etc.
- **Quantum**: `@qubit`, `@int`, `@float`, `@bool`, `@bell_t`, etc.
- **Built-in**: `hashmap`, `sample_t`, `fn_t`, `tuple`, `array`, etc.

### Operators
- `::` (return), `*` (cast), `&` (reference), `^` (pointer)
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `&&`, `||`, `!`

### Literals
- **Numbers**: `42`, `3.14`, `@42` (quantum integer)
- **Strings**: `"hello world"`
- **Booleans**: `true`, `false`, `@true`, `@false`
- **Quantum states**: `|0>`, `|1>`, `|+>`, `|->`, `|00>`, `|11>`, etc.

### Quantum Gates
- Single-qubit: `h`, `x`, `y`, `z`, `s`, `t`
- Rotation: `rx`, `ry`, `rz`
- Multi-qubit: `cnot`, `cx`, `swap`, `toffoli`

### Special Syntax
- **Quantum variables**: `@variable` (prefixed with @)
- **Traits**: `#Printable`, `#[Trait1 Trait2]`
- **Modifiers**: `<mut>`, `<ref>`, `<&>`
- **Comments**: `// line comment`, `/* multiline */`

## IDE Integration

### VS Code

Create or update `.vscode/settings.json`:

```json
{
  "files.associations": {
    "*.hat": "heather",
    "*.hhat": "heather"
  }
}
```

Install the Pygments extension for VS Code, which will use the registered lexer.

### Vim/Neovim

If you have Pygments installed and a plugin that uses it (like vim-polyglot), the lexer will be automatically available.

### Emacs

Use the `pygments-mode` package, which will automatically detect and use the registered lexer.

### JetBrains IDEs

Install the "Pygments Lexer Support" plugin to enable Pygments-based highlighting.

## Testing the Lexer

To test the lexer locally:

```python
from pygments import highlight
from pygments.formatters import TerminalFormatter
from hhat_lang.dialects.heather.toolchain.pygments import HeatherLexer

code = '''
main {
    let q:qubit = |0>
    let q2:qubit = h(q)
    let result:bool = cast(q2, bool)
    print(result)
}
'''

lexer = HeatherLexer()
formatter = TerminalFormatter()
print(highlight(code, lexer, formatter))
```

Or from the command line:

```bash
# Install pygmentize if not already installed
pip install pygments

# Highlight a file
pygmentize -l heather example.hat

# Generate HTML
pygmentize -l heather -f html -o output.html example.hat

# List all available lexers (heather should be listed)
pygmentize -L lexers | grep -i heather
```

## Troubleshooting

### Lexer not found

If the lexer is not recognized:

1. Ensure `hhat-lang[heather]` is installed:
   ```bash
   pip install -e ".[heather]"
   ```

2. Verify the entry point is registered:
   ```bash
   python -c "from pygments.lexers import get_lexer_by_name; print(get_lexer_by_name('heather'))"
   ```

3. Clear any Pygments caches:
   ```bash
   rm -rf ~/.cache/pygments
   ```

4. Reinstall the package:
   ```bash
   pip uninstall hhat-lang
   pip install -e ".[heather]"
   ```

### Highlighting not working in MkDocs

1. Ensure MkDocs Material and dependencies are installed:
   ```bash
   pip install mkdocs-material
   ```

2. Check that `pymdownx.highlight` is enabled in `mkdocs.yml`:
   ```yaml
   markdown_extensions:
     - pymdownx.highlight:
         linenums: true
         pygments_lang_class: true
   ```

3. Rebuild the documentation:
   ```bash
   mkdocs build --clean
   ```

### Colors don't look right

The lexer uses standard Pygments token types. Colors are determined by the Pygments style (theme) in use. For MkDocs Material, the colors are defined by the theme's CSS.

To customize colors, you can add custom CSS in `docs/stylesheets/extra.css`:

```css
/* Quantum-specific highlighting */
.highlight .nv-magic { color: #ab47bc; } /* Quantum variables (@var) */
.highlight .ss { color: #7c4dff; }        /* Quantum states (|0>) */
.highlight .nb-pseudo { color: #00897b; } /* Quantum gates */
```

## Contributing

To improve the lexer:

1. Edit `python/src/hhat_lang/dialects/heather/toolchain/pygments/lexer.py`
2. Add tests for new syntax patterns
3. Update this documentation
4. Submit a pull request

See the [Contributing Guide](../../contributing/guide.md) for details.
