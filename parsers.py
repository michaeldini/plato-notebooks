from pathlib import Path
import re
import dill
from utils import create_dialogue_entry, TITLES

Path("pickles").mkdir(exist_ok=True)

def process_and_save(key):
    """
    A decorator to handle file reading, processing, and saving.
    :param key: Key to retrieve the input and output file paths from TITLES.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Open the input file
            with open(TITLES[key]["text"], "r", encoding="utf-8-sig") as file:
                text_content = file.read()
            
            # Process the content using the decorated function
            results = func(text_content, *args, **kwargs)
            
            # Save the results to the output file
            with open(TITLES[key]["pickle"], "wb") as file:
                dill.dump(results, file)
            
            return results
        return wrapper
    return decorator

@process_and_save(key="Euthyphro")
def parse_euthyphro(text_content):
    
    # Define the regex pattern with a group for the dialogue and a lookahead for the next speaker
    pattern = r"^(EUTHYPHRO:.*?\n\nSOCRATES:.*?)(?=(\n\nEUTHYPHRO:|$))"
    
    # Check if the entire text matches the pattern
    if not re.fullmatch(f"({pattern})*", text_content, re.DOTALL):
        raise ValueError("The text does not alternate correctly between EUTHYPHRO and SOCRATES.")
    
    # Find all matches of the pattern in the text
    results = re.findall(pattern, text_content, re.DOTALL | re.MULTILINE)
    
    # the pattern captures the text in a tuple because we have more than 1 capture group,
    # so we need to extract the first element
    return [match[0].strip() for match in results]

@process_and_save(key="Phaedo")
def parse_phaedo(text_content):
    
    # Split the text into paragraphs
    text_content: list[str] = text_content.strip().split("\n\n")

    # Check for non-ECHECRATES-PHAEDO pairs
    for i, line in enumerate(text_content):
        if line.startswith('ECHECRATES:'):
            if not text_content[i + 1].startswith('PHAEDO:'):
                raise ValueError(f"Text at index {i} is not a ECHECRATES-PHAEDO pair. {text_content[i]}")
    
    dialogue_pairs = []
    for i, text in enumerate(text_content):
        
        # Capture the ECHECRATES-PHAEDO pairs
        if text.startswith("ECHECRATES:") and (i + 1 < len(text_content) and text_content[i + 1].startswith("PHAEDO:")):
            dialogue_pairs.append(create_dialogue_entry(text, text_content[i + 1]))
        
        elif text.startswith("PHAEDO:"):
            # this line is captured by the previous if statement, so we can skip it
            pass
        
        else:
            # If the line more than 140 characters, add it as its own entry
            if len(text) > 140:
                dialogue_pairs.append(text)
                
            # If the line is less than 140 characters, append it to the last entry
            elif len(text) < 140 and dialogue_pairs:
                dialogue_pairs[-1] += " " + text
                
            else:
                raise ValueError(f"Text at index {i} is not a ECHECRATES-PHAEDO pair. {text}")
    return dialogue_pairs

@process_and_save(key="Apology")
def parse_apology(text_content):
    text_content = text_content.strip().split("\n\n")
    # No checking needed for Apology since the whole text is iterated over and added to the dictionary, so nothing is skipped.
    return text_content

@process_and_save(key="Crito")
def parse_crito(text_content):
    # Define the regex pattern with a group for the dialogue and a lookahead for the next speaker
    pattern = r"^(SOCRATES:.*?\n\nCRITO:.*?)(?=(\n\nSOCRATES:|$))"

    # Check if the entire text matches the pattern
    if not re.fullmatch(f"({pattern})*", text_content, re.DOTALL):
        raise ValueError("The text does not alternate correctly between SOCRATES and CRITO.")

    # Find all matches of the pattern in the text
    results = re.findall(pattern, text_content, re.DOTALL | re.MULTILINE)

    # the pattern captures the text in a tuple because we have more than 1 capture group, 
    # so we need to extract the first element
    return [match[0].strip() for match in results]

# Map titles to their corresponding parsing functions
TITLE_TO_PARSER_FUNCTION_MAP = {
    "Euthyphro": parse_euthyphro,
    "Apology": parse_apology,
    "Crito": parse_crito,
    "Phaedo": parse_phaedo,
}

# Dynamically build TITLE_FUNCTION_MAP
TITLE_TO_PARSER_FUNCTION_MAP = {
    name.replace("parse_", "").capitalize(): func
    for name, func in globals().items()
    if callable(func) and name.startswith("parse_")
}