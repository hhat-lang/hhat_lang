# Heather Toolchain

The `toolchain/` module provides developer tooling for the Heather dialect, including syntax highlighting and notebook support.

## Overview

Provides development tools:
- Pygments syntax highlighting
- Jupyter notebook integration
- Code formatting utilities
- IDE integration helpers

## Structure

```
toolchain/
├── __init__.py     # Module exports
├── pygments/       # Syntax highlighting
│   ├── lexer.py            # Heather lexer
│   ├── styles.py           # Color themes
│   ├── colors.py           # Color palette
│   └── mkdocs_plugin.py    # MkDocs integration
└── notebooks/      # Jupyter notebook support
```

## Key Components

### pygments/ - Syntax Highlighting

Complete Pygments integration:

**lexer.py - HeatherLexer:**
- Tokenizes Heather code
- Recognizes all Heather syntax
- Quantum-specific tokens
- Multiple language aliases

**styles.py - Custom Themes:**
- `HhatDarkStyle` - Dark theme
- `HhatLightStyle` - Light theme
- Quantum-inspired colors

**colors.py - Color Palette:**
- Brand colors
- Syntax highlighting colors
- Theme definitions

**mkdocs_plugin.py - MkDocs Integration:**
- Custom formatter for documentation
- Seamless MkDocs integration

### notebooks/ - Jupyter Support

Jupyter notebook integration:
- Heather kernel
- Magic commands
- Interactive execution
- Visualization support

## Syntax Highlighting

### Supported Elements
- Keywords: `fn`, `type`, `let`, etc.
- Types: `i32`, `@qubit`, etc.
- Operators: `::`, `*`, `=>`, etc.
- Literals: `42`, `3.14`, `|0>`, `"hello"`
- Comments: `//`, `/* */`
- Quantum syntax: `@var`, `|state>`, gates

### Language Identifiers
Use in code blocks:
````markdown
```heather
main { print("Hello") }
```

```hhat
// Alternative identifier
```

```hhat-heather
// Another alternative
```
````

### Color Palette

**Quantum Purple**: `#7c4dff` - Primary brand
**Quantum Blue**: `#448aff` - Secondary  
**Entangle Pink**: `#ff4081` - Accent
**Measurement Teal**: `#00bfa5` - Success

## Usage

### Command Line
```bash
# Highlight code
pygmentize -l heather -O style=hhat-dark code.hat

# Generate HTML
pygmentize -l heather -f html -o output.html code.hat
```

### Python API
```python
from pygments import highlight
from pygments.formatters import HtmlFormatter
from hhat_lang.dialects.heather.toolchain.pygments import (
    HeatherLexer,
    HhatDarkStyle
)

code = "main { print('Hello') }"
html = highlight(code, HeatherLexer(), 
                HtmlFormatter(style=HhatDarkStyle))
```

### MkDocs
Automatically applied in documentation:
````markdown
```heather
main {
    let q:@qubit = |0>
    print(q)
}
```
````

## Integration

- **docs/**: Documentation with syntax highlighting
- **toolchain.cli**: CLI with colored output
- **IDE plugins**: VSCode, Vim, etc.

## Related Documentation
- [Heather README](../README.md)
- [Visual Identity](../../../../docs/brand/visual_identity.md)
- [Syntax Highlighting Guide](../../../../docs/dialects/heather/syntax_highlighting.md)
- [Pygments README](pygments/README.md)
