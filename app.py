from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
import json, os, signal
from InputDocument import InputDocument
import requests
from dotenv import load_dotenv
import pathlib
import textwrap
import psycopg2
from datetime import datetime
from paddleocr import PaddleOCR
import google.generativeai as genai
import tqdm as notebook_tqdm
from psycopg2.extras import execute_values
from psycopg2.extras import DictCursor
import numpy as np
from sentence_transformers import SentenceTransformer
load_dotenv()
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
from sqltools.dataaccess import DataKeeper
dbkeeper = DataKeeper()


ocr = PaddleOCR(use_angle_cls=True, lang='en')

GOOGLE_API_KEY = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
CORS(app)

ROOT_DIR = 'spaces'
# PostgreSQL connection
conn = psycopg2.connect(
    dbname=os.environ["DBNAME"],
    user=os.environ["DBUSER"],
    password=os.environ["DBUSERPASSWORD"],
    host=os.environ["HOST"],
    port=os.environ["PORT"]
)



db = os.environ["DBNAME"]
dbschema = os.environ["SCHEMA"]
dbtable = "spaces_embeddings"
cur = conn.cursor()
model_dir = "models/all-MiniLM-L6-v2"
embedding_model = ''
logging.basicConfig(level=logging.DEBUG)

# Check if the model directory exists
if not os.path.exists(model_dir):
    # Load and save the model to the specified directory
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding_model.save(model_dir)
else:
    # Load the model from the specified directory
    embedding_model = SentenceTransformer(model_dir)

# Function to perform OCR on an image
def perform_ocr(image_path):
    result = ocr.ocr(image_path, cls=True)
    ocr_text = "\n".join([line[1][0] for line in result[0]])
    return ocr_text

