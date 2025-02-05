#!/usr/env python3
"""Screpa CLI tool"""

from typer import Typer

app = Typer()


@app.command()
def hello(name: str):
    """Says Hello to an entity"""
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
