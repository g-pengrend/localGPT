import argparse
import os
import sys
import tempfile
import time
import io
# import json # to debug
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import requests
from flask import Flask, render_template, request, jsonify, session, g, Response
from werkzeug.utils import secure_filename
from extensions.lesson_plan.utils import recreate_docx

app = Flask(__name__)
app.secret_key = "LeafmanZSecretKey"

API_HOST = "http://localhost:5110/api"

def get_latest_file(directory):
    try:
        # Walk through all directories and subdirectories
        docx_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".docx"):  # Only consider .docx files
                    full_path = os.path.join(root, file)
                    docx_files.append(full_path)
        
        if not docx_files:
            return None  # No .docx files found

        # Get the most recently modified .docx file
        latest_file = max(docx_files, key=os.path.getmtime)
        return latest_file
    except ValueError:
        return None  # Handle the case where no files are found
    
# Initialize selected_folder and selected_prompt_template
@app.before_request
def load_selected_values():
    g.selected_folder = session.get('selected_folder', '')
    g.selected_prompt_template = session.get('selected_prompt_template', '')

# Proxy API requests from UI to API on localhost:5110
@app.route("/api/download/<filename>", methods=["GET"])
def proxy_download(filename):
    api_url = f"{API_HOST}/download/{filename}"
    
    # Forward the request to the API
    response = requests.get(api_url, stream=True)

    # Return the response from the API to the user
    if response.status_code == 200:
        return Response(response.content, headers=dict(response.headers))
    else:
        return Response(response.content, status=response.status_code)
    
# PAGES #
@app.route("/", methods=["GET", "POST"])
def home_page():
    global selected_folder, selected_prompt_template
    
    if request.method == "GET":
        print("GET correct")

        if request.headers.get('X-Requested-With') == 'fetchSourceDocDirectoryTree':
            # Handle AJAX request for directory tree data
            api_url = f"{API_HOST}/source_dirtree"
            response = requests.get(api_url)
            tree_data = response.json()
            # print(json.dumps(tree_data, indent=2)) # debugging output
            return jsonify(tree_data)
        
        if request.headers.get('X-Requested-With') == 'fetchDatabaseDirectoryTree':
            # Handle AJAX request for directory tree data
            api_url = f"{API_HOST}/database_dirtree"
            response = requests.get(api_url)
            tree_data = response.json()
            # print(json.dumps(tree_data, indent=2)) # debugging output
            return jsonify(tree_data)
    
    if request.method == "POST":
        print("POST correct")
        # Prompt Template (output) selection code
        if request.headers.get('X-Requested-With') == 'promptTemplateRequest':
            selected_prompt_template = request.form.get("selectedPrompt")
            print(f"Selected Prompt Template received from UI: {selected_prompt_template}")  # Debug print
            if selected_prompt_template:
                g.selected_prompt_template = selected_prompt_template
                # Store the selected folder in session
                session['selected_prompt_template'] = selected_prompt_template
                # Process the selected prompt template as needed
                selected_prompt_template_url = f"{API_HOST}/choose_prompt_template/{selected_prompt_template}"
                response = requests.post(selected_prompt_template_url)
                print(response.status_code)  # Print HTTP response status code for debugging
                if response.status_code == 200:
                    return jsonify({"message": f"Prompt Template '{selected_prompt_template}' selected successfully."})
                else:
                    return jsonify({"message": f"Prompt Template '{selected_prompt_template}' facing some issue."}), 400
            else:
                selected_prompt_template = "Question Answer"
                print("Empty selection found for selected_prompt_template - Using default.")

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

        # DB selection code
        if request.headers.get('X-Requested-With') == 'selectDBRequest':
            selected_folder = request.form.get("selectedFolder")
            print(f"Selected database received from UI: {selected_folder}")  # Debug print
            if selected_folder:
                g.selected_folder = selected_folder
                # Store the selected folder in session
                session['selected_folder'] = selected_folder
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
        
        if "password" in request.form:
            # Handle password verification
            password = request.form["password"]
            filename = request.form["filename"]  # filename from the front-end
            # Verify password with API
            verify_url = f"{API_HOST}/verify_password/{filename}"
            response = requests.post(verify_url, data={"password": password})
            
            if response.status_code == 200 and response.json().get("message") == "Password correct":
                # Password is correct, allow download
                download_url = f"{API_HOST}/download/{filename}"
                file_response = requests.get(download_url)
                if file_response.status_code == 200:
                    return file_response.content, 200, {
                        'Content-Disposition': f'attachment; filename={filename}',
                        'Content-Type': 'application/octet-stream'
                    }
                else:
                    return jsonify({"error": "File not found."}), 404
            else:
                # Invalid password
                return jsonify({"error": "Invalid password."}), 401
            
        if "user_prompt" in request.form:
            user_prompt = request.form["user_prompt"]
            print(f"User Prompt: {user_prompt}")
            print(f"Debugging: selected prompt_template after user key in prompt: {g.selected_prompt_template}") # debugging
            print(f"Debugging: selected DB after user key in prompt: {g.selected_folder}") # debugging
            main_prompt_url = f"{API_HOST}/prompt_route"
            response = requests.post(main_prompt_url, data={"user_prompt": user_prompt})
            print(response.status_code)  # print HTTP response status code for debugging

            new_output_filename = ""
            if g.selected_prompt_template != "Question Answer":
                output_directory = "../extensions"
                new_output_filename = get_latest_file(output_directory) 

            if response.status_code == 200:
                response_json = response.json()
                output_filename = new_output_filename if new_output_filename else ""
                output_filename = os.path.basename(output_filename)
                
                return render_template("home.html", selected_folder=g.selected_folder, selected_prompt_template=g.selected_prompt_template, output_filename=output_filename, show_response_modal=True, response_dict=response_json)
        
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
        selected_folder=g.selected_folder,
        selected_prompt_template=g.selected_prompt_template,
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
    app.run(debug=False, host=args.host, port=args.port)
