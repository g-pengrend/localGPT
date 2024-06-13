import argparse
import os
import sys
import tempfile

import requests
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(__name__)
app.secret_key = "LeafmanZSecretKey"

API_HOST = "http://localhost:5110/api"


# PAGES #
@app.route("/", methods=["GET", "POST"])
def home_page():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle AJAX request for directory tree data
        api_url = f"{API_HOST}/dirtree"
        response = requests.get(api_url)
        tree_data = response.json()
        return jsonify(tree_data)
    
    if request.headers.get('X-Requested-With') == 'createNewFolderRequest':
        new_folder = request.form.get("newFolder")
        print(f"Request form data: {new_folder}")
        if new_folder is not None:
            print(f"New folder to be created: {new_folder}")
            create_folder_url = f"{API_HOST}/create_folder/{new_folder}"
            response = requests.post(create_folder_url)
            print(response.status_code)  # Print HTTP response status code for debugging
            if response.status_code == 200:
                return jsonify({"message": f"Folder '{new_folder}' created successfully."})
            else:
                return jsonify({"message": f"Folder '{new_folder}' already exists."}), 400
        else:
            print("newFolder parameter is missing in the request.")

    if request.headers.get('X-Requested-With') == 'selectFolderRequest':
        selected_folder = request.form.get("selectedFolder")
        print(f"Selected folder received from UI: {selected_folder}")  # Debug print
        if selected_folder is not None:
            # Process the selected folder as needed
            selected_folder_url = f"{API_HOST}/choose_folder/{selected_folder}"
            response = requests.post(selected_folder_url)
            print(response.status_code)  # Print HTTP response status code for debugging
            if response.status_code == 200:
                return jsonify({"message": f"Folder '{selected_folder}' selected successfully."})
            else:
                return jsonify({"message": f"Folder '{selected_folder}' facing some issue."}), 400
        else:
            print("selected_folder parameter is missing in the request.")

    
    if request.method == "POST":
        print("POST correct")
        
        select_prompt = request.form["select_prompt"]
        print(f"Prompt Template Selected: {select_prompt}")
        if select_prompt == "QA":
        # Handle Question & Answer (Default)
            pass
        elif select_prompt == "LP":
            # Handle Lesson Plan Creation
            pass
        elif select_prompt == "MCQ":
            # Handle Multiple Choice Questions
            pass
        elif select_prompt == "SAQ":
            # Handle Short Answer Questions
            pass
        elif select_prompt == "LS":
            # Handle Labsheet Creation
            pass
        else:
            select_prompt = "QA"

        if "user_prompt" in request.form:
            user_prompt = request.form["user_prompt"]
            print(f"User Prompt: {user_prompt}")

            main_prompt_url = f"{API_HOST}/prompt_route"
            response = requests.post(main_prompt_url, data={"user_prompt": user_prompt})
            print(response.status_code)  # print HTTP response status code for debugging
            if response.status_code == 200:
                # print(response.json())  # Print the JSON data from the response
                return render_template("home.html", show_response_modal=True, response_dict=response.json())
        
        elif "documents" in request.files:
            delete_source_url = f"{API_HOST}/delete_source"  # URL of the /api/delete_source endpoint
            # Access the action and uploadPath values from the form data
            action = request.form.get("action")
            upload_path = request.form.get("uploadPath")            
            
            if action == "reset":
                response = requests.get(delete_source_url)

            if action == "add" and upload_path is not None:
                # Perform actions specific to 'add'
                save_document_url = f"{API_HOST}/save_document/{upload_path}"
                run_ingest_url = f"{API_HOST}/run_ingest/{upload_path}"  # URL of the /api/run_ingest endpoint
                files = request.files.getlist("documents")
                for file in files:
                    print(file.filename)
                    filename = secure_filename(file.filename)
                    with tempfile.SpooledTemporaryFile() as f:
                        f.write(file.read())
                        f.seek(0)
                        response = requests.post(save_document_url, files={"document": (filename, f)})
                        print(response.status_code)  # print HTTP response status code for debugging
                # Make a GET request to the /api/run_ingest endpoint
                response = requests.get(run_ingest_url)
                print(response.status_code)  # print HTTP response status code for debugging

    # Display the form for GET request
    return render_template(
        "home.html",
        show_response_modal=False,
        response_dict={"Prompt": "None", "Answer": "None", "Sources": [("ewf", "wef")]},
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5111, help="Port to run the UI on. Defaults to 5111.")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to run the UI on. Defaults to 127.0.0.1. "
        "Set to 0.0.0.0 to make the UI externally "
        "accessible from other devices.",
    )
    args = parser.parse_args()
    app.run(debug=True, host=args.host, port=args.port)
