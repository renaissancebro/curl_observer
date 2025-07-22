#!/usr/bin/env python3
"""
Plurl CLI entry point

This is the main entry point when plurl is installed as a CLI command.
"""

import sys
import os

# Add current directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import run

def main():
    """Main entry point for the plurl CLI command."""
    try:
        run()
    except KeyboardInterrupt:
        print("\nExiting...", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()