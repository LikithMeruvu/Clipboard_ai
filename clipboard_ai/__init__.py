"""Clipboard AI - A desktop application that monitors the clipboard and processes content using Ollama."""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

# Don't import main module directly to avoid circular imports
__all__ = ["main"] 

def main():
    """Application entry point function."""
    from .main import main as _main
    _main()