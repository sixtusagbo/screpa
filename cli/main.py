#!/usr/env python3
"""Screpa CLI tool"""

from typer import Typer

app = Typer()


@app.command()
def hello(name: str):
    """Says Hello to an entity"""
    print(f"Hello {name}")


@app.command()
def goodbye(name: str, formal: bool = False):
    """Say goodbye to an entity

    Args:
        name (str): Name of an entity
        formal (bool): Formal or informal?
    """
    if formal:
        print(f"Goodbye, Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
