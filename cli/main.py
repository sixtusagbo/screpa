#!/usr/env python3
"""Screpa CLI tool"""

import typer


def main(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    typer.run(main)
