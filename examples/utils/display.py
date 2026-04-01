"""Rich console output helpers for Agent-Harness-101 examples."""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

console = Console()

LAYER_COLORS = {
    'loop': 'blue',
    'tools': 'dark_orange',
    'context': 'purple',
    'persistence': 'green',
    'verification': 'cyan',
    'constraints': 'red',
}


def print_header(title: str, layer: str = '') -> None:
    """Print a styled section header."""
    color = LAYER_COLORS.get(layer, 'white')
    console.print(Panel(title, style=f"bold {color}", expand=False))


def print_step(step: int, description: str) -> None:
    """Print a numbered step in the process."""
    console.print(f"  [dim]{step}.[/dim] {description}")


def print_code(code: str, language: str = 'python', title: str = '') -> None:
    """Print syntax-highlighted code."""
    syntax = Syntax(code, language, theme='monokai', line_numbers=True)
    if title:
        console.print(f"\n[dim]{title}[/dim]")
    console.print(syntax)


def print_result(label: str, value: str, style: str = 'green') -> None:
    """Print a key-value result."""
    console.print(f"  [{style}]{label}:[/{style}] {value}")
