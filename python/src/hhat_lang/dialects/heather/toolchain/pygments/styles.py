"""
Custom Pygments styles for H-hat Heather dialect.

Provides dark and light theme styles with carefully chosen colors
for optimal readability and visual identity.
"""

from __future__ import annotations

from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
)

from .colors import HhatColors


class HhatDarkStyle(Style):
    """
    Dark theme style for H-hat Heather syntax highlighting.
    
    Based on the official H-hat color palette with quantum-inspired colors.
    Designed for comfortable reading in low-light environments.
    """
    
    name = "hhat-dark"
    
    background_color = HhatColors.Dark.BG
    highlight_color = HhatColors.Dark.CURSOR_LINE
    line_number_color = HhatColors.Dark.LINE_NUMBER
    line_number_background_color = HhatColors.Dark.BG
    line_number_special_color = HhatColors.Dark.FG
    line_number_special_background_color = HhatColors.Dark.SELECTION
    
    styles = {
        Text:                      HhatColors.Dark.FG,
        Whitespace:                "",
        Error:                     f"bold {HhatColors.Dark.ERROR}",
        
        # Comments
        Comment:                   f"italic {HhatColors.Dark.COMMENT}",
        Comment.Multiline:         f"italic {HhatColors.Dark.COMMENT}",
        Comment.Preproc:           f"{HhatColors.Dark.META}",
        Comment.Single:            f"italic {HhatColors.Dark.COMMENT}",
        Comment.Special:           f"bold italic {HhatColors.Dark.COMMENT}",
        
        # Keywords
        Keyword:                   f"bold {HhatColors.Dark.KEYWORD}",
        Keyword.Constant:          f"bold {HhatColors.Dark.QUANTUM_TYPE}",
        Keyword.Declaration:       f"bold {HhatColors.Dark.KEYWORD_TYPE}",
        Keyword.Namespace:         f"bold {HhatColors.Dark.KEYWORD}",
        Keyword.Pseudo:            f"bold {HhatColors.Dark.KEYWORD_CONTROL}",
        Keyword.Reserved:          f"bold {HhatColors.Dark.KEYWORD}",
        Keyword.Type:              f"bold {HhatColors.Dark.KEYWORD_TYPE}",
        
        # Names
        Name:                      HhatColors.Dark.FG,
        Name.Attribute:            HhatColors.Dark.TRAIT,
        Name.Builtin:              HhatColors.Dark.QUANTUM_TYPE,
        Name.Builtin.Pseudo:       HhatColors.Dark.QUANTUM_GATE,
        Name.Class:                f"bold {HhatColors.Dark.CLASS}",
        Name.Constant:             HhatColors.Dark.CONSTANT,
        Name.Decorator:            HhatColors.Dark.META,
        Name.Entity:               HhatColors.Dark.FG,
        Name.Exception:            f"bold {HhatColors.Dark.ERROR}",
        Name.Function:             HhatColors.Dark.FUNCTION,
        Name.Function.Magic:       HhatColors.Dark.META,
        Name.Label:                HhatColors.Dark.CONSTANT,
        Name.Namespace:            HhatColors.Dark.MODIFIER,
        Name.Tag:                  HhatColors.Dark.TRAIT,
        Name.Variable:             HhatColors.Dark.FG,
        Name.Variable.Class:       HhatColors.Dark.CLASS,
        Name.Variable.Global:      HhatColors.Dark.CONSTANT,
        Name.Variable.Instance:    HhatColors.Dark.FG,
        Name.Variable.Magic:       HhatColors.Dark.QUANTUM_VAR,
        
        # Numbers
        Number:                    HhatColors.Dark.NUMBER,
        Number.Bin:                HhatColors.Dark.NUMBER,
        Number.Float:              HhatColors.Dark.NUMBER,
        Number.Hex:                HhatColors.Dark.NUMBER,
        Number.Integer:            HhatColors.Dark.NUMBER,
        Number.Integer.Long:       HhatColors.Dark.NUMBER,
        Number.Oct:                HhatColors.Dark.NUMBER,
        
        # Operators
        Operator:                  HhatColors.Dark.OPERATOR,
        Operator.Word:             f"bold {HhatColors.Dark.KEYWORD}",
        
        # Punctuation
        Punctuation:               HhatColors.Dark.PUNCTUATION,
        
        # Strings
        String:                    HhatColors.Dark.STRING,
        String.Backtick:           HhatColors.Dark.STRING,
        String.Char:               HhatColors.Dark.STRING,
        String.Doc:                f"italic {HhatColors.Dark.COMMENT}",
        String.Double:             HhatColors.Dark.STRING,
        String.Escape:             f"bold {HhatColors.Dark.OPERATOR}",
        String.Heredoc:            HhatColors.Dark.STRING,
        String.Interpol:           HhatColors.Dark.OPERATOR,
        String.Other:              HhatColors.Dark.STRING,
        String.Regex:              HhatColors.Dark.QUANTUM_STATE,
        String.Single:             HhatColors.Dark.STRING,
        String.Symbol:             HhatColors.Dark.QUANTUM_STATE,
    }


