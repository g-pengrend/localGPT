import re
import sys
import colorama

def success(message: str) -> None:
    print(colorama.Back.GREEN + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)
    return None

def info(message: str) -> None:
    print(colorama.Back.CYAN + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)
    return None

def warning(message: str) -> None:
    print(colorama.Back.YELLOW + colorama.Fore.BLACK + message + colorama.Style.RESET_ALL)
    return None

def error(message: str) -> None:
    print(colorama.Back.RED + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)
    sys.exit(1)
    return None

def clean_json_string(llm_output):
    """
    Extract and clean a JSON string from a given input string.

    Parameters:
    llm_output (str): The input string containing JSON content.

    Returns:
    str: The cleaned and corrected JSON string.
    """
    # Extract JSON content from the input string
    json_start = llm_output.find('{')
    json_end = llm_output.rfind('}')
    if json_start == -1 or json_end == -1:
        raise ValueError("No valid JSON object found in the input string.")
    
    json_string = llm_output[json_start:json_end + 1]

    # Replace problematic characters or sequences
    json_string = re.sub(r'\n|\s+', ' ', json_string)  # Replace newlines and multiple spaces with a single space
    json_string = re.sub(r',\s*([}\]])', r'\1', json_string)  # Remove trailing commas before closing braces/brackets
    json_string = re.sub(r'\\', r'\\\\', json_string)  # Escape backslashes
    json_string = re.sub(r'(?<!\\)"', r'\\"', json_string)  # Escape unescaped double quotes
    json_string = re.sub(r'\\"(.*?)\\"', r'"\1"', json_string)  # Unescape double quotes within strings

    # Fix missing commas between key-value pairs
    json_string = re.sub(r'(?<=\})(\s*)(?=\{)', r'\1, ', json_string)  # Add comma between objects in an array
    json_string = re.sub(r'(?<=\])(\s*)(?=\[)', r'\1, ', json_string)  # Add comma between arrays in an array
    json_string = re.sub(r'(?<=\d)(\s*)(?=\{)', r'\1, ', json_string)  # Add comma between numbers and objects
    json_string = re.sub(r'(?<=\])(\s*)(?=\{)', r'\1, ', json_string)  # Add comma between closing bracket and opening brace

    # Correct the JSON formatting
    json_string = json_string.replace('\\"', '"')  # Revert escaped quotes to normal quotes

    return json_string