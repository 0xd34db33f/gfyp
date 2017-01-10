"""Shared functions and constants"""
import sys

BOLD = ""
END = ""
if sys.platform != 'win32' and sys.stdout.isatty():
    BOLD = "\033[1m"
    END = "\033[0m"

def pretty_print(string):
    """For *nix systems, augment TTY output. For others, strip such syntax."""
    string = string.replace('$BOLD$', BOLD)
    string = string.replace('$END$', END)
    print string
