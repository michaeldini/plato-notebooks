import typer
from pathlib import Path
from utils import run_notebook
from generate_notebook import generate_notebook
import utils
from parsers import parse_euthyphro, parse_apology, parse_crito, parse_phaedo

app = typer.Typer()

# Map titles to their corresponding parsing functions
TITLE_FUNCTION_MAP = {
    "Euthyphro": parse_euthyphro,
    "Apology": parse_apology,
    "Crito": parse_crito,
    "Phaedo": parse_phaedo,
}

@app.command(help="Accepts the title of a book from the user.")
def title(title: str):
    """
    Accepts the title of a book from the user and parses the corresponding text.
    Args:
        title (str): The title of the book.
    
    Returns:
        None
    """
    if title not in TITLE_FUNCTION_MAP:
        typer.echo(f"Error: '{title}' is not a valid title. Use the 'titles' command to see available options.")
        raise typer.Exit(code=1)

    typer.echo(f"The title of the book is: {title}")

    typer.echo("Parsing the selected text...")
    TITLE_FUNCTION_MAP[title]()

    typer.echo(f"Success! The text for '{title}' has been parsed and saved. 🚀")

    typer.echo("Generating notebook...")
    notebook_path = Path('notebooks')
    notebook_path.mkdir(parents=True, exist_ok=True)
    generate_notebook(title, notebook_path / f'{title}_auto-generated.ipynb')
    
    typer.echo("Success! The notebook has been generated. 🚀")


@app.command(help="List all available texts.")
def titles():
    """
    List all available texts.
    Returns:
        None
    """
    available_titles = list(utils.TITLES.keys())
    typer.echo("Available texts:")
    for title in available_titles:
        typer.echo(f"- {title}")

if __name__ == "__main__":
    app()

