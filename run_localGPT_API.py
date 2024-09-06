# Standard library imports
import logging
import os
import shutil
import subprocess
import argparse
import time
from threading import Lock
from typing import Tuple

# Third-party library imports
import torch
from flask import Flask, jsonify, request, Response, abort, send_file, session
from werkzeug.utils import secure_filename
from langchain.chains import RetrievalQA, LLMChain
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import Chroma

# Local application imports
from utils import (
    success,
    info,
    warning,
    error
)
from run_localGPT import load_model
from prompt_templates.prompt_template_utils import (
    get_prompt_template,
    PROMPT_TEMPLATE_MAPPING,
    LESSON_PLAN_PROMPT
)
from constants import (
    CHROMA_SETTINGS, 
    EMBEDDING_MODEL_NAME,  
    DATABASE_MAPPING,
    PERSIST_DIRECTORY,
    PERSIST_DIRECTORIES, 
    MODEL_ID, 
    MODEL_BASENAME,
    SOURCE_DIRECTORY,
)
    
app = Flask(__name__)
app.secret_key = "LeafmanZSecretKey"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_PASSWORD = "12345"

# Initialize a lock for handling API requests
request_lock = Lock()

# Determine the device type based on availability
if torch.backends.mps.is_available():
    DEVICE_TYPE: str = "mps"
elif torch.cuda.is_available():
    DEVICE_TYPE: str = "cuda"
else:
    DEVICE_TYPE: str = "cpu"

SHOW_SOURCES: bool = True

# Log the device type and source document display setting
logging.info(f"Running on: {DEVICE_TYPE}")
logging.info(f"Display Source Documents set to: {SHOW_SOURCES}")


# Initialize embeddings using HuggingFaceInstructEmbeddings
EMBEDDINGS = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs={"device": DEVICE_TYPE})

# Initialize retriever dictionary and debugging variables
RETRIEVER_DICT: dict = {}
DB_SELECTED: str = ""  # For debugging
PROMPT_TEMPLATE_SELECTED: str = ""  # For debugging

# Load the language model
LLM = load_model(device_type=DEVICE_TYPE, model_id=MODEL_ID, model_basename=MODEL_BASENAME)

# Get the prompt template and memory
prompt, memory = get_prompt_template(promptTemplate_type="mistral", history=False)

# Iterate over each directory in the database mapping
for dir_name, dir_path in DATABASE_MAPPING.items():
    # Initialize Chroma database with embeddings and settings
    DB = Chroma(persist_directory=dir_path, embedding_function=EMBEDDINGS, client_settings=CHROMA_SETTINGS)
    
    # Get the retriever from the database
    retriever = DB.as_retriever()
    
    # Store the retriever in the dictionary
    RETRIEVER_DICT[dir_name] = retriever

# Sleep for a short duration to ensure all processes are ready
time.sleep(0.2)

# Open the localhost URL in the default web browser
subprocess.run(['python', '-m', 'webbrowser', '-t', 'http://localhost:5111'])

def make_tree(path: str) -> dict:
    """
    Generate a tree structure of directories starting from the given path.

    Args:
        path (str): The root directory path to generate the tree from.

    Returns:
        dict: A dictionary representing the directory tree structure.
    """
    # Initialize the tree with the root directory name and an empty list for children
    tree = dict(name=os.path.basename(path), children=[])
    
    try:
        # List all entries in the directory
        lst = os.listdir(path)
    except OSError:
        # Ignore errors, e.g., if the directory cannot be accessed
        pass
    else:
        # Iterate over each entry in the directory
        for name in lst:
            # Construct the full path of the entry
            fn = os.path.join(path, name)
            # Check if the entry is a directory
            if os.path.isdir(fn):
                # Add the directory to the children list
                tree['children'].append(dict(name=name))
    
    return tree

# Initialize the Flask application
app = Flask(__name__)

@app.route('/api/source_dirtree', methods=["GET"])
def source_dirtree_api() -> jsonify:
    """
    Endpoint to retrieve the directory tree structure of the 'SOURCE_DOCUMENTS' folder.

    This function handles a GET request to generate and return a JSON representation
    of the directory tree structure of the 'SOURCE_DOCUMENTS' folder.

    Returns:
        jsonify: A JSON response containing the directory tree structure of the 'SOURCE_DOCUMENTS' folder.
    """
    # Construct the path to the 'SOURCE_DOCUMENTS' folder
    path: str = os.path.join(os.getcwd(), "SOURCE_DOCUMENTS")
    
    # Print the path for debugging purposes
    print(path)
    
    # Generate the directory tree structure and return it as a JSON response
    return jsonify(make_tree(path))

