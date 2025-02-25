#!/usr/env python3
"""Screpa CLI tool"""

from typer import Typer
from rich import print
from rich.console import Console
from rich.table import Table

app = Typer()
console = Console()

data = {
    "name": "Rick",
    "age": 42,
    "items": [{"name": "Portal Gun"}, {"name": "Plumbus"}],
    "active": True,
    "affiliation": None,
}


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


@app.command()
def greet(name: str, lastname: str = "", formal: bool = False):
    """
    Greet NAME, optionally with a --lastname.

    If --formal is used, greet very formally.
    """
    if formal:
        print(f"Good day Ms. {name} {lastname}.")
    else:
        print(f"Hello {name} {lastname}")


@app.command()
def printing():
    """Printing and colors"""
    print("Here's the data:")
    print(data)


@app.command()
def markup():
    """Custom markup, even emojis! Woah!"""
    print(
        "[bold red]Alert![/bold red] [green]Portal gun[/green] shooting! :boom:"
    )


@app.command()
def table():
    """Table printing"""
    table = Table("Name", "Item")
    table.add_row("Rick", "Portal Gun")
    table.add_row("Morty", "Planetina")
    console.print(table)


@app.command()
def stderror():
    """Standard error"""
    err_console = Console(stderr=True)
    err_console.print("This is written in standard error")


if __name__ == "__main__":
    app()
