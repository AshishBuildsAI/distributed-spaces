from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from pdf2image import convert_from_path
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request
import json, os, signal
from InputDocument import InputDocument

app = Flask(__name__)
CORS(app)

ROOT_DIR = 'spaces'

@app.route('/create_space', methods=['POST'])
def create_space():
    space_name = request.json['spaceName']
    space_path = os.path.join(ROOT_DIR, space_name)
    if not os.path.exists(space_path):
        os.makedirs(space_path)
        return jsonify({"message": "Space created successfully"}), 201
    return jsonify({"message": "Space already exists"}), 400

@app.route('/list_spaces', methods=['GET'])
def list_spaces():
    spaces = [name for name in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, name))]
    return jsonify({"spaces": spaces})

@app.route('/list_files/<space>', methods=['GET'])
def list_files(space):
    space_path = os.path.join(ROOT_DIR, space)
    if os.path.exists(space_path):
        files = [f for f in os.listdir(space_path) if os.path.isfile(os.path.join(space_path, f))]
        return jsonify({"files": files})
    return jsonify({"message": "Space not found"}), 404

@app.route('/index_file', methods=['POST'])
def index_file():
    space = request.json['space']
    filename = request.json['filename']
    # Implement file indexing logic here
    return jsonify({"message": f"File '{filename}' indexed in space '{space}'"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    space = request.json['space']
    query = request.json['query']
    # Implement chatbot logic here
    response = f"Query '{query}' in space '{space}' is processed"
    return jsonify({"response": response})

@app.route('/upload_file/<space>', methods=['POST'])
def upload_file(space):
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    space_path = os.path.join(ROOT_DIR, space)
    if not os.path.exists(space_path):
        return jsonify({"message": "Space not found"}), 404
    file.save(os.path.join(space_path, file.filename))
    return jsonify({"message": "File uploaded successfully"}), 200

@app.route('/stopServer', methods=['GET'])
def stopServer():
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({ "success": True, "message": "Server is shutting down..." })

@app.route('/convert_pdf/<filename>', methods=['POST'])
def convert_pdf(filename):
   
    space = request.json['space']
    # print(space,filename )
    if not space:
        return jsonify({"error": "Space not provided"}), 400
    space_path = os.path.join(ROOT_DIR, space)
    filepath = os.path.join(space_path, filename)
    # print(filepath)
    pdf_doc = InputDocument(document_name=filename, file_path=filepath)
    pdf_doc.pages
    
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    # image_files.append((f"{filename}_page_{i+1}.jpg", image_file))

    return jsonify({"message": f"PDF converted to images in space: {space}", "imageslocation": ""}), 200

if __name__ == '__main__':
    if not os.path.exists(ROOT_DIR):
        os.makedirs(ROOT_DIR)
    app.run(debug=True)
