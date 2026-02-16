# H-hat Visual Identity

This document defines the official visual identity for the H-hat quantum programming language, including color palettes, typography, and usage guidelines.

## Color Palette

The H-hat color palette is designed to evoke quantum computing concepts while maintaining excellent readability. All colors avoid pure white (#ffffff) and pure black (#000000) for visual comfort.

### Primary Brand Colors

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Quantum Purple | `#7c4dff` | Primary brand color, quantum computing emphasis |
| Quantum Blue | `#448aff` | Secondary brand, superposition concepts |
| Entangle Pink | `#ff4081` | Accent color, entanglement emphasis |
| Measurement Teal | `#00bfa5` | Success states, measurement results |

### Dark Theme

**Background & Foreground:**
- Background: `#1e1e2e` (dark blue-gray, not pure black)
- Foreground: `#cdd6f4` (light lavender, not pure white)
- Selection: `#45475a`
- Current Line: `#313244`

**Syntax Highlighting:**

| Element | Color | Hex Code |
|---------|-------|----------|
| Keywords | Purple | `#cba6f7` |
| Type Keywords | Blue | `#89b4fa` |
| Control Flow | Red-Pink | `#f38ba8` |
| Strings | Green | `#a6e3a1` |
| Numbers | Orange | `#fab387` |
| Comments | Gray | `#6c7086` |
| Functions | Cyan | `#89dceb` |
| Types/Classes | Yellow | `#f9e2af` |
| Constants | Pink | `#f5c2e7` |
| Operators | Teal | `#94e2d5` |

**Quantum-Specific:**

| Element | Color | Hex Code |
|---------|-------|----------|
| Quantum Types (`@qubit`) | Light Purple | `#d4a5ff` |
| Quantum Gates (`h`, `cnot`) | Mint | `#80ffdb` |
| Quantum States (`\|0>`, `\|+>`) | Violet | `#b794f6` |
| Quantum Variables (`@var`) | Lavender | `#e0aaff` |
| Traits (`#Printable`) | Pink | `#ffc6ff` |
| Modifiers (`<mut>`) | Light Blue | `#a0c4ff` |
| Meta-programming | Peach | `#ffd6a5` |

### Light Theme

**Background & Foreground:**
- Background: `#eff1f5` (light gray-blue, not pure white)
- Foreground: `#4c4f69` (dark gray, not pure black)
- Selection: `#dce0e8`
- Current Line: `#e6e9ef`

**Syntax Highlighting:**

| Element | Color | Hex Code |
|---------|-------|----------|
| Keywords | Purple | `#8839ef` |
| Type Keywords | Blue | `#1e66f5` |
| Control Flow | Red | `#d20f39` |
| Strings | Green | `#40a02b` |
| Numbers | Orange | `#fe640b` |
| Comments | Gray | `#9ca0b0` |
| Functions | Cyan | `#209fb5` |
| Types/Classes | Gold | `#df8e1d` |
| Constants | Pink | `#ea76cb` |
| Operators | Teal | `#179299` |

**Quantum-Specific:**

| Element | Color | Hex Code |
|---------|-------|----------|
| Quantum Types | Deep Purple | `#7c3aed` |
| Quantum Gates | Dark Teal | `#0d9488` |
| Quantum States | Violet | `#8b5cf6` |
| Quantum Variables | Purple | `#a855f7` |
| Traits | Magenta | `#d946ef` |
| Modifiers | Blue | `#3b82f6` |
| Meta-programming | Amber | `#f59e0b` |

## Typography

### Documentation Font

**Body Text:** Inter
- Clean, modern sans-serif
- Excellent readability at all sizes
- Good for technical documentation

**Code:** JetBrains Mono
- Designed specifically for developers
- Excellent monospace font with ligatures
- Clear distinction between similar characters (0/O, 1/l/I)

**Fallback Stack:**
```css
/* Body Text */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;

/* Code */
font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 
             'Courier New', monospace;
```

### Font Guidelines

- **Headings**: Inter, 700 weight, slight negative letter-spacing
- **Body**: Inter, 400 weight, 1.7 line-height for readability
- **Code**: JetBrains Mono, 400 weight, ligatures enabled
- **Bold**: 600-700 weight (avoid 900+ for accessibility)
- **Emphasis**: Italic, not underline

## Usage in Code

### Python (Pygments)

```python
from hhat_lang.dialects.heather.toolchain.pygments import (
    HhatDarkStyle,
    HhatLightStyle,
    HhatColors,
    get_color_palette
)

# Get dark theme colors
dark_palette = get_color_palette("dark")
print(dark_palette["KEYWORD"])  # #cba6f7

# Use in Pygments
from pygments import highlight
from pygments.formatters import HtmlFormatter
from hhat_lang.dialects.heather.toolchain.pygments import HeatherLexer

code = "main { print('Hello, Quantum!') }"
lexer = HeatherLexer()
formatter = HtmlFormatter(style=HhatDarkStyle)
html = highlight(code, lexer, formatter)
```

### CSS (Web/Documentation)

```css
/* Import H-hat colors */
@import url('hhat-colors.css');

/* Use CSS variables */
.my-element {
  color: var(--hhat-quantum-purple);
  background: var(--md-default-bg-color);
}

/* Or use hex values directly */
.quantum-highlight {
  color: #7c4dff;
}
```

### MkDocs Configuration

```yaml
theme:
  name: material
  palette:
    # Light mode
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: deep purple
      accent: pink
    # Dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: deep purple
      accent: pink
  font:
    text: Inter
    code: JetBrains Mono

markdown_extensions:
  - pymdownx.highlight:
      pygments_style: hhat-dark

extra_css:
  - stylesheets/hhat-colors.css
```

## Design Principles

### 1. Quantum-Inspired

Colors evoke quantum computing concepts:
- **Purple/Violet**: Quantum states, superposition
- **Blue/Cyan**: Classical computing, deterministic operations
- **Pink/Magenta**: Entanglement, quantum correlations
- **Teal/Green**: Measurement, observation

### 2. Accessibility First

- WCAG AA contrast ratios minimum
- No pure black or white (reduces eye strain)
- Clear distinction between similar elements
- Color is not the only indicator (use icons, text)

### 3. Consistent & Scalable

- Same colors across all platforms
- CSS variables for easy theming
- Defined semantic meanings for each color
- Extensible for future additions

### 4. Developer-Friendly

- Monospace fonts with ligatures
- Clear syntax highlighting
- Good contrast for long coding sessions
- Comfortable for both light and dark environments

## Assets Location

All visual identity assets are located in:
- **Colors**: `python/src/hhat_lang/dialects/heather/toolchain/pygments/colors.py`
- **Pygments Styles**: `python/src/hhat_lang/dialects/heather/toolchain/pygments/styles.py`
- **CSS**: `docs/stylesheets/hhat-colors.css`

## License

The H-hat color palette, typography guidelines, and associated design assets are released under **CC BY-SA 4.0** (Creative Commons Attribution-ShareAlike 4.0 International).

**You are free to:**
- Share — copy and redistribute the material
- Adapt — remix, transform, and build upon the material

**Under the following terms:**
- **Attribution** — You must give appropriate credit to the H-hat project
- **ShareAlike** — Distributed adaptations must use the same license

## Examples

### Code Block with Full Styling

```heather
// Quantum teleportation example
fn quantum_teleportation(alice:@qubit, bob:@qubit, message:@qubit) -> @qubit {
    // Create entangled pair
    let entangled:@bell_t = pipe alice { h cnot(bob) }
    
    // Alice's operations
    let cx_result:@bell_t = cnot(message, alice)
    let alice_measured:@qubit = h(message)
    
    // Measure Alice's qubits
    let m1:bool = cast(alice_measured, bool)
    let m2:bool = cast(alice, bool)
    
    // Bob's corrections based on measurement
    let bob_corrected:@qubit = if m2 { x(bob) } else { bob }
    let final_bob:@qubit = if m1 { z(bob_corrected) } else { bob_corrected }
    
    :: final_bob  // Return statement
}

main {
    let alice:@qubit = |0>
    let bob:@qubit = |0>
    let message:@qubit = |1>
    
    let result:@qubit = quantum_teleportation(alice, bob, message)
    print("Teleported state:", result)
}
```

This code demonstrates the full color palette in action with proper syntax highlighting.

## Contributing

When proposing changes to the visual identity:

1. Ensure colors maintain accessibility standards (WCAG AA minimum)
2. Test in both light and dark themes
3. Verify readability with long code samples
4. Update this documentation with rationale
5. Include visual examples

## Resources

- [Inter Font](https://rsms.me/inter/)
- [JetBrains Mono Font](https://www.jetbrains.com/lp/mono/)
- [Pygments Documentation](https://pygments.org/)
- [MkDocs Material Theme](https://squidfunk.github.io/mkdocs-material/)
- [WCAG Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