@app.route('/api/database_dirtree', methods=["GET"])
def database_dirtree_api() -> jsonify:
    """
    Endpoint to retrieve the directory tree structure of the 'DB' folder.

    This function handles a GET request to generate and return a JSON representation
    of the directory tree structure of the 'DB' folder.

    Returns:
        jsonify: A JSON response containing the directory tree structure of the 'DB' folder.
    """
    # Construct the path to the 'DB' folder
    path: str = os.path.join(os.getcwd(), "DB")
    
    # Print the path for debugging purposes
    print(path)
    
    # Generate the directory tree structure and return it as a JSON response
    return jsonify(make_tree(path))

@app.route("/api/delete_source", methods=["GET"])
def delete_source_route() -> jsonify:
    """
    Endpoint to delete and recreate the 'SOURCE_DOCUMENTS' and 'DB' folders.

    This function handles a GET request to delete the specified folders if they exist,
    and then recreate them. It returns a JSON response indicating the success of the operation.

    Returns:
        jsonify: A JSON response containing a message about the operation's success.
    """
    folder_names: list[str] = ["SOURCE_DOCUMENTS", "DB"]
    
    for folder_name in folder_names:
        # Check if the folder exists
        if os.path.exists(folder_name):
            # Remove the folder and all its contents
            shutil.rmtree(folder_name)
        
        # Recreate the folder
        os.makedirs(folder_name)

    # Return a JSON response indicating the folders were successfully deleted and recreated
    return jsonify({"message": f"Folders {folder_names} successfully deleted and recreated."})

@app.route("/api/save_document/<directory_name>", methods=["GET", "POST"])
def save_document_route(directory_name: str) -> tuple[str, int]:
    """
    Endpoint to save a document to a specified directory within the SOURCE_DOCUMENTS folder.

    Args:
        directory_name (str): The name of the directory where the document will be saved.

    Returns:
        tuple: A tuple containing a message and an HTTP status code.
    """
    # Check if the 'document' part is present in the request
    if "document" not in request.files:
        return "No document part", 400

    # Retrieve the file from the request
    file = request.files["document"]

    # Check if a file was selected
    if file.filename == "":
        return "No selected file", 400

    # If a file is present, proceed with saving it
    if file:
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)

        # Construct the folder path within the SOURCE_DOCUMENTS directory
        folder_path = os.path.join("SOURCE_DOCUMENTS", directory_name)

        # Check if the folder exists, if not, create it
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Construct the full file path
        file_path = os.path.join(folder_path, filename)

        # Save the file to the constructed file path
        file.save(file_path)

        # Return a success message and HTTP status code 200
        return "File saved successfully", 200
    
@app.route("/api/create_folder/<folder_name>", methods=["POST"])
def create_folder(folder_name: str) -> tuple[dict[str, str], int]:
    """
    Endpoint to create a new folder in the SOURCE_DOCUMENTS directory.

    Args:
        folder_name (str): The name of the folder to be created.

    Returns:
        tuple: A tuple containing a dictionary with a message and an HTTP status code.
    """
    # Construct the full path for the new folder
    folder_path = os.path.join("SOURCE_DOCUMENTS", folder_name)
    
    # Check if the folder already exists
    if not os.path.exists(folder_path):
        # Create the folder if it does not exist
        os.makedirs(folder_path)
        # Return a success message and HTTP status code 200
        return {"message": f"Folder '{folder_name}' created successfully."}, 200
    else:
        # Return an error message and HTTP status code 400 if the folder already exists
        return {"message": f"Folder '{folder_name}' already exists."}, 400

@app.route("/api/choose_prompt_template/<selected_prompt_template>", methods=["POST"])
def chosen_prompt_template(selected_prompt_template: str) -> str:
    """
    Endpoint to choose a prompt template and set it as the selected template.

    Args:
        selected_prompt_template (str): The name of the prompt template to be selected.

    Returns:
        str: The name of the selected prompt template.
    """
    # Log the received prompt template for debugging purposes
    info(message=f"Received selected_prompt_template: {selected_prompt_template}")

    # Declare the global variable to store the selected prompt template
    global PROMPT_TEMPLATE_SELECTED

    # Check if the selected prompt template exists in the mapping
    if selected_prompt_template in PROMPT_TEMPLATE_MAPPING:
        # Update the global variable with the selected prompt template
        PROMPT_TEMPLATE_SELECTED = selected_prompt_template
        # Log a success message indicating the selected prompt template
        success(message=f"PROMPT_TEMPLATE_SELECTED updated to: {PROMPT_TEMPLATE_SELECTED}")
    else:
        # If the selected prompt template does not exist, set the global variable to "No Prompt"
        PROMPT_TEMPLATE_SELECTED = "No Prompt"
        # Log a warning message indicating that the selected prompt template does not exist
        warning(message=f"Prompt template '{selected_prompt_template}' does not exist. PROMPT_TEMPLATE_SELECTED set to No Prompt.")

    # Return the name of the selected prompt template
    return PROMPT_TEMPLATE_SELECTED

