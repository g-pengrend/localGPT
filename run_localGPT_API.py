import logging
import os
import shutil
import subprocess
import argparse
import time

import torch
from flask import Flask, jsonify, request
from langchain.chains import RetrievalQA, LLMChain
from langchain.embeddings import HuggingFaceInstructEmbeddings

# from langchain.embeddings import HuggingFaceEmbeddings
from run_localGPT import load_model
from prompt_templates.prompt_template_utils import (
    get_prompt_template,
    PROMPT_TEMPLATE_MAPPING,
    LESSON_PLAN_PROMPT
)

# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import Chroma
from werkzeug.utils import secure_filename

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



# API queue addition
from threading import Lock

request_lock = Lock()


if torch.backends.mps.is_available():
    DEVICE_TYPE = "mps"
elif torch.cuda.is_available():
    DEVICE_TYPE = "cuda"
else:
    DEVICE_TYPE = "cpu"

SHOW_SOURCES = True
logging.info(f"Running on: {DEVICE_TYPE}")
logging.info(f"Display Source Documents set to: {SHOW_SOURCES}")

EMBEDDINGS = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs={"device": DEVICE_TYPE})

# uncomment the following line if you used HuggingFaceEmbeddings in the ingest.py
# EMBEDDINGS = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
# if os.path.exists(PERSIST_DIRECTORY):
#     try:
#         shutil.rmtree(PERSIST_DIRECTORY)
#     except OSError as e:
#         print(f"Error: {e.filename} - {e.strerror}.")
# else:
#     print("The directory does not exist")

# run_langest_commands = ["python", "ingest.py"]
# if DEVICE_TYPE == "cpu":
#     run_langest_commands.append("--device_type")
#     run_langest_commands.append(DEVICE_TYPE)

# result = subprocess.run(run_langest_commands, capture_output=True)
# if result.returncode != 0:
#     raise FileNotFoundError(
#         "No files were found inside SOURCE_DOCUMENTS, please put a starter file inside before starting the API!"
#     )

RETRIEVER_DICT = {}
DB_SELECTED = "" # For debugging
PROMPT_TEMPLATE_SELECTED = "" # For debugging

LLM = load_model(device_type=DEVICE_TYPE, model_id=MODEL_ID, model_basename=MODEL_BASENAME)
prompt, memory = get_prompt_template(promptTemplate_type="mistral", history=False)

for dir_name, dir_path in DATABASE_MAPPING.items():
    DB = Chroma(persist_directory=dir_path, embedding_function=EMBEDDINGS, client_settings=CHROMA_SETTINGS)
    retriever = DB.as_retriever()
    RETRIEVER_DICT[dir_name] = retriever

    # QA = RetrievalQA.from_chain_type(
    #     llm=LLM,
    #     chain_type="stuff",
    #     retriever=RETRIEVER,
    #     return_source_documents=SHOW_SOURCES,
    #     chain_type_kwargs={
    #         "prompt": prompt,
    #     },
    # )

time.sleep(0.2)
# Open localhost URL
subprocess.run(['python', '-m', 'webbrowser', '-t', 'http://localhost:5111'])

def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try:
        lst = os.listdir(path)
    except OSError:
        pass  # Ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(dict(name=name))
    return tree

app = Flask(__name__)

@app.route('/api/dirtree')
def dirtree_api():
    path = os.path.join(os.getcwd(), "SOURCE_DOCUMENTS")
    return jsonify(make_tree(path))

@app.route("/api/delete_source", methods=["GET"])
def delete_source_route():
    folder_name = "SOURCE_DOCUMENTS"

    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)

    os.makedirs(folder_name)

    return jsonify({"message": f"Folder '{folder_name}' successfully deleted and recreated."})

@app.route("/api/save_document/<directory_name>", methods=["GET", "POST"])
def save_document_route(directory_name):
    if "document" not in request.files:
        return "No document part", 400
    file = request.files["document"]
    if file.filename == "":
        return "No selected file", 400
    if file:
        filename = secure_filename(file.filename)
        folder_path = os.path.join("SOURCE_DOCUMENTS", directory_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, filename)
        file.save(file_path)
        return "File saved successfully", 200
    
