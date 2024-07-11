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
import numpy as np
from sentence_transformers import SentenceTransformer
load_dotenv()
import logging

ocr = PaddleOCR(use_angle_cls=True, lang='en')
GOOGLE_API_KEY = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
language_model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
CORS(app)

ROOT_DIR = 'spaces'
# In-memory storage for conversations
conversations = {}
# PostgreSQL connection
conn = psycopg2.connect(
    dbname=os.environ["DBNAME"],
    user=os.environ["DBUSER"],
    password=os.environ["DBUSERPASSWORD"],
    host=os.environ["HOST"],
    port=os.environ["PORT"]
)
db = "ai"
dbschema = "public"
dbtable = "spaces_eicp"
cur = conn.cursor()
model_dir = "models/all-MiniLM-L6-v2"
embedding_model =''
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

def create_table(schema, table_name):
    with conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
                    id SERIAL PRIMARY KEY,
                    pageno INTEGER,
                    metadata JSONB,
                    context TEXT,
                    embedding VECTOR(384),
                    numtokens INTEGER,
                    cost FLOAT,
                    tabletext TEXT,
                    source TEXT,
                    imagepath TEXT
                )
            """)
            conn.commit()
    return True

def get_embeddings(content):
    # Generate embeddings using the local model
    embeddings = embedding_model.encode(content, convert_to_tensor=True)
    return embeddings.tolist()
create_table(schema=dbschema, table_name=dbtable)
logging.basicConfig(level=logging.DEBUG)

def get_top1_similar_docs(query_embedding, conn, schema, table):
    # Normalize the query embedding
    query_embedding = np.array(query_embedding)
    query_embedding = query_embedding / np.linalg.norm(query_embedding)
    
    cur = conn.cursor()
    # Use normalized embeddings and add additional filters for relevance
    cur.execute(f"""
        SELECT pageno, context, tabletext, source, imagepath, embedding, COALESCE(numtokens, 0)
        FROM {schema}.{table}
    """)
    
    rows = cur.fetchall()
    
    # Compute similarities and store results
    results = []
    for row in rows:
        pageno, context, tabletext, source, imagepath, embedding_str, numtokens = row
        try:
            embedding = np.array(json.loads(embedding_str))  # Convert JSON string to numpy array
            
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
            
            results.append((pageno, context, tabletext, source, imagepath, weighted_similarity))
        except Exception as e:
            logging.error(f"Error processing row {row}: {e}")
    
    # Sort results by weighted similarity
    results.sort(key=lambda x: x[-1], reverse=True)
    
    # Return the top 3 most similar documents
    top3_docs = results[:5]
    return top3_docs


# Function to save OCR results to PostgreSQL
def save_ocr_result(source, pageno, imagesource, ocrtext, embedding, cost, metadata):
    cur.execute(f"""
        INSERT INTO {dbschema}.{dbtable} (source, pageno, imagepath, context, embedding, cost, metadata)
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
        files = []
        for f in os.listdir(space_path):
            file_path = os.path.join(space_path, f)
            if "DS_Store" not in file_path:
                if os.path.isfile(file_path):
                    images_folder = file_path[0:file_path.rindex(".")]
                    images_folder_path = images_folder
                    is_indexed = os.path.isdir(images_folder_path)
                    files.append({
                        "name": f,
                        "isIndexed": is_indexed
                    })
        return jsonify({"files": files})
    return jsonify({"message": "Space not found"}), 404


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    space = data.get('space')
    filename = data.get('filename')
    question = data.get('query')
    
    if not space or not filename or not question:
        return jsonify({"error": "Space, filename, and query are required"}), 400
    
    try:
        embed = get_embeddings(question)
        res = get_top1_similar_docs(embed, conn=conn,schema=dbschema, table=dbtable)
        envelope=f"You are an AI assitant, capable of replying with precise information only from the documetn or documents,if dont know the answer, dont answer from anywhere only use the context {res} to answer the question {question}, add smiley in the end"
        response = language_model.generate_content(envelope)
        print("Bot : ", res, response.text)
        return jsonify(response.text)
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
    
    # Verify the PDF file exists
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    # Convert the PDF to images using InputDocument (assuming this class has a method for this)
    pdf_doc = InputDocument(document_name=filename, file_path=filepath)
    #pdf_doc.pages
    images_folder = pdf_doc.imagesfolder  # Get the folder where images are saved
    
    #create_table(schema=dbschema, table_name=dbtable)
    embeddings = []
    # Iterate over all PNG files in the images folder
    for image_file in os.listdir(images_folder):
        if image_file.endswith(".png"):
            image_path = os.path.join(images_folder, image_file)
            pageno = int(image_file.split('_')[1].split('.')[0])  # Extract page number from filename
            metadata = {"filename": filename, "page": pageno, "space": space}
            ocr_text = perform_ocr(image_path)
            content = f"{metadata} {ocr_text}"
            embedding = get_embeddings(content)
            cost = len(content.split()) * 0.0001  # Example cost calculation
            
            save_ocr_result(source=filename, pageno=pageno, imagesource=image_path, ocrtext=ocr_text, embedding=embedding, cost=cost, metadata=metadata)
            embeddings.append(embedding)
    
    #table_name = f"{space}_{filename.split('.')[0]}"
    #create_table('public', table_name)
    
    for i, embedding in enumerate(embeddings):
        cur.execute(f"""
            INSERT INTO public.{table_name} (pageno, context, embedding, numtokens, cost, source, imagepath)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (i+1, ocr_text, embedding, len(ocr_text.split()), cost, filename, os.path.join(images_folder, f"{filename}_page_{i+1}.png")))
        conn.commit()
    
    return jsonify({"message": f"PDF converted to images in space: {space}", "imageslocation": images_folder}), 200


@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    data = request.get_json()
    user_message = data['userMessage']
    bot_message = data['botMessage']
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    if date_str not in conversations:
        conversations[date_str] = []
    
    if user_message not in conversations[date_str]:
        conversations[date_str].append(user_message)
    if bot_message not in conversations[date_str]:
        conversations[date_str].append(bot_message)
    
    return jsonify({"status": "success"})

@app.route('/save_all_conversations', methods=['POST'])
def save_all_conversations():
    all_conversations = []
    seen_messages = set()
    
    for date, msgs in conversations.items():
        for msg in msgs:
            msg_tuple = (msg['sender'], msg['text'], msg['timestamp'])
            if msg_tuple not in seen_messages:
                seen_messages.add(msg_tuple)
                all_conversations.append(msg)
    
    with open('all_conversations.json', 'w') as f:
        json.dump(all_conversations, f)
    
    return jsonify({"status": "all conversations saved", "total_conversations": len(all_conversations)})

@app.route('/get_conversations/<date>', methods=['GET'])
def get_conversations(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    if date in conversations:
        return jsonify(conversations[date])
    else:
        return jsonify([])

if __name__ == '__main__':
    if not os.path.exists(ROOT_DIR):
        os.makedirs(ROOT_DIR)
    app.run(debug=True)