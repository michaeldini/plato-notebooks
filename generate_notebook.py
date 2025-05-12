from inspect import getsource
import nbformat as nbf
from utils import load_plato, generate_image, display_image, compress_image

def generate_notebook(text_title, output_path):

    # List of strings to be added as Markdown cells
    strings = load_plato(text_title)

    # Create a new notebook
    notebook = nbf.v4.new_notebook()

    # import utils and define the title
    generate_image_code = getsource(generate_image)
    display_image_code = getsource(display_image)
    compress_image_code = getsource(compress_image)
    notebook.cells.append(nbf.v4.new_code_cell(f"""
import base64
import openai
from loguru import logger
import os
from IPython.display import Image, display
from PIL import Image as PILImage
logger.remove()  # Remove the default handler that logs to stderr
logger.add("plato_app.log", format="{{time}} {{level}} {{message}}", level="DEBUG", rotation="1 MB", compression="zip")
openai.api_key = os.environ['OPENAI_API_KEY']
client = openai.OpenAI()

TITLE = '{text_title}'

{generate_image_code}

{display_image_code}

{compress_image_code}
"""))

    # Iterate through the list and add Markdown and Code cells
    for i, text in enumerate(strings):

        # Add a Code cell with slide type
        code_cell = nbf.v4.new_code_cell("# Generate image for text below\ndisplay_image(generate_image(TITLE, ''))")
        code_cell['metadata']['slideshow'] = {'slide_type': 'slide'}
        notebook.cells.append(code_cell)

        # Add a Markdown cell with slide type
        markdown_cell = nbf.v4.new_markdown_cell(text)
        markdown_cell['metadata']['slideshow'] = {'slide_type': 'fragment'}
        notebook.cells.append(markdown_cell)
        
        # Add a Markdown cell for the user to add a note with slide type
        note_cell = nbf.v4.new_markdown_cell("**Note:** Add your notes here.")
        note_cell['metadata']['slideshow'] = {'slide_type': 'subslide'}
        notebook.cells.append(note_cell)

    # Save the notebook to a file
    with open(output_path, "w") as f:
        nbf.write(notebook, f)

    print(f"Notebook saved to {output_path}")
