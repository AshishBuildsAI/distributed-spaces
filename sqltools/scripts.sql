-- Create the spaces table
CREATE TABLE org.spaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    total_file_size_mb NUMERIC DEFAULT 0, -- Total file size on disk in megabytes
    created date NOT NULL
);

-- Create the files table with an additional column for file size in megabytes
CREATE TABLE org.spaces_files (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    space_id INTEGER REFERENCES org.spaces(id),
    file_size_mb NUMERIC NOT NULL, -- File size in megabytes
    created date NOT NULL
);

-- Create the conversations table
CREATE TABLE org.spaces_conversations (
    id SERIAL PRIMARY KEY,
    sender VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    space_id INTEGER REFERENCES org.spaces(id),
    file_id INTEGER REFERENCES org.spaces_files(id),
    related_message_id INTEGER REFERENCES org.spaces_conversations(id), -- Self-referencing column to indicate the related message
    user_ip INET NOT NULL, -- Column to store the user's IP address
    embedding VECTOR(768) -- Column to store the vector representation of the conversation
);


-- Create the embeddings table with file_id column
CREATE TABLE IF NOT EXISTS org.spaces_embeddings (
    id SERIAL PRIMARY KEY,
    pageno INTEGER,
    metadata JSONB,
    context TEXT,
    embedding VECTOR(768),
    numtokens INTEGER,
    cost DOUBLE PRECISION,
    tabletext TEXT,
    source TEXT,
    imagepath TEXT,
    file_id INTEGER REFERENCES org.spaces_files(id), -- Foreign key to spaces_files table
    created date NOT NULL
);

ALTER TABLE IF EXISTS org.spaces_embeddings
    OWNER TO postgres;

-- Create index for faster querying
CREATE INDEX idx_spaces_conversations_user_ip ON org.spaces_conversations(user_ip);
CREATE INDEX IF NOT EXISTS idx_spaces_conversations_user_ip ON org.spaces_conversations(user_ip);
CREATE INDEX IF NOT EXISTS idx_spaces_conversations_space_id ON org.spaces_conversations(space_id);
CREATE INDEX IF NOT EXISTS idx_spaces_conversations_file_id ON org.spaces_conversations(file_id);

-- Create indexes on the embeddings table
CREATE INDEX IF NOT EXISTS idx_spaces_embeddings_id ON org.spaces_embeddings(id);
CREATE INDEX IF NOT EXISTS idx_spaces_embeddings_source ON org.spaces_embeddings(source);

-- Create the necessary triggers

-- Trigger function to update the total_file_size_mb in spaces when a new file is added
CREATE OR REPLACE FUNCTION update_total_file_size()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE org.spaces
    SET total_file_size_mb = total_file_size_mb + NEW.file_size_mb
    WHERE id = NEW.space_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger function to update the total_file_size_mb in spaces when a file is deleted
CREATE OR REPLACE FUNCTION decrease_total_file_size()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE org.spaces
    SET total_file_size_mb = total_file_size_mb - OLD.file_size_mb
    WHERE id = OLD.space_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger for inserting new files
CREATE TRIGGER after_insert_files
AFTER INSERT ON org.spaces_files
FOR EACH ROW
EXECUTE FUNCTION update_total_file_size();

-- Create the trigger for deleting files
CREATE TRIGGER after_delete_files
AFTER DELETE ON org.spaces_files
FOR EACH ROW
EXECUTE FUNCTION decrease_total_file_size();