@app.route("/api/choose_folder/<selected_folder>", methods=["POST"])
def chosen_folder(selected_folder: str) -> str:
    """
    Endpoint to choose a folder and set it as the selected database.

    Args:
        selected_folder (str): The name of the folder to be selected as the database.

    Returns:
        str: The name of the selected database.
    """
    global DB_SELECTED

    # Check if a folder name is provided
    if selected_folder:
        # Set the global variable DB_SELECTED to the provided folder name
        DB_SELECTED = selected_folder
        # Log a success message indicating the selected database
        success(message=f"Selected Database: {DB_SELECTED}")
    else:
        # If no folder name is provided, set DB_SELECTED to an empty string
        DB_SELECTED = ""
        # Log a warning message indicating that no database was selected
        warning(message="Selected Database: None")

    # Return the name of the selected database
    return DB_SELECTED

@app.route("/api/run_ingest/<directory_name>", methods=["GET"])
def run_ingest_route(directory_name: str) -> Tuple[str, int]:
    """
    Endpoint to run the ingestion process for a specified directory.

    Args:
        directory_name (str): The name of the directory to ingest.

    Returns:
        Tuple[str, int]: A message indicating the result of the operation and the HTTP status code.
    """
    global RETRIEVER_DICT

    info(message=f"Device currently in use: {DEVICE_TYPE.upper()}")

    try:
        # Construct the path to the directory where data will be persisted
        persist_directory_path = os.path.join(PERSIST_DIRECTORY, directory_name)
        
        # Check if the directory exists and remove it if it does
        if os.path.exists(persist_directory_path):
            try:
                shutil.rmtree(persist_directory_path)
            except OSError as e:
                print(f"Error: {e.filename} - {e.strerror}.")
        else:
            warning(message="The directory does not exist")

        # Prepare the command to run the ingestion script
        run_ingest_commands = ["python", "ingest.py"]
        
        # Add device type to the command if specified
        if DEVICE_TYPE == "cpu":
            run_ingest_commands.append("--device_type")
            run_ingest_commands.append(DEVICE_TYPE)
        
        # Add directory paths to the command if directory_name is provided
        if directory_name is not None:
            run_ingest_commands.append("--select_directory")
            run_ingest_commands.append(os.path.join(SOURCE_DIRECTORY, directory_name))
            run_ingest_commands.append("--db_directory")
            run_ingest_commands.append(os.path.join(PERSIST_DIRECTORY, directory_name))

        # Execute the ingestion script
        result = subprocess.run(run_ingest_commands, capture_output=True)
        
        # Check if the script execution was successful
        if result.returncode != 0:
            return "Script execution failed: {}".format(result.stderr.decode("utf-8")), 500
        
        # Load the vector store
        DB = Chroma(
            persist_directory=persist_directory_path,
            embedding_function=EMBEDDINGS,
            client_settings=CHROMA_SETTINGS,
        )
        retriever = DB.as_retriever()

        # Store the retriever in the global dictionary
        RETRIEVER_DICT[directory_name] = retriever

        success(message=f"Script executed successfully: {result.stdout.decode('utf-8')}")

        return "Script executed successfully: {}".format(result.stdout.decode("utf-8")), 200
    except Exception as e:
        return f"Error occurred: {str(e)}", 500

