# Quick Start: Using Heather Syntax Highlighting

This guide shows you how to quickly get Heather syntax highlighting working in your H-hat documentation.

## 1. Install the Package

```bash
cd hhat_lang/python
pip install -e .
```

## 2. Verify Installation

```bash
python3 -c "from pygments.lexers import get_lexer_by_name; print(get_lexer_by_name('heather'))"
```

You should see:
```
<hhat_lang.dialects.heather.toolchain.pygments.lexer.HeatherLexer object at 0x...>
```

## 3. Use in Documentation

In your markdown files, use the `heather` language identifier:

````markdown
```heather
main {
    let q:qubit = |0>
    let q2:qubit = h(q)
    print(q2)
}
```
````

## 4. Build and Preview

```bash
cd /path/to/hhat_lang
mkdocs build
mkdocs serve
```

Open http://127.0.0.1:8000 in your browser to see the syntax-highlighted documentation!

## Alternative Language Identifiers

You can use any of these in your code blocks:
- `heather` ← recommended
- `hhat`
- `hhat-heather`
- `h-hat`

## Command Line Usage

Highlight a Heather file:
```bash
pygmentize -l heather mycode.hat
```

Generate HTML:
```bash
pygmentize -l heather -f html -o output.html mycode.hat
```

## Python API

```python
from pygments import highlight
from pygments.formatters import HtmlFormatter
from hhat_lang.dialects.heather.toolchain.pygments import HeatherLexer

code = '''
main {
    let x:i32 = 42
    print(x)
}
'''

lexer = HeatherLexer()
formatter = HtmlFormatter(style='monokai')
html = highlight(code, lexer, formatter)
print(html)
```

## Troubleshooting

### Lexer not found?

1. Reinstall: `pip install -e .`
2. Check: `python3 -c "import pygments.lexers; print(pygments.lexers.get_all_lexers())"`

### Highlighting not working in MkDocs?

1. Ensure `pymdownx.highlight` is in `mkdocs.yml`:
   ```yaml
   markdown_extensions:
     - pymdownx.highlight:
         linenums: true
   ```

2. Rebuild: `mkdocs build --clean`

### Colors look wrong?

The lexer uses standard Pygments token types. Colors come from the Pygments style (theme). For MkDocs Material, colors are defined by the theme's CSS.

## More Information

- Full documentation: [docs/dialects/heather/syntax_highlighting.md](../../../docs/dialects/heather/syntax_highlighting.md)
- Technical details: [README.md](README.md)
- Implementation notes: [IMPLEMENTATION.md](IMPLEMENTATION.md)
- Live demo: [docs/examples/quantum/syntax_demo.md](../../../docs/examples/quantum/syntax_demo.md)

## What Gets Highlighted?

- Keywords: `fn`, `type`, `const`, `let`, `if`, `match`, etc.
- Types: `i32`, `f64`, `qubit`, `@qint`, `@bell_t`, etc.
- Operators: `::`, `=>`, `->`, `*`, `&`, etc.
- Quantum syntax: `|0>`, `@variable`, `h(q)`, etc.
- Comments: `// line` and `/* multiline */`
- Strings, numbers, and all other language constructs

Enjoy your syntax-highlighted Heather code! 🎨
