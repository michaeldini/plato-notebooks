import typer
from pathlib import Path
from utils import run_notebook
from generate_notebook import generate_notebook
import utils

app = typer.Typer()

@app.command(help="Accepts the title of a book from the user.")
def title(title: str):
    """
    Accepts the title of a book from the user.
    """
    notebook_path = Path('notebooks')
    notebook_path.mkdir(parents=True, exist_ok=True)

    typer.echo(f"The title of the book is: {title}")
    typer.echo("Parsing texts...")

    # Run the notebook that processes the text
    run_notebook('parse_texts.ipynb')
    
    typer.echo("Generating notebook...")
    generate_notebook(title, notebook_path / f'{title}_auto-generated.ipynb')
    
    typer.echo("Success! The notebook has been generated. 🚀")

@app.command(help="List all available texts.")
def titles():
    """
    Lists all available texts.
    """
    available_titles = list(utils.TITLES.keys())
    typer.echo("Available texts:")
    for title in available_titles:
        typer.echo(f"- {title}")
if __name__ == "__main__":
    app()
# This code is a simple command-line application using Typer that accepts a book title as input and prints it out.

