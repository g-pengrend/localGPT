import colorama

def error(message: str):
    print(f"{colorama.Fore.RED}{message}{colorama.Style.RESET_ALL}")

def clean_json_string(answer: str) -> str:
    """
    Extract and clean a JSON string from a given input string.

    Parameters:
    answer (str): The input string containing JSON content.

    Returns:
    str: The cleaned and corrected JSON string.
    """
    # Extract JSON content from the input string
    json_start = answer.find('{')
    json_end = answer.rfind('}')
    if json_start == -1 or json_end == -1:
        raise ValueError("No valid JSON object found in the input string.")
    
    json_string = answer[json_start:json_end + 1]

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
