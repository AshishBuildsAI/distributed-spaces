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
from transformers import AutoTokenizer, AutoModelForCausalLM

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

# # Load the LLAMA model and tokenizer
# llama_model_name = "ggml-model-q4_k.gguf"
# llama_model_directory = "./models"
# llama_tokenizer = AutoTokenizer.from_pretrained(llama_model_name, cache_dir=llama_model_directory)
# llama_model = AutoModelForCausalLM.from_pretrained(llama_model_name, cache_dir=llama_model_directory)

# # Load the Mistral model and tokenizer
# mistral_model_name = "mistral-7b-v0.1.Q4_K_M.gguf"
# mistral_model_directory = "./models"
# mistral_tokenizer = AutoTokenizer.from_pretrained(mistral_model_name, cache_dir=mistral_model_directory)
# mistral_model = AutoModelForCausalLM.from_pretrained(mistral_model_name, cache_dir=mistral_model_directory)

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

def get_top(query_embedding, conn, schema, table, space, filename=None,numrows=5):
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
            """, (space))
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
                else :
                     #print("Possibly array already")
                     embedding = embedding_str

                # Safe normalization
                norm = np.linalg.norm(embedding)
                #print(norm)
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
                #print(type(embedding_str))
                logging.error(f"Error processing row : {e}")
         # Sort results by weighted similarity

        results.sort(key=lambda x: x[-1], reverse=True)
        
        # Return the top 3 most similar documents
        top_docs = results
        #conn.commit()
        return top_docs
    except Exception as e:
        print(e)
        rows = ""
    #conn.commit()
    return rows

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

def get_postgres_size(schema, table_name):
    query = f"""
            SELECT 
                pg_size_pretty(pg_total_relation_size('{schema}.' || {table_name})) as size
            FROM 
                information_schema.tables
            WHERE 
                table_schema = %s;
                
        """
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
    """Helper function to format the size in a human-readable format."""
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
                    files.append({
                        "name": f,
                        "isIndexed": is_indexed
                    })
        return jsonify({"files": files})
    return jsonify({"message": "Space not found"}), 404
def generate_response_with_model(envelope, model, tokenizer, poweredby):
    # Tokenize the input text
    inputs = tokenizer(envelope, return_tensors="pt")

    # Generate the response
    outputs = model.generate(**inputs, max_length=150, num_return_sequences=1)

    # Decode the generated text
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("This response was powered by ", poweredby)
    return {"text": response_text} 

def chatIM(messages,model):
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
    #model_choice = data.get('model_choice', 'llama','gemini', 'mistral') 
    
    if not space or not question:
        return jsonify({"error": "Space and query are required"}), 400
    
    try:
        embed = get_embeddings(question)
        
        if filename:
            res = get_top(embed, conn=conn, schema=dbschema, table=dbtable, space=space, filename=filename, numrows=10)
        else:
            res = get_top(embed, conn=conn, schema=dbschema, table=dbtable, space=space, numrows=10)
        
        envelope = f"You are a friendly AI assistant who finds information for HR assistants, Engineers, sales teams and many more. only using the given context {res} answer the question in as much detail as you can, here is the question or instruction {question}"
            # Construct the messages with the additional parameters
        messages = [
            {"role": "system", "content": f"Space: {space}, Filename: {filename}"},
            {"role": "user", "content": envelope}
        ]

        try:
            print(model)
            response_message = chatIM(messages,model)
            return jsonify(response_message), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            # if model_choice == 'mistral':
            #     response = generate_response_with_model(envelope, mistral_model, mistral_tokenizer, "Mistral")
            
            # elif model_choice=='llama':
            #     response = generate_response_with_model(envelope, llama_model, llama_tokenizer, "llama")
        # else:
        #     response = language_model.generate_content(envelope)
        # print("Bot : ", res, response.text)
        # return jsonify(response.text)
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
            INSERT INTO {dbschema}.{dbtable} (pageno, context, embedding, numtokens, cost, source, imagepath)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (i+1, ocr_text, embedding, len(ocr_text.split()), cost, filename, os.path.join(images_folder, f"{filename}_page_{i+1}.png")))
        conn.commit()
    
    return jsonify({"message": f"Indexed PDF {filename} in space: {space}", "imageslocation": images_folder}), 200


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