class HhatLightStyle(Style):
    """
    Light theme style for H-hat Heather syntax highlighting.
    
    Based on the official H-hat color palette with quantum-inspired colors.
    Designed for comfortable reading in bright environments.
    """
    
    name = "hhat-light"
    
    background_color = HhatColors.Light.BG
    highlight_color = HhatColors.Light.CURSOR_LINE
    line_number_color = HhatColors.Light.LINE_NUMBER
    line_number_background_color = HhatColors.Light.BG
    line_number_special_color = HhatColors.Light.FG
    line_number_special_background_color = HhatColors.Light.SELECTION
    
    styles = {
        Text:                      HhatColors.Light.FG,
        Whitespace:                "",
        Error:                     f"bold {HhatColors.Light.ERROR}",
        
        # Comments
        Comment:                   f"italic {HhatColors.Light.COMMENT}",
        Comment.Multiline:         f"italic {HhatColors.Light.COMMENT}",
        Comment.Preproc:           f"{HhatColors.Light.META}",
        Comment.Single:            f"italic {HhatColors.Light.COMMENT}",
        Comment.Special:           f"bold italic {HhatColors.Light.COMMENT}",
        
        # Keywords
        Keyword:                   f"bold {HhatColors.Light.KEYWORD}",
        Keyword.Constant:          f"bold {HhatColors.Light.QUANTUM_TYPE}",
        Keyword.Declaration:       f"bold {HhatColors.Light.KEYWORD_TYPE}",
        Keyword.Namespace:         f"bold {HhatColors.Light.KEYWORD}",
        Keyword.Pseudo:            f"bold {HhatColors.Light.KEYWORD_CONTROL}",
        Keyword.Reserved:          f"bold {HhatColors.Light.KEYWORD}",
        Keyword.Type:              f"bold {HhatColors.Light.KEYWORD_TYPE}",
        
        # Names
        Name:                      HhatColors.Light.FG,
        Name.Attribute:            HhatColors.Light.TRAIT,
        Name.Builtin:              HhatColors.Light.QUANTUM_TYPE,
        Name.Builtin.Pseudo:       HhatColors.Light.QUANTUM_GATE,
        Name.Class:                f"bold {HhatColors.Light.CLASS}",
        Name.Constant:             HhatColors.Light.CONSTANT,
        Name.Decorator:            HhatColors.Light.META,
        Name.Entity:               HhatColors.Light.FG,
        Name.Exception:            f"bold {HhatColors.Light.ERROR}",
        Name.Function:             HhatColors.Light.FUNCTION,
        Name.Function.Magic:       HhatColors.Light.META,
        Name.Label:                HhatColors.Light.CONSTANT,
        Name.Namespace:            HhatColors.Light.MODIFIER,
        Name.Tag:                  HhatColors.Light.TRAIT,
        Name.Variable:             HhatColors.Light.FG,
        Name.Variable.Class:       HhatColors.Light.CLASS,
        Name.Variable.Global:      HhatColors.Light.CONSTANT,
        Name.Variable.Instance:    HhatColors.Light.FG,
        Name.Variable.Magic:       HhatColors.Light.QUANTUM_VAR,
        
        # Numbers
        Number:                    HhatColors.Light.NUMBER,
        Number.Bin:                HhatColors.Light.NUMBER,
        Number.Float:              HhatColors.Light.NUMBER,
        Number.Hex:                HhatColors.Light.NUMBER,
        Number.Integer:            HhatColors.Light.NUMBER,
        Number.Integer.Long:       HhatColors.Light.NUMBER,
        Number.Oct:                HhatColors.Light.NUMBER,
        
        # Operators
        Operator:                  HhatColors.Light.OPERATOR,
        Operator.Word:             f"bold {HhatColors.Light.KEYWORD}",
        
        # Punctuation
        Punctuation:               HhatColors.Light.PUNCTUATION,
        
        # Strings
        String:                    HhatColors.Light.STRING,
        String.Backtick:           HhatColors.Light.STRING,
        String.Char:               HhatColors.Light.STRING,
        String.Doc:                f"italic {HhatColors.Light.COMMENT}",
        String.Double:             HhatColors.Light.STRING,
        String.Escape:             f"bold {HhatColors.Light.OPERATOR}",
        String.Heredoc:            HhatColors.Light.STRING,
        String.Interpol:           HhatColors.Light.OPERATOR,
        String.Other:              HhatColors.Light.STRING,
        String.Regex:              HhatColors.Light.QUANTUM_STATE,
        String.Single:             HhatColors.Light.STRING,
        String.Symbol:             HhatColors.Light.QUANTUM_STATE,
    }
