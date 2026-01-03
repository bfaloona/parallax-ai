# -*- coding: utf-8 -*-
"""Shared utilities for invoke task modules."""

import sys


class Colors:
    """Terminal colors with Rich fallback and graceful degradation."""

    # Try to use Rich if available
    try:
        from rich.console import Console
        _console = Console()
        _use_rich = True
    except ImportError:
        _use_rich = False
        _console = None

    # ANSI color codes (fallback)
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

    @staticmethod
    def _supports_color():
        """Check if terminal supports color."""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    @staticmethod
    def cmd(text):
        """Format command text with cyan arrow."""
        if Colors._use_rich:
            Colors._console.print(f"[bold cyan]>>[/bold cyan] [cyan]{text}[/cyan]")
            return ""  # Already printed
        elif Colors._supports_color():
            return f"{Colors.BOLD}{Colors.CYAN}>> {text}{Colors.END}"
        else:
            return f">> {text}"

    @staticmethod
    def success(text):
        """Format success text with green checkmark."""
        if Colors._use_rich:
            Colors._console.print(f"[bold green]✓[/bold green] [green]{text}[/green]")
            return ""
        elif Colors._supports_color():
            return f"{Colors.BOLD}{Colors.GREEN}✓ {text}{Colors.END}"
        else:
            return f"[OK] {text}"

    @staticmethod
    def warning(text):
        """Format warning text with yellow warning sign."""
        if Colors._use_rich:
            Colors._console.print(f"[bold yellow]![/bold yellow] [yellow]{text}[/yellow]")
            return ""
        elif Colors._supports_color():
            return f"{Colors.BOLD}{Colors.YELLOW}! {text}{Colors.END}"
        else:
            return f"[WARNING] {text}"

    @staticmethod
    def error(text):
        """Format error text with red X."""
        if Colors._use_rich:
            Colors._console.print(f"[bold red]✗[/bold red] [red]{text}[/red]")
            return ""
        elif Colors._supports_color():
            return f"{Colors.BOLD}{Colors.RED}✗ {text}{Colors.END}"
        else:
            return f"[ERROR] {text}"

    @staticmethod
    def info(text):
        """Format info text with blue icon."""
        if Colors._use_rich:
            Colors._console.print(f"[bold blue]i[/bold blue] [blue]{text}[/blue]")
            return ""
        elif Colors._supports_color():
            return f"{Colors.BOLD}{Colors.BLUE}i {text}{Colors.END}"
        else:
            return f"[INFO] {text}"

    @staticmethod
    def dim(text):
        """Format dimmed text."""
        if Colors._use_rich:
            return f"[dim]{text}[/dim]"
        elif Colors._supports_color():
            return f"{Colors.DIM}{text}{Colors.END}"
        else:
            return text

    @staticmethod
    def command(cmd):
        """Format command line with >> prefix and colored command only."""
        if Colors._use_rich:
            Colors._console.print(f">> [cyan]{cmd}[/cyan]")
            return ""  # Already printed
        elif Colors._supports_color():
            return f">> {Colors.CYAN}{cmd}{Colors.END}"
        else:
            return f">> {cmd}"


__all__ = ['Colors']
