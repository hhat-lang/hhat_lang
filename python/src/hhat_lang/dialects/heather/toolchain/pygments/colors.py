"""
H-hat Color Palette

Defines the official color palette for the H-hat quantum programming language.
All colors are designed to be pleasant to read and provide good contrast
in both light and dark themes.

Colors avoid pure white (#ffffff) and pure black (#000000) for better
visual comfort and modern aesthetics.
"""

from __future__ import annotations


class HhatColors:
    """Official H-hat color palette."""
    
    # Primary Brand Colors
    QUANTUM_PURPLE = "#7c4dff"      # Primary brand color - quantum computing
    QUANTUM_BLUE = "#448aff"        # Secondary brand - superposition
    ENTANGLE_PINK = "#ff4081"       # Accent - entanglement
    MEASUREMENT_TEAL = "#00bfa5"    # Success/measurement - quantum results
    
    # Syntax Highlighting - Dark Theme
    class Dark:
        """Colors for dark theme syntax highlighting."""
        # Background and foreground
        BG = "#1e1e2e"              # Dark blue-gray background (not pure black)
        FG = "#cdd6f4"              # Light lavender foreground (not pure white)
        
        # Syntax elements
        KEYWORD = "#cba6f7"         # Purple - keywords (fn, let, type, etc.)
        KEYWORD_TYPE = "#89b4fa"    # Blue - type keywords
        KEYWORD_CONTROL = "#f38ba8" # Red-pink - control flow (if, match, return)
        
        STRING = "#a6e3a1"          # Green - strings
        NUMBER = "#fab387"          # Orange - numbers
        COMMENT = "#6c7086"         # Gray - comments
        
        FUNCTION = "#89dceb"        # Cyan - function names
        CLASS = "#f9e2af"           # Yellow - type names
        CONSTANT = "#f5c2e7"        # Pink - constants
        
        OPERATOR = "#94e2d5"        # Teal - operators
        PUNCTUATION = "#bac2de"     # Light gray - punctuation
        
        # Quantum-specific
        QUANTUM_TYPE = "#d4a5ff"    # Light purple - quantum types (@qubit)
        QUANTUM_GATE = "#80ffdb"    # Mint - quantum gates (h, cnot)
        QUANTUM_STATE = "#b794f6"   # Violet - quantum states (|0>, |+>)
        QUANTUM_VAR = "#e0aaff"     # Lavender - quantum variables (@var)
        
        # Special
        TRAIT = "#ffc6ff"           # Pink - traits (#Printable)
        MODIFIER = "#a0c4ff"        # Light blue - modifiers (<mut>)
        META = "#ffd6a5"            # Peach - meta-programming
        
        # UI elements
        SELECTION = "#45475a"       # Selection background
        CURSOR_LINE = "#313244"     # Current line highlight
        LINE_NUMBER = "#585b70"     # Line numbers
        ERROR = "#f38ba8"           # Errors
        WARNING = "#fab387"         # Warnings
        INFO = "#89b4fa"            # Information
        HINT = "#94e2d5"            # Hints
    
    # Syntax Highlighting - Light Theme
    class Light:
        """Colors for light theme syntax highlighting."""
        # Background and foreground
        BG = "#eff1f5"              # Light gray-blue background (not pure white)
        FG = "#4c4f69"              # Dark gray foreground (not pure black)
        
        # Syntax elements
        KEYWORD = "#8839ef"         # Purple - keywords
        KEYWORD_TYPE = "#1e66f5"    # Blue - type keywords
        KEYWORD_CONTROL = "#d20f39" # Red - control flow
        
        STRING = "#40a02b"          # Green - strings
        NUMBER = "#fe640b"          # Orange - numbers
        COMMENT = "#9ca0b0"         # Gray - comments
        
        FUNCTION = "#209fb5"        # Cyan - function names
        CLASS = "#df8e1d"           # Yellow/gold - type names
        CONSTANT = "#ea76cb"        # Pink - constants
        
        OPERATOR = "#179299"        # Teal - operators
        PUNCTUATION = "#5c5f77"     # Dark gray - punctuation
        
        # Quantum-specific
        QUANTUM_TYPE = "#7c3aed"    # Deep purple - quantum types
        QUANTUM_GATE = "#0d9488"    # Dark teal - quantum gates
        QUANTUM_STATE = "#8b5cf6"   # Violet - quantum states
        QUANTUM_VAR = "#a855f7"     # Purple - quantum variables
        
        # Special
        TRAIT = "#d946ef"           # Magenta - traits
        MODIFIER = "#3b82f6"        # Blue - modifiers
        META = "#f59e0b"            # Amber - meta-programming
        
        # UI elements
        SELECTION = "#dce0e8"       # Selection background
        CURSOR_LINE = "#e6e9ef"     # Current line highlight
        LINE_NUMBER = "#acb0be"     # Line numbers
        ERROR = "#d20f39"           # Errors
        WARNING = "#fe640b"         # Warnings
        INFO = "#1e66f5"            # Information
        HINT = "#179299"            # Hints


def get_color_palette(theme: str = "dark") -> dict[str, str]:
    """
    Get the complete color palette for a given theme.
    
    Args:
        theme: Either "dark" or "light"
        
    Returns:
        Dictionary mapping color names to hex values
    """
    palette_class = HhatColors.Dark if theme == "dark" else HhatColors.Light
    
    return {
        name: getattr(palette_class, name)
        for name in dir(palette_class)
        if not name.startswith("_") and isinstance(getattr(palette_class, name), str)
    }


def print_palette(theme: str = "dark") -> None:
    """Print the color palette for a given theme."""
    palette = get_color_palette(theme)
    print(f"\n{theme.upper()} THEME COLOR PALETTE")
    print("=" * 50)
    for name, color in palette.items():
        print(f"{name:20s}: {color}")
