import base64
import openai
from loguru import logger
import os
from IPython.display import Image, display
import dill
from pathlib import Path
import nbformat

from PIL import Image as PILImage
from nbconvert.preprocessors import ExecutePreprocessor


TITLES = {
    "Euthyphro": {"text": "texts/euthyphro.txt", "pickle": "pickles/euthyphro.pkl"},
    "Apology": {"text": "texts/apology.txt", "pickle": "pickles/apology.pkl"},
    "Crito": {"text": "texts/crito.txt", "pickle": "pickles/crito.pkl"},
    "Phaedo": {"text": "texts/phaedo.txt", "pickle": "pickles/phaedo.pkl"},
}


openai.api_key = os.environ['OPENAI_API_KEY']
client = openai.OpenAI()


logger.remove()  # Remove the default handler that logs to stderr
logger.add("plato_app.log", format="{{time}} {{level}} {{message}}", level="DEBUG", rotation="1 MB", compression="zip")

# Used in parsing the text
def create_dialogue_entry(text1, text2):
    if not text1 or not text2:
        raise ValueError("Both text1 and text2 must be provided.")
    return f"{text1.strip()}\n{text2.strip()}"


def load_plato(title):
    if title not in TITLES:
        raise ValueError(f"Invalid title. Please choose from {list(TITLES.keys())}.")
    with open(TITLES[title]["pickle"], "rb") as f:
        return dill.load(f)

# Used to run the parsing notebook
def run_notebook(notebook_path):
    with open(notebook_path) as f:
        notebook = nbformat.read(f, as_version=4)
    
    # Configure the notebook execution
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    
    # Execute the notebook
    ep.preprocess(notebook, {'metadata': {'path': './'}})
    

class Illustrator:
    def __init__(self, text_title):
        self.text_title = text_title

    def __call__(self, prompt):
        return generate_image(self.text_title, prompt)
    
# Used in the generated notebook
def generate_image(text_title, prompt):

    # Generate shortened filenames to a maximum of 200 characters
    sanitized_prompt = prompt.replace(' ', '_')[:200]  # Limit the prompt part to 200 characters
    original_filename = Path(f"./imgs/original/{text_title}/{sanitized_prompt}.png")
    compressed_filename = Path(f"./imgs/compressed/{text_title}/{sanitized_prompt}.jpg")

    # Create the directories if they don't exist
    original_filename.parent.mkdir(parents=True, exist_ok=True)
    compressed_filename.parent.mkdir(parents=True, exist_ok=True)

    # Check if the compressed file already exists
    if compressed_filename.exists():
        logger.info(f"File '{compressed_filename}' already exists. Skipping image generation.")
        return compressed_filename
    elif prompt.strip() == "":
        return None
    elif original_filename.exists() and not compressed_filename.exists():
        logger.info(f"File '{original_filename}' already exists. Compressing image.")
        return compress_image(original_filename, compressed_filename)
    else:
        logger.info(f"Generating image for prompt: {prompt}")
        # Generate the image using OpenAI's DALL-E
        img = client.images.generate(
            model="dall-e-3",
            prompt=f"{prompt}",
            n=1,
            size="1024x1024",
            response_format="b64_json",
        )
        image_bytes = base64.b64decode(img.data[0].b64_json)
        with open(original_filename, "wb") as f:
            f.write(image_bytes)
            
        return compress_image(original_filename, compressed_filename)

def compress_image(original_filename, compressed_filename):
    # Check if the original file exists
    if not os.path.exists(original_filename):
        logger.error(f"Original file '{original_filename}' does not exist.")
        raise FileNotFoundError(f"Original file '{original_filename}' does not exist.")

    with PILImage.open(original_filename) as img:
        img.save(compressed_filename, "JPEG", quality=85, optimize=True)

    logger.info(f"Compressed image saved to '{compressed_filename}'")
    return compressed_filename

# Used in the generated notebook
def display_image(filename):
    """Display the image in the notebook. filename is the path to the image and also the prompt"""
    if filename is None:
        return 'Did you enter a prompt?'
    else:
        # Display the image
        display(Image(filename, width=400, height=400))

