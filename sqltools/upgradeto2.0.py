import os
import json
import requests
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DBNAME = os.environ.get("DBNAME")
DBUSER = os.environ.get("DBUSER")
DBUSERPASSWORD = os.environ.get("DBUSERPASSWORD")
HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")

def get_db_connection():
    return psycopg2.connect(
        dbname=DBNAME,
        user=DBUSER,
        password=DBUSERPASSWORD,
        host=HOST,
        port=PORT
    )

def create_indexes(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            -- Create indexes on the conversations table
            CREATE INDEX IF NOT EXISTS idx_spaces_conversations_user_ip ON org.spaces_conversations(user_ip);
            CREATE INDEX IF NOT EXISTS idx_spaces_conversations_space_id ON org.spaces_conversations(space_id);
            CREATE INDEX IF NOT EXISTS idx_spaces_conversations_file_id ON org.spaces_conversations(file_id);

            -- Create indexes on the embeddings table
            CREATE INDEX IF NOT EXISTS idx_spaces_embeddings_id ON org.spaces_embeddings(id);
            CREATE INDEX IF NOT EXISTS idx_spaces_embeddings_source ON org.spaces_embeddings(source);
        """)
        conn.commit()

def update_spaces_table(conn):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        spaces_path = 'spaces'
        for space_name in os.listdir(spaces_path):
            space_dir = os.path.join(spaces_path, space_name)
            if os.path.isdir(space_dir):
                cursor.execute("SELECT id FROM org.spaces WHERE name = %s", (space_name,))
                space = cursor.fetchone()
                if not space:
                    cursor.execute("INSERT INTO org.spaces (name) VALUES (%s) RETURNING id", (space_name,))
                    space_id = cursor.fetchone()['id']
                else:
                    space_id = space['id']
                
                update_files_in_space(conn, space_id, space_dir)

def update_files_in_space(conn, space_id, space_dir):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        for file_name in os.listdir(space_dir):
            file_path = os.path.join(space_dir, file_name)
            if os.path.isfile(file_path):
                cursor.execute("SELECT id FROM org.spaces_files WHERE name = %s AND space_id = %s", (file_name, space_id))
                file = cursor.fetchone()
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if not file:
                    cursor.execute("INSERT INTO org.spaces_files (name, space_id, file_size_mb) VALUES (%s, %s, %s) RETURNING id", (file_name, space_id, file_size_mb))
                    file_id = cursor.fetchone()['id']
                else:
                    file_id = file['id']
                    cursor.execute("UPDATE org.spaces_files SET file_size_mb = %s WHERE id = %s", (file_size_mb, file_id))
                
                # Update embeddings for the file
                update_embeddings_for_file(conn, space_id, file_id, file_path)

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='iso-8859-1') as file:
            return file.read()

def sanitize_content(content):
    return content.replace('\x00', '')  # Remove null characters

def get_embedding_from_api(prompt):
    url = "http://localhost:11434/api/embeddings"
    payload = {
        "model": "nomic-embed-text",
        "prompt": prompt
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    return response.json()["embedding"]

def update_embeddings_for_file(conn, space_id, file_id, file_path):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT * FROM org.spaces_embeddings WHERE source = %s AND metadata->>'file_id' = %s", (file_path, str(file_id)))
        embeddings = cursor.fetchall()

        if not embeddings:
            # If no embeddings exist for this file, create them
            context = read_file_content(file_path)
            context = sanitize_content(context)  # Sanitize the content
            embedding = get_embedding_from_api(context)  # Get embedding from API
            metadata = {"space_id": space_id, "file_id": file_id}
            cursor.execute("""
                INSERT INTO org.spaces_embeddings (pageno, metadata, context, embedding, numtokens, cost, tabletext, source, imagepath, file_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (1, json.dumps(metadata), context, embedding, len(context.split()), 0.0, '', file_path, file_path, file_id))

def update_conversations_embeddings(conn):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT * FROM org.spaces_conversations")
        conversations = cursor.fetchall()

        for conversation in conversations:
            if conversation['embedding'] is None:
                embedding = get_embedding_from_api(conversation['text'])  # Get embedding from API
                cursor.execute(
                    "UPDATE org.spaces_conversations SET embedding = %s WHERE id = %s",
                    (embedding, conversation['id'])
                )

def main():
    conn = get_db_connection()
    try:
        create_indexes(conn)
        update_spaces_table(conn)
        update_conversations_embeddings(conn)
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
