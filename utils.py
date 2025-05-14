import base64
import openai
from loguru import logger
import os
from IPython.display import Image, display
import dill
from pathlib import Path
import hashlib
import json
from PIL import Image as PILImage

TITLES = {
    "Euthyphro": {"text": "texts/euthyphro.txt", "pickle": "pickles/euthyphro.pkl"},
    "Apology": {"text": "texts/apology.txt", "pickle": "pickles/apology.pkl"},
    "Crito": {"text": "texts/crito.txt", "pickle": "pickles/crito.pkl"},
    "Phaedo": {"text": "texts/phaedo.txt", "pickle": "pickles/phaedo.pkl"},
}

# i think this is here for type hinting
openai.api_key = os.environ['OPENAI_API_KEY']
client = openai.OpenAI()


logger.remove()  # Remove the default handler that logs to stderr
logger.add("plato_app.log", format="{{time}} {{level}} {{message}}", level="DEBUG", rotation="1 MB", compression="zip")

def load_plato(title):
    if title not in TITLES:
        raise ValueError(f"Invalid title. Please choose from {list(TITLES.keys())}.")
    with open(TITLES[title]["pickle"], "rb") as f:
        return dill.load(f)


class Illustrator:
    
    # Define the directories for original and compressed images
    original_img_dir = Path("imgs/original")
    compressed_img_dir = Path("imgs/compressed")
    prompt_map_file = Path("imgs/prompt_map.json")  # File to store the map between filenames and prompts

    # Create the directories if they don't exist
    original_img_dir.mkdir(parents=True, exist_ok=True)
    compressed_img_dir.mkdir(parents=True, exist_ok=True)
    prompt_map_file.touch(exist_ok=True)  # Create the file if it doesn't exist

    def __init__(self):
        # Load the prompt map from file
        try:
            with open(self.prompt_map_file, "r") as f:
                self.prompt_map = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.prompt_map = {}

    def __call__(self, prompt):
        return self.generate_image(prompt)
        
    # Used in the generated notebook
    def generate_image(self, prompt):
        # Generate a hash from the prompt for the filename
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        original_filename = Illustrator.original_img_dir / f"{prompt_hash}.png"
        compressed_filename = Illustrator.compressed_img_dir / f"{prompt_hash}.jpg"

        # Save the mapping between the hash and the prompt
        if prompt_hash not in self.prompt_map:
            self.prompt_map[prompt_hash] = prompt
            self._save_prompt_map()

        # Check if the compressed file already exists
        if compressed_filename.exists():
            logger.info(f"File '{compressed_filename}' already exists. Skipping image generation.")
            return compressed_filename
        elif prompt.strip() == "":
            return None # No prompt provided
        elif original_filename.exists() and not compressed_filename.exists():
            logger.info(f"File '{original_filename}' already exists.  Skipping image generation. Compressing image.")
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

    def _save_prompt_map(self):
        """Save the prompt map to a file."""
        with open(self.prompt_map_file, "w") as f:
            json.dump(self.prompt_map, f, indent=4)

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