@app.route("/api/prompt_route", methods=["GET", "POST"])
def prompt_route() -> Tuple[Response, int]:
    """
    Handle the prompt route for processing user prompts.

    Returns:
        Tuple[Response, int]: JSON response containing the prompt, answer, and sources (if any), along with the HTTP status code.
    """
    global request_lock  # Make sure to use the global lock instance
    global OUT_DIR

    # Retrieve the user prompt from the form data
    user_prompt: str = request.form.get("user_prompt")

    # Modify the user prompt if the selected template is "Lesson Plan"
    if PROMPT_TEMPLATE_SELECTED == "Lesson Plan":
        user_prompt = f'Create a lesson plan on the following topic: {user_prompt}. Ensure that there are at least 2 activities per section. Be verbose on the content and provide examples.'

    # Modify the user prompt if the selected template is "Multiple Choice Question"
    if PROMPT_TEMPLATE_SELECTED == "Multiple Choice Question":
        # subprocess.run(["export", "TOKENIZERS_PARALLELISM=false"])
        user_prompt = f'Create 3 multiple choice questions, 1 per taxonomy level, on the following topic: {user_prompt}. There is strictly only one correct answer per question.'

    # Modify the user prompt if the selected template is "Content Generation"
    if PROMPT_TEMPLATE_SELECTED == "Content Generation":
        user_prompt = f"""Write an in-depth article of at least 5,000 words on the topic of {user_prompt}, providing a comprehensive analysis that covers the background and history, current trends, key players, challenges, and future prospects. Begin with a compelling introduction that explains the relevance and importance of the topic. Delve into its origins and development, highlighting key milestones and influential figures with specific examples. Analyze the current state of the topic, discussing significant trends, technological advancements, and recent changes, supported by relevant data and case studies. Explore the roles of major contributors, organizations, or entities, illustrating their impact with real-world examples. Address the challenges, controversies, and debates surrounding the topic, elaborating on different perspectives. Conclude with a forward-looking analysis of potential future trends, innovations, and emerging ideas, providing concrete examples where possible. Throughout, ensure that each section is detailed, well-supported by examples, and written in an engaging, informative tone for a well-read audience.

Format the article in Markdown using the following structure:

Title: Use a level 1 header (#) for the title.
Introduction: Start with a level 2 header (## Introduction) and write an engaging overview.
Sections: Each major section should begin with a level 2 header (e.g., ## Background and History), with sub-sections under level 3 headers (e.g., ### Key Milestones).
Bullet Points: Use bullet points (-) or numbered lists (1., 2., etc.) where appropriate to break down complex information.
Blockquotes: Use blockquotes (>) to highlight significant quotes or key insights.
Bold/Italics: Use bold (**bold**) and italics (*italics*) for emphasis as needed.
Code Blocks: If applicable, include code snippets or data in fenced code blocks (```).
Links and References: Use markdown for hyperlinks ([text](url)) and cite any sources or references appropriately.
Images: If including images, use the markdown syntax for embedding images (![alt text](image_url)).

Ensure the article is meticulously organized, flows logically from one section to the next, and is fully elaborated with examples, data, and expert opinions where relevant."""

    # Return an error response if no user prompt is received
    if not user_prompt:
        return "No user prompt received", 400

    info(message="*****************Processing prompt*****************")
    info(message=f"The selected folder is {DB_SELECTED}")
    info(message=f"The selected output is {PROMPT_TEMPLATE_SELECTED}")

    with request_lock:
        # Case 1: Both a database and a prompt template are selected
        if DB_SELECTED and PROMPT_TEMPLATE_SELECTED:
            info(message="*****************Using LLM with both RAG/OutputType*****************")
            prompt, memory = get_prompt_template(system_prompt=PROMPT_TEMPLATE_MAPPING[PROMPT_TEMPLATE_SELECTED], promptTemplate_type="mistral", history=False)
            QA = RetrievalQA.from_chain_type(
                llm=LLM,
                chain_type="stuff",
                retriever=RETRIEVER_DICT[DB_SELECTED],
                return_source_documents=SHOW_SOURCES,
                chain_type_kwargs={"prompt": prompt},
            )
            res = QA(user_prompt)
            answer, docs = res["result"], res["source_documents"]
        # Case 2: Only a database is selected
        elif DB_SELECTED:
            warning(message="*****************Using LLM with RAG without OutputType*****************")
            prompt, memory = get_prompt_template(promptTemplate_type="mistral", history=False)
            QA = RetrievalQA.from_chain_type(
                llm=LLM,
                chain_type="stuff",
                retriever=RETRIEVER_DICT[DB_SELECTED],
                return_source_documents=SHOW_SOURCES,
                chain_type_kwargs={"prompt": prompt},
            )
            res = QA(user_prompt)
            answer, docs = res["result"], res["source_documents"]
        # Case 3: Only a prompt template is selected
        elif PROMPT_TEMPLATE_SELECTED:
            warning(message="*****************Using LLM with OutputType without RAG*****************")
            prompt = PROMPT_TEMPLATE_MAPPING[PROMPT_TEMPLATE_SELECTED]
            answer = LLM(prompt + user_prompt)
            docs = []
        # Case 4: Neither a database nor a prompt template is selected
        else:
            warning(message="*****************Using base LLM without both RAG/OutputType*****************")
            answer = LLM(user_prompt)
            docs = []

        # Construct the response dictionary
        prompt_response_dict: Dict[str, Any] = {
            "Prompt": user_prompt,
            "Answer": answer,
        }

        # Include source documents in the response if available
        # if docs:
        #     prompt_response_dict["Sources"] = [
        #         (os.path.basename(str(document.metadata["source"])), str(document.page_content))
        #         for document in docs
        #     ]

        OUT_DIR = None
        # Run additional scripts based on the selected prompt template
        if PROMPT_TEMPLATE_SELECTED == "Lesson Plan":
            subprocess.run(["python", "./extensions/lesson_plan/run_llm_to_xml.py", answer])
            OUT_DIR = "./extensions/lesson_plan/outputs"
        elif PROMPT_TEMPLATE_SELECTED == "Multiple Choice Question":
            subprocess.run(["python", "./extensions/mcq/convert.py", answer])
            OUT_DIR = "./extensions/mcq/outputs"
        elif PROMPT_TEMPLATE_SELECTED == "Content Generation":
            if docs:
                prompt_response_dict["Sources"] = [
                    (os.path.basename(str(document.metadata["source"])), str(document.page_content))
                    for document in docs
                ]
                sources_string = "\n".join([
                    f"{os.path.basename(str(document.metadata['source']))}: {str(document.page_content).encode('ascii', 'xmlcharrefreplace').decode()}"
                    for document in docs
                ]).encode('ascii', 'ignore').decode()
                print(sources_string)
            subprocess.run(["python", "./extensions/content_generation/convert.py", answer, sources_string])
            OUT_DIR = "./extensions/content_generation/outputs"
        # Return the JSON response along with the HTTP status code
        return jsonify(prompt_response_dict), 200

