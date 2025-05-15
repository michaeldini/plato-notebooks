from inspect import getsource
from pathlib import Path
from loguru import logger
import nbformat as nbf
from utils import load_plato,  display_image, compress_image, Illustrator

def generate_notebook(text_title):

    # make a folder just for this notebook
    output_dir = Path(text_title)
    try:
        output_dir.mkdir()
    except FileExistsError:
        raise FileExistsError(f"Directory {text_title} already exists. Please remove it or choose a different title.")
    
    # List of strings to be added as Markdown cells
    strings = load_plato(text_title)

    # Create a new notebook
    notebook = nbf.v4.new_notebook()

    # convert the functions used in the notebook to strings
    # this way we can create the funcs outside the import string
    display_image_code = getsource(display_image)
    compress_image_code = getsource(compress_image)
    illustrator_code = getsource(Illustrator)
    
    # import utils and define the title
    notebook.cells.append(nbf.v4.new_code_cell(f"""
import json
import hashlib

import base64
import openai
from loguru import logger
import os
from IPython.display import Image, display
from PIL import Image as PILImage
from pathlib import Path

logger.remove()  # Remove the default handler that logs to stderr
logger.add("{text_title}.log", format="{{time}} {{level}} {{message}}", level="DEBUG", rotation="1 MB", compression="zip")

openai.api_key = os.environ['OPENAI_API_KEY']

{illustrator_code}

{display_image_code}

{compress_image_code}

client = openai.OpenAI()
illustrator = Illustrator()
"""))

    # Iterate through the list and add Markdown and Code cells
    for i, text in enumerate(strings):

        # Add a Code cell for the user to generate an image
        code_cell = nbf.v4.new_code_cell("# Generate image for text below\ndisplay_image(illustrator(''))")
        notebook.cells.append(code_cell)

        # Add a Markdown cell of the text
        markdown_cell = nbf.v4.new_markdown_cell(text)
        notebook.cells.append(markdown_cell)

        # Add a Markdown cell for the user to add a note
        note_cell = nbf.v4.new_markdown_cell("**Note:** Add your notes here.")
        notebook.cells.append(note_cell)

    # Save the notebook to a file
    notebook_file = output_dir / f"{text_title}.ipynb"
    with open(notebook_file, "w") as f:
        nbf.write(notebook, f)

    logger.info(f"Notebook '{text_title}.ipynb' has been created in the '{text_title}' directory.")