@app.route("/api/create_folder/<folder_name>", methods=["POST"])
def create_folder(folder_name):
    folder_path = os.path.join("SOURCE_DOCUMENTS", folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return {"message": f"Folder '{folder_name}' created successfully."}, 200
    else:
        return {"message": f"Folder '{folder_name}' already exists."}, 400

@app.route("/api/choose_prompt_template/<selected_prompt_template>", methods=["POST"])
def chosen_prompt_template(selected_prompt_template):
    print(f"Received selected_prompt_template: {selected_prompt_template}")  # Debug print
    global PROMPT_TEMPLATE_SELECTED
    if selected_prompt_template:
        PROMPT_TEMPLATE_SELECTED = selected_prompt_template
        print(f"PROMPT_TEMPLATE_SELECTED updated to: {PROMPT_TEMPLATE_SELECTED}")  # Debug print
    else:
        PROMPT_TEMPLATE_SELECTED = ""
        print(f"PROMPT_TEMPLATE_SELECTED set to None")
    return PROMPT_TEMPLATE_SELECTED

@app.route("/api/choose_folder/<selected_folder>", methods=["POST"])
def chosen_folder(selected_folder):
    global DB_SELECTED
    if selected_folder:
        DB_SELECTED = selected_folder
        print(f"Selected Database: {DB_SELECTED}")
    else:
        DB_SELECTED = ""
        print(f"Selected Database: None")
    return DB_SELECTED

@app.route("/api/get_current_state", methods=["GET"])
def get_current_state():
    global DB_SELECTED, PROMPT_TEMPLATE_SELECTED
    current_state = {
        "DEBUGGING: DB_SELECTED": DB_SELECTED,
        "DEBUGGING: PROMPT_TEMPLATE_SELECTED": PROMPT_TEMPLATE_SELECTED
    }
    print(f"Current state: {current_state}")  # Debug print
    return jsonify(current_state)

@app.route("/api/run_ingest/<directory_name>", methods=["GET"])
def run_ingest_route(directory_name):
    global RETRIEVER_DICT
    try:
        persist_directory_path = os.path.join(PERSIST_DIRECTORY, directory_name)
        if os.path.exists(persist_directory_path):
            try:
                shutil.rmtree(persist_directory_path)
            except OSError as e:
                print(f"Error: {e.filename} - {e.strerror}.")
        else:
            print("The directory does not exist")

        run_langest_commands = ["python", "ingest.py"]
        if DEVICE_TYPE == "cpu":
            run_langest_commands.append("--device_type")
            run_langest_commands.append(DEVICE_TYPE)
        if directory_name is not None:
            run_langest_commands.append("--select_directory")
            run_langest_commands.append(os.path.join(SOURCE_DIRECTORY, directory_name))
            run_langest_commands.append("--db_directory")
            run_langest_commands.append(os.path.join(PERSIST_DIRECTORY, directory_name))

        result = subprocess.run(run_langest_commands, capture_output=True)
        if result.returncode != 0:
            return "Script execution failed: {}".format(result.stderr.decode("utf-8")), 500
        # load the vectorstore
        DB = Chroma(
            persist_directory=persist_directory_path,
            embedding_function=EMBEDDINGS,
            client_settings=CHROMA_SETTINGS,
        )
        retriever = DB.as_retriever()

        RETRIEVER_DICT[persist_directory_path] = retriever

        # prompt, memory = get_prompt_template(promptTemplate_type="mistral", history=False)

        # QA = RetrievalQA.from_chain_type(
        #     llm=LLM,
        #     chain_type="stuff",
        #     retriever=RETRIEVER,
        #     return_source_documents=SHOW_SOURCES,
        #     chain_type_kwargs={
        #         "prompt": prompt,
        #     },
        # )

        return "Script executed successfully: {}".format(result.stdout.decode("utf-8")), 200
    except Exception as e:
        return f"Error occurred: {str(e)}", 500

@app.route("/api/prompt_route", methods=["GET", "POST"])
def prompt_route():
    global request_lock  # Make sure to use the global lock instance

    user_prompt = request.form.get("user_prompt")

    if user_prompt and DB_SELECTED == "" and PROMPT_TEMPLATE_SELECTED == "":
        ### History is not coded in this case ###

        # Acquire the lock before processing the prompt
        print("*****************Using base LLM without both RAG/OutputType*****************")
        print("The selected folder is", DB_SELECTED)
        print("The selected output is", PROMPT_TEMPLATE_SELECTED)
        with request_lock:

            answer = LLM(user_prompt)
            prompt_response_dict = {
                "Prompt": user_prompt,
                "Answer": answer,
            }

            return jsonify(prompt_response_dict), 200

    elif user_prompt and DB_SELECTED and PROMPT_TEMPLATE_SELECTED == "":
        # Acquire the lock before processing the prompt
        print("*****************Using LLM with RAG without OutputType*****************")
        print("The selected folder is", DB_SELECTED)
        print("The selected output is", PROMPT_TEMPLATE_SELECTED)   
        with request_lock:

            prompt, memory = get_prompt_template(promptTemplate_type="mistral", history=False)    
            QA = RetrievalQA.from_chain_type(
                llm=LLM,
                chain_type="stuff",
                retriever=RETRIEVER_DICT[DB_SELECTED],
                return_source_documents=SHOW_SOURCES,
                chain_type_kwargs={
                    "prompt": prompt,
                },
            )           
            # Get the answer from the chain
            res = QA(user_prompt)
            answer, docs = res["result"], res["source_documents"]

            prompt_response_dict = {
                "Prompt": user_prompt,
                "Answer": answer,
            }

            prompt_response_dict["Sources"] = []
            for document in docs:
                prompt_response_dict["Sources"].append(
                    (os.path.basename(str(document.metadata["source"])), str(document.page_content))
                )

    elif user_prompt and DB_SELECTED == "" and PROMPT_TEMPLATE_SELECTED:
        ### History is not coded in this case ###

        # Acquire the lock before processing the prompt
        print("*****************Using LLM with OutputType without RAG*****************")
        print("The selected folder is", DB_SELECTED)
        print("The selected output is", PROMPT_TEMPLATE_SELECTED)   
        with request_lock:

            prompt = PROMPT_TEMPLATE_MAPPING[PROMPT_TEMPLATE_SELECTED]
            # Get the answer from the chain
            answer = LLM(prompt + user_prompt)

            prompt_response_dict = {
                "Prompt": user_prompt,
                "Answer": answer,
            }
            
            # Code to output XML document in ACTEP CED Lesson Plan format.
            if PROMPT_TEMPLATE_SELECTED == "Lesson Plan": 
                os.chdir("C:/Users/Brandon/Desktop/Projects/ELITE_lessonPlans")
                subprocess.run(["python", "./run_llm_to_xml.py", answer])

        return jsonify(prompt_response_dict), 200

    elif user_prompt and DB_SELECTED and PROMPT_TEMPLATE_SELECTED:
        # Acquire the lock before processing the prompt
        print("*****************Using LLM with both RAG/OutputType*****************")
        print("The selected folder is", DB_SELECTED)
        print("The selected output is", PROMPT_TEMPLATE_SELECTED)   
        with request_lock:

            prompt, memory = get_prompt_template(system_prompt=PROMPT_TEMPLATE_MAPPING[PROMPT_TEMPLATE_SELECTED] ,promptTemplate_type="mistral", history=False)    
            QA = RetrievalQA.from_chain_type(
                llm=LLM,
                chain_type="stuff",
                retriever=RETRIEVER_DICT[DB_SELECTED],
                return_source_documents=SHOW_SOURCES,
                chain_type_kwargs={
                    "prompt": prompt,
                },
            )           
            # Get the answer from the chain
            res = QA(user_prompt)
            answer, docs = res["result"], res["source_documents"]

            prompt_response_dict = {
                "Prompt": user_prompt,
                "Answer": answer,
            }
            # Code to output XML document in ACTEP CED Lesson Plan format.
            if PROMPT_TEMPLATE_SELECTED == "Lesson Plan": 
                os.chdir("C:/Users/Brandon/Desktop/Projects/ELITE_lessonPlans")
                subprocess.run(["python", "./run_llm_to_xml.py", answer])

        return jsonify(prompt_response_dict), 200
    else:
        return "No user prompt received", 400


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5110, help="Port to run the API on. Defaults to 5110.")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to run the UI on. Defaults to 127.0.0.1. "
        "Set to 0.0.0.0 to make the UI externally "
        "accessible from other devices.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
    app.run(debug=False, host=args.host, port=args.port)