# Password verification endpoint
@app.route("/api/verify_password/<filename>", methods=["POST"])
def verify_password(filename):
    entered_password = request.form.get("password")

    if entered_password == DOWNLOAD_PASSWORD:
        # If the password is correct, store that in the session
        session['authenticated'] = True
        return jsonify({"message": "Password correct, you can now download the file."})
    else:
        # Return an error message if the password is wrong
        return jsonify({"error": "Invalid password"}), 401

# File download endpoint
@app.route("/api/download/<filename>", methods=["GET"])
def download_file(filename):
    global OUT_DIR

    if not OUT_DIR:
        return jsonify({"error": "Output directory not found"}), 400
    
    # Log the filename and session info
    print(f"Attempting to download file: {filename}")
    # info(message=f"Session authenticated: {session.get('authenticated')}")

    # DISABLE FIRST
    # Check if the user is authenticated
    # if not session.get('authenticated'):
    #     return jsonify({"error": "You are not authorized to download this file"}), 403

    # Securely serve the file using send_file
    OUT_PATH = os.path.join(BASE_DIR, OUT_DIR)
    DL_FILE_PATH = os.path.join(OUT_PATH, filename)
    # rel_path = f"./extensions/lesson_plan/outputs/{filename}"  # Make sure this path is correct
    # file_path = os.path.join(BASE_DIR, rel_path)
    print(f"Looking for file at: {DL_FILE_PATH}")
    # Check if the file exists
    if os.path.exists(DL_FILE_PATH):
        return send_file(DL_FILE_PATH, as_attachment=True)
    else:
        print(f"File not found: {DL_FILE_PATH}")
        return abort(404)  # Return 404 if file not found

#DEBUGGER
@app.route("/api/get_current_state", methods=["GET"])
def get_current_state() -> jsonify:
    """
    Endpoint to get the current state of the selected database and prompt template,
    as well as check the existence of the generated file.

    Optionally, accepts a 'filename' query parameter to check for the file existence.

    Returns:
        jsonify: A JSON object containing the current state of the selected database,
        prompt template, and file existence.
    """
    global DB_SELECTED, PROMPT_TEMPLATE_SELECTED

    # Create a dictionary to hold the current state
    current_state = {
        "DEBUGGING: DB_SELECTED": DB_SELECTED,
        "DEBUGGING: PROMPT_TEMPLATE_SELECTED": PROMPT_TEMPLATE_SELECTED,
    }

    # Print the current state for debugging purposes
    print(f"Current state: {current_state}")  # Debug print

    # Return the current state as a JSON response
    return jsonify(current_state)

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Run the local GPT API.")
    parser.add_argument(
        "--port", 
        type=int, 
        default=5110, 
        help="Port to run the API on. Defaults to 5110."
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help=(
            "Host to run the UI on. Defaults to 127.0.0.1. "
            "Set to 0.0.0.0 to make the UI externally "
            "accessible from other devices."
        ),
    )
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()

    # Uncomment the following lines to enable logging
    # logging.basicConfig(
    #     format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", 
    #     level=logging.INFO
    # )

    # Run the Flask application
    app.run(debug=False, host=args.host, port=args.port)
