import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self, db_config):
        self.connection = psycopg2.connect(**db_config)
        self.connection.autocommit = True
    #space
    def create_space(self, name, created):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO org.spaces (name, created)
                VALUES (%s, %s) RETURNING id;
            """, (name, created))
            return cursor.fetchone()[0]

    def get_space(self, space_id):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM org.spaces WHERE id = %s;
            """, (space_id,))
            return cursor.fetchone()

    def update_space(self, space_id, name=None, total_file_size_mb=None):
        with self.connection.cursor() as cursor:
            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if total_file_size_mb is not None:
                updates.append("total_file_size_mb = %s")
                params.append(total_file_size_mb)

            if updates:
                params.append(space_id)
                cursor.execute(f"""
                    UPDATE org.spaces SET {', '.join(updates)}
                    WHERE id = %s;
                """, params)

    def delete_space(self, space_id):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM org.spaces WHERE id = %s;
            """, (space_id,))
    # Handle Files
    def create_file(self, name, space_id, file_size_mb, created):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO org.spaces_files (name, space_id, file_size_mb, created)
                VALUES (%s, %s, %s, %s) RETURNING id;
            """, (name, space_id, file_size_mb, created))
            return cursor.fetchone()[0]

    def get_file(self, file_id):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM org.spaces_files WHERE id = %s;
            """, (file_id,))
            return cursor.fetchone()

    def update_file(self, file_id, name=None, file_size_mb=None):
        with self.connection.cursor() as cursor:
            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if file_size_mb is not None:
                updates.append("file_size_mb = %s")
                params.append(file_size_mb)

            if updates:
                params.append(file_id)
                cursor.execute(f"""
                    UPDATE org.spaces_files SET {', '.join(updates)}
                    WHERE id = %s;
                """, params)

    def delete_file(self, file_id):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM org.spaces_files WHERE id = %s;
            """, (file_id,))

    #Conversations (Memory)
    def create_conversation(self, sender, text, timestamp, space_id, file_id, related_message_id, user_ip, embedding):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO org.spaces_conversations (sender, text, timestamp, space_id, file_id, related_message_id, user_ip, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """, (sender, text, timestamp, space_id, file_id, related_message_id, user_ip, embedding))
            return cursor.fetchone()[0]

    def get_conversation(self, conversation_id):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM org.spaces_conversations WHERE id = %s;
            """, (conversation_id,))
            return cursor.fetchone()

    def update_conversation(self, conversation_id, text=None):
        with self.connection.cursor() as cursor:
            updates = []
            params = []

            if text is not None:
                updates.append("text = %s")
                params.append(text)

            if updates:
                params.append(conversation_id)
                cursor.execute(f"""
                    UPDATE org.spaces_conversations SET {', '.join(updates)}
                    WHERE id = %s;
                """, params)

    def delete_conversation(self, conversation_id):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM org.spaces_conversations WHERE id = %s;
            """, (conversation_id,))

    #Embeddings - Chunks
    def create_embedding(self, pageno, metadata, context, embedding, numtokens, cost, tabletext, source, imagepath, file_id, created):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO org.spaces_embeddings (pageno, metadata, context, embedding, numtokens, cost, tabletext, source, imagepath, file_id, created)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """, (pageno, metadata, context, embedding, numtokens, cost, tabletext, source, imagepath, file_id, created))
            return cursor.fetchone()[0]

    def get_embedding(self, embedding_id):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM org.spaces_embeddings WHERE id = %s;
            """, (embedding_id,))
            return cursor.fetchone()

    def update_embedding(self, embedding_id, context=None, embedding=None):
        with self.connection.cursor() as cursor:
            updates = []
            params = []

            if context is not None:
                updates.append("context = %s")
                params.append(context)
            if embedding is not None:
                updates.append("embedding = %s")
                params.append(embedding)

            if updates:
                params.append(embedding_id)
                cursor.execute(f"""
                    UPDATE org.spaces_embeddings SET {', '.join(updates)}
                    WHERE id = %s;
                """, params)

    def delete_embedding(self, embedding_id):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM org.spaces_embeddings WHERE id = %s;
            """, (embedding_id,))

    def close(self):
        self.connection.close()

# # Example usage:
# db_config = {
#     'dbname': 'your_database',
#     'user': 'your_user',
#     'password': 'your_password',
#     'host': 'your_host',
#     'port': 'your_port'
# }

# db_manager = DatabaseManager(db_config)

# # Creating a space
# space_id = db_manager.create_space('New Space', '2024-07-21')

# # Fetching a space
# space = db_manager.get_space(space_id)
# print(space)

# # Updating a space
# db_manager.update_space(space_id, name='Updated Space')

# # Deleting a space
# db_manager.delete_space(space_id)

# # Closing the connection
# db_manager.close()
