import typer
from generate_notebook import generate_notebook
import utils
from parsers import TITLE_TO_PARSER_FUNCTION_MAP

app = typer.Typer()

@app.command(help="Accepts the title of a book from the user.")
def title(title: str):
    """
    Accepts the title of a book from the user and parses the corresponding text.
    Args:
        title (str): The title of the book.
    
    Returns:
        None
    """
    if title not in TITLE_TO_PARSER_FUNCTION_MAP:
        typer.echo(f"Error: '{title}' is not a valid title. Use the 'titles' command to see available options.")
        raise typer.Exit(code=1)

    typer.echo(f"The title of the book is: {title}")

    typer.echo("Parsing the selected text...")
    TITLE_TO_PARSER_FUNCTION_MAP[title]()

    typer.echo(f"Success! The text for '{title}' has been parsed.")

    typer.echo("Generating notebook...")
    generate_notebook(title)
    
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

