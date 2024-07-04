import sys
import os
import csv
import colorama
from datetime import datetime
from constants import EMBEDDING_MODEL_NAME
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from typing import Union


def success(message: str) -> None:
    """
    Display a success message in the console with a green background and white text.

    Args:
        message (str): The success message to be displayed.

    Returns:
        None
    """
    # Print the message with colorama styling for success
    print(colorama.Back.GREEN + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)
    
    # Explicitly return None (though it's not necessary as Python functions return None by default)
    return None

def info(message: str) -> None:
    """
    Display an informational message in the console with a cyan background and white text.

    Args:
        message (str): The informational message to be displayed.

    Returns:
        None
    """
    # Print the message with colorama styling for informational messages
    print(colorama.Back.CYAN + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)
    
    # Explicitly return None (though it's not necessary as Python functions return None by default)
    return None

def warning(message: str) -> None:
    """
    Display a warning message in the console with a yellow background and black text.

    Args:
        message (str): The warning message to be displayed.

    Returns:
        None
    """
    # Print the message with colorama styling for warning messages
    print(colorama.Back.YELLOW + colorama.Fore.BLACK + message + colorama.Style.RESET_ALL)
    
    # Explicitly return None (though it's not necessary as Python functions return None by default)
    return None

def error(message: str) -> None:
    """
    Display an error message in the console with a red background and white text, then exit the program.

    Args:
        message (str): The error message to be displayed.

    Returns:
        None
    """
    # Print the message with colorama styling for error messages
    print(colorama.Back.RED + colorama.Fore.WHITE + message + colorama.Style.RESET_ALL)
    
    # Exit the program with a status code of 1 indicating an error
    sys.exit(1)
    
    # Explicitly return None (though it's not necessary as Python functions return None by default)
    return None

def log_to_csv(question: str, answer: str) -> None:
    """
    Log a question and its corresponding answer to a CSV file with a timestamp.

    This function ensures that the log directory and file exist, creates them if necessary,
    and appends the question and answer along with the current timestamp to the CSV file.

    Args:
        question (str): The question to be logged.
        answer (str): The answer to be logged.

    Returns:
        None
    """
    
    log_dir, log_file = "local_chat_history", "qa_log.csv"
    
    # Ensure log directory exists, create if not
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Construct the full file path
    log_path = os.path.join(log_dir, log_file)

    # Check if file exists, if not create and write headers
    if not os.path.isfile(log_path):
        with open(log_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(["timestamp", "question", "answer"])

    # Append the log entry
    with open(log_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Get the current timestamp in the format YYYY-MM-DD HH:MM:SS
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Write the timestamp, question, and answer to the CSV file
        writer.writerow([timestamp, question, answer])


def get_embeddings(device_type: str = "cuda") -> Union[HuggingFaceInstructEmbeddings, HuggingFaceBgeEmbeddings, HuggingFaceEmbeddings]:
    """
    Get the appropriate embedding model based on the global EMBEDDING_MODEL_NAME.

    This function returns an instance of a HuggingFace embedding model based on the 
    specified EMBEDDING_MODEL_NAME. It supports different types of embedding models 
    such as 'instructor', 'bge', and others.

    Args:
        device_type (str): The type of device to use for the model (e.g., "cuda" for GPU, "cpu" for CPU).
                           Default is "cuda".

    Returns:
        Union[HuggingFaceInstructEmbeddings, HuggingFaceBgeEmbeddings, HuggingFaceEmbeddings]: 
        An instance of the appropriate HuggingFace embedding model.
    """
    
    # Check if the embedding model name contains "instructor"
    if "instructor" in EMBEDDING_MODEL_NAME:
        # Return an instance of HuggingFaceInstructEmbeddings with specific instructions
        return HuggingFaceInstructEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": device_type},
            embed_instruction="Represent the document for retrieval:",
            query_instruction="Represent the question for retrieving supporting documents:",
        )

    # Check if the embedding model name contains "bge"
    elif "bge" in EMBEDDING_MODEL_NAME:
        # Return an instance of HuggingFaceBgeEmbeddings with a specific query instruction
        return HuggingFaceBgeEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": device_type},
            query_instruction="Represent this sentence for searching relevant passages:",
        )

    # For all other cases, return a general HuggingFaceEmbeddings instance
    else:
        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": device_type},
        )