#moved
def get_embeddings(content):
    url = "http://localhost:11434/api/embeddings"
    payload = {
        "model": "nomic-embed-text",
        "prompt": content
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    return response.json()["embedding"]
#moved
def get_top(query_embedding, conn, schema, table, space, filename=None, numrows=5):
    try:
        print(filename)
        if filename:
            cur.execute(f"""
                SELECT pageno, context, metadata, source, imagepath, embedding, COALESCE(numtokens, 0)
                FROM {schema}.{table} where metadata->>'space' = %s
                and source = %s
            """, (space, filename))
        else:
            cur.execute(f"""
                SELECT pageno, context, metadata, source, imagepath, embedding, COALESCE(numtokens, 0)
                FROM {schema}.{table} where metadata->>'space' = %s
            """, (space,))
        rows = cur.fetchall()
        print("rows", len(rows))
        # Compute similarities and store results
        results = []
        wrong_embeddings = []
        for row in rows:
            pageno, context, metadata, source, imagepath, embedding_str, numtokens = row
            try:
                if isinstance(embedding_str, str):
                    embedding = json.loads(embedding_str)
                elif isinstance(embedding_str, (bytes, bytearray)):
                    embedding = json.loads(embedding_str.decode('utf-8'))
                elif isinstance(embedding_str, list):
                    embedding = np.array(embedding_str)
                else:
                    embedding = embedding_str

                # Safe normalization
                norm = np.linalg.norm(embedding)
                if norm == 0:
                    logging.warning(f"Skipping normalization for zero vector: {embedding}")
                    continue

                embedding = embedding / norm
                similarity = np.dot(query_embedding, embedding)

                # Ensure numtokens is a valid number
                numtokens = numtokens if numtokens is not None else 0

                # Optionally, weight similarity by the number of tokens or other criteria
                weighted_similarity = similarity * (1 + 0.01 * numtokens)

                results.append((pageno, context, metadata, source, imagepath, weighted_similarity))
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error for row: {e}")
            except Exception as e:
                logging.error(f"Error processing row : {e}")

        results.sort(key=lambda x: x[-1], reverse=True)

        top_docs = results
        return top_docs
    except Exception as e:
        print(e)
        rows = ""
    return rows
#moved
# Function to save OCR results to PostgreSQL
def save_ocr_result(source, pageno, imagesource, ocrtext, embedding, cost, metadata):
    cur.execute(f"""
        INSERT INTO {dbschema}.spaces_embeddings (source, pageno, imagepath, context, embedding, cost, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
    """, (source, pageno, imagesource, ocrtext, embedding, cost, json.dumps(metadata)))
    conn.commit()
    return cur.fetchone()[0]

@app.route('/create_space', methods=['POST'])
def create_space():
    space_name = request.json['spaceName']
    space_path = os.path.join(ROOT_DIR, space_name)
    if not os.path.exists(space_path):
        os.makedirs(space_path)
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("INSERT INTO org.spaces (name) VALUES (%s) RETURNING id", (space_name,))
            #space_id = cursor.fetchone()['id']
            conn.commit()
        return jsonify({"message": f"New Space {space_name} created successfully"}), 201
    return jsonify({"message": f"Space '{space_name}' already exists"}), 400

#moved - but incomplete
@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    data = request.json
    space = data.get('space')
    filename = data.get('filename', '')
    message = data.get('message')
    user_ip = request.remote_addr
    
    dbkeeper.save_conversation(space=space, filename=filename, message=message, user_ip=user_ip)
    if not space or not message:
        return jsonify({"status": "error", "message": "Space and message are required"}), 400

    conn = psycopg2.connect(
        dbname=os.environ["DBNAME"],
        user=os.environ["DBUSER"],
        password=os.environ["DBUSERPASSWORD"],
        host=os.environ["HOST"],
        port=os.environ["PORT"]
    )
    cursor = conn.cursor()

    cursor.execute(f"SELECT id FROM {dbschema}.spaces WHERE name = %s", (space,))
    space_id = cursor.fetchone()
    if not space_id:
        cursor.execute(f"INSERT INTO {dbschema}.spaces (name) VALUES (%s) RETURNING id", (space,))
        space_id = cursor.fetchone()[0]
    else:
        space_id = space_id[0]

    if filename:
        cursor.execute(f"SELECT id FROM {dbschema}.spaces_files WHERE name = %s AND space_id = %s", (filename, space_id))
        file_id = cursor.fetchone()
        if not file_id:
            cursor.execute(f"INSERT INTO {dbschema}.spaces_files (name, space_id, file_size_mb) VALUES (%s, %s, %s) RETURNING id", (filename, space_id, 0))
            file_id = cursor.fetchone()[0]
        else:
            file_id = file_id[0]
    else:
        file_id = None

    text_content = message['text']
    embedding = get_embeddings(text_content)

    cursor.execute(f"""
        INSERT INTO {dbschema}.spaces_conversations (sender, text, timestamp, space_id, file_id, user_ip, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (message['sender'], message['text'], message['timestamp'], space_id, file_id, user_ip, embedding))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "conversation saved"})

@app.route('/list_spaces', methods=['GET'])
def list_spaces():
    spaces = [name for name in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, name))]
    return jsonify({"spaces": spaces})

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

def format_size(size):
    power = 1024
    n = 0
    power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

@app.route('/list_files/<space>', methods=['GET'])
def list_files(space):
    space_path = os.path.join(ROOT_DIR, space)
    
    if os.path.exists(space_path):
        files = []
        for f in os.listdir(space_path):
            file_path = os.path.join(space_path, f)
            if "DS_Store" not in file_path:
                if os.path.isfile(file_path):
                    images_folder = file_path[0:file_path.rindex(".")]
                    images_folder_path = images_folder
                    is_indexed = os.path.isdir(images_folder_path)
                    ## TODO : check if all pages have db records only then say indexed is true
                    files.append({
                        "name": f,
                        "isIndexed": is_indexed
                    })
        return jsonify({"files": files})
    return jsonify({"message": "Space not found"}), 404

def generate_response_with_model(envelope, model, tokenizer, poweredby):
    inputs = tokenizer(envelope, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=150, num_return_sequences=1)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("This response was powered by ", poweredby)
    return {"text": response_text}

def chatIM(messages, model):
    print(model)
    r = requests.post(
        "http://0.0.0.0:11434/api/chat",
        json={"model": model, "messages": messages, "stream": True},
        stream=True
    )
    r.raise_for_status()
    output = ""

    for line in r.iter_lines():
        body = json.loads(line)
        if "error" in body:
            raise Exception(body["error"])
        if body.get("done") is False:
            message = body.get("message", "")
            content = message.get("content", "")
            output += content
        if body.get("done", False):
            message["content"] = output
            return message

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    space = data.get('space')
    filename = data.get('filename')
    question = data.get('query')
    model = data.get('model')
    
    if not space or not question:
        return jsonify({"error": "Space and query are required"}), 400
    
    try:
        embed = get_embeddings(question)
        
        if filename:
            res = get_top(embed, conn=conn, schema=dbschema, table=f"{dbschema}.spaces_embeddings", space=space, filename=filename, numrows=10)
        else:
            res = get_top(embed, conn=conn, schema=dbschema, table=f"{dbschema}.spaces_embeddings", space=space, numrows=10)
        
        envelope = f"You are a friendly AI assistant who finds information for HR assistants, Engineers, sales teams and many more. only using the given context {res} answer the question in as much detail as you can, here is the question or instruction {question}"
        messages = [
            {"role": "system", "content": f"Space: {space}, Filename: {filename}"},
            {"role": "user", "content": envelope}
        ]

        try:
            print(model)
            response_message = chatIM(messages, model)
            return jsonify(response_message), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

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
    return jsonify({"success": True, "message": "Server is shutting down..."})

@app.route('/convert_pdf/<filename>', methods=['POST'])
def convert_pdf(filename):
    space = request.json['space']
    if not space:
        return jsonify({"error": "Space not provided"}), 400

    space_path = os.path.join(ROOT_DIR, space)
    filepath = os.path.join(space_path, filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    pdf_doc = InputDocument(document_name=filename, file_path=filepath)
    images_folder = pdf_doc.imagesfolder
    
    embeddings = []
    for image_file in os.listdir(images_folder):
        if image_file.endswith(".png"):
            image_path = os.path.join(images_folder, image_file)
            pageno = int(image_file.split('_')[1].split('.')[0])
            metadata = {"filename": filename, "page": pageno, "space": space}
            ocr_text = perform_ocr(image_path)
            content = f"{metadata} {ocr_text}"
            embedding = get_embeddings(content)
            cost = len(content.split()) * 0.0001
            
            save_ocr_result(source=filename, pageno=pageno, imagesource=image_path, ocrtext=ocr_text, embedding=embedding, cost=cost, metadata=metadata)
            embeddings.append(embedding)
    
    for i, embedding in enumerate(embeddings):
        cur.execute(f"""
            INSERT INTO {dbschema}.spaces_embeddings (pageno, context, embedding, numtokens, cost, source, imagepath)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (i+1, ocr_text, embedding, len(ocr_text.split()), cost, filename, os.path.join(images_folder, f"{filename}_page_{i+1}.png")))
        conn.commit()
    
    return jsonify({"message": f"Indexed PDF {filename} in space: {space}", "imageslocation": images_folder}), 200

@app.route('/get_conversations', methods=['GET'])
def get_conversations():
    ip_address = request.remote_addr
    space = request.args.get('space')
    filename = request.args.get('filename')

    conn = psycopg2.connect(
        dbname=os.environ["DBNAME"],
        user=os.environ["DBUSER"],
        password=os.environ["DBUSERPASSWORD"],
        host=os.environ["HOST"],
        port=os.environ["PORT"]
    )
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT sender, text, timestamp, space_id, file_id, user_ip, embedding
        FROM {dbschema}.spaces_conversations
        WHERE user_ip = %s
    """, (ip_address,))
    conversations = cursor.fetchall()

    if not conversations and space:
        cursor.execute(f"""
            SELECT sender, text, timestamp, space_id, file_id, user_ip, embedding
            FROM {dbschema}.spaces_conversations
            WHERE space_id = (SELECT id FROM {dbschema}.spaces WHERE name = %s)
        """, (space,))
        conversations = cursor.fetchall()

        if not conversations and filename:
            cursor.execute(f"""
                SELECT sender, text, timestamp, space_id, file_id, user_ip, embedding
                FROM {dbschema}.spaces_conversations
                WHERE file_id = (
                    SELECT id
                    FROM {dbschema}.spaces_files
                    WHERE name = %s AND space_id = (SELECT id FROM {dbschema}.spaces WHERE name = %s)
                )
            """, (filename, space))
            conversations = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({"conversations": conversations})

if __name__ == '__main__':
    if not os.path.exists(ROOT_DIR):
        os.makedirs(ROOT_DIR)
    app.run(debug=True)
