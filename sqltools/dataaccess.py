import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
import numpy as np
from dotenv import load_dotenv
import os
load_dotenv()
from embedlib.embeddings import get_embeddings
class DataKeeper:
    def __init__(self):
        print("called!")
        self.connection = psycopg2.connect(
            dbname=os.environ["DBNAME"],
            user=os.environ["DBUSER"],
            password=os.environ["DBUSERPASSWORD"],
            host=os.environ["HOST"],
            port=os.environ["PORT"]
        )
        self.config ={}
        self.config["dbschema"] =os.environ["SCHEMA"]
        self.config["spaces_table"] =os.environ["SPACES_TABLE"]
        self.config["embeddings_table"] =os.environ["EMBEDDINGS_TABLE"]
        self.config["files_table"] =os.environ["FILES_TABLE"]
        self.config["conversations_table"] =os.environ["CONVERSATIONS_TABLE"]
        self.connection.autocommit = os.environ["AUTOCOMMIT"]
    
    def save_conversation(self, space, filename, message, user_ip):
        # data = request.json
        # space = data.get('space')
        # filename = data.get('filename', '')
        # message = data.get('message')
        # user_ip = request.remote_addr

        if not space or not message:
            raise Exception("Space and message are required for saving the conversation")
        
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT id FROM {self.config.dbschema}.{self.config.spaces_table} WHERE name = %s", (space,))
            space_id = cursor.fetchone()
            if not space_id:
                cursor.execute(f"INSERT INTO {self.config.dbschema}.{self.config.conversations_table} (name) VALUES (%s) RETURNING id", (space,))
                space_id = cursor.fetchone()[0]
            else:
                space_id = space_id[0]

            if filename:
                cursor.execute(f"SELECT id FROM {self.config.dbschema}.{self.config.files_table} WHERE name = %s AND space_id = %s", (filename, space_id))
                file_id = cursor.fetchone()
                if not file_id:
                    cursor.execute(f"INSERT INTO {self.config.dbschema}.{self.config.files_table} (name, space_id, file_size_mb) VALUES (%s, %s, %s) RETURNING id", (filename, space_id, 0))
                    file_id = cursor.fetchone()[0]
                else:
                    file_id = file_id[0]
            else:
                file_id = None

            text_content = message['text']
            embedding = get_embeddings(text_content)

            cursor.execute(f"""
                INSERT INTO {self.config.dbschema}.{self.config.conversations_table} (sender, text, timestamp, space_id, file_id, user_ip, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (message['sender'], message['text'], message['timestamp'], space_id, file_id, user_ip, embedding))
            self.connection.commit()


    # Function to save OCR results to PostgreSQL
    def save_ocr_result(self, source, pageno, imagesource, ocrtext, embedding, cost, metadata):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO {self.config.dbschema}.spaces_embeddings (source, pageno, imagepath, context, embedding, cost, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """, (source, pageno, imagesource, ocrtext, embedding, cost, json.dumps(metadata)))
            self.connection.commit()
            return cursor.fetchone()[0]
    def insert_data(self, table, data):
        """
        Inserts data into the specified table.
        
        :param table: Name of the table where data will be inserted.
        :param data: Dictionary containing column names as keys and corresponding values.
        """
        columns = data.keys()
        values = [data[column] for column in columns]
        insert_statement = f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s"
        
        with self.connection.cursor() as cursor:
            cursor.execute(insert_statement, (tuple(values),))

    def get_data(self, table, columns='*', conditions=None):
        """
        Retrieves data from the specified table.
        
        :param table: Name of the table from which data will be retrieved.
        :param columns: Columns to retrieve, default is all columns.
        :param conditions: Optional conditions for data retrieval.
        :return: List of dictionaries representing the rows.
        """
        if isinstance(columns, list):
            columns = ', '.join(columns)
        query = f"SELECT {columns} FROM {table}"
        
        if conditions:
            query += f" WHERE {conditions}"
        
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def close_connection(self):
        """Closes the database connection."""
        self.connection.close()
    
    def get_top_chunks(self, query_embedding, schema, table, space, filename=None, numrows=5):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                print(filename)
                if filename:
                    cursor.execute(f"""
                        SELECT pageno, context, metadata, source, imagepath, embedding, COALESCE(numtokens, 0)
                        FROM {schema}.{table} where metadata->>'space' = %s
                        and source = %s
                    """, (space, filename))
                else:
                    cursor.execute(f"""
                        SELECT pageno, context, metadata, source, imagepath, embedding, COALESCE(numtokens, 0)
                        FROM {schema}.{table} where metadata->>'space' = %s
                    """, (space,))
                rows = cursor.fetchall()
                print("rows", len(rows))
                # Compute similarities and store results
            results = []
            wrong_embeddings = []
            # iterate in rows and find the similarity by averaging
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
            #sort and return the results
            results.sort(key=lambda x: x[-1], reverse=True)
            top_docs = results
            return top_docs
        except Exception as e:
            print(e)
            rows = ""
        return rows


