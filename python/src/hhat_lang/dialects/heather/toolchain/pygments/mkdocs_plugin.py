"""
MkDocs integration for Heather syntax highlighting.

This module provides a custom formatter for pymdownx.superfences
to enable Heather syntax highlighting in MkDocs documentation.
"""

from __future__ import annotations

from typing import Any

from pygments import highlight
from pygments.formatters import HtmlFormatter

from hhat_lang.dialects.heather.toolchain.pygments import HeatherLexer


def heather_formatter(
    src: str,
    language: str,
    css_class: str,
    options: dict[str, Any] | None = None,
    md: Any = None,
    **kwargs: Any,
) -> str:
    """
    Custom formatter for Heather code blocks in MkDocs.
    
    This formatter is used with pymdownx.superfences to provide
    syntax highlighting for Heather code blocks.
    
    Args:
        src: The source code to highlight
        language: The language identifier (heather, hhat, etc.)
        css_class: CSS class for the code block
        options: Additional options
        md: Markdown instance
        **kwargs: Additional keyword arguments
        
    Returns:
        HTML string with highlighted code
    """
    options = options or {}
    
    # Create the lexer
    lexer = HeatherLexer()
    
    # Create the formatter with proper options
    formatter = HtmlFormatter(
        cssclass=css_class,
        wrapcode=True,
        **options
    )
    
    # Highlight the code
    return highlight(src, lexer, formatter)


def setup_mkdocs_integration() -> dict[str, Any]:
    """
    Set up MkDocs integration for Heather syntax highlighting.
    
    Returns a dictionary suitable for use in mkdocs.yml superfences
    configuration.
    
    Returns:
        Configuration dictionary for pymdownx.superfences
    """
    return {
        "name": "heather",
        "class": "heather",
        "format": heather_formatter,
    }
