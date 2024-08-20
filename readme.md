# Spaces API

**Spaces** api is a simple yet powerful RAG question-answering tool, it allows creating remote spaces (folders) and upload documents that you want to talk to or ask questions to. 

It is designed for managing, indexing, and retrieving information from documents within categorized spaces, making it useful for organizing and interacting with large amounts of documentation.

## Features

*Creating a New Space*
![alt text](/demos/newspace.png)

*Answering questions about a candidate for screening round* 
![demo showing anwers](/demos/demo.png?raw=true "Question & Answer")

*For every question you can choose a LLM of your choice depending on the complexity of infomration architecture in your document and past experience* 
![demo showing anwers](/demos/chooselocalllms.png "Choose your favourite LLM")


**Spaces as anything!** :
You can use space for managing, indexing, and retrieving any kind of information by containing them in spaces 

**Memory**: Remembers past conversations and uses it as memory to answer questions much faster and efficiently.

**Chat with your documentation**
Users can interact with specific documents within a space, such as asking questions about the document content.
The app provides detailed responses based on the document content.

**Information Tagging and Retrieval**:
Users can request specific information from a document using tags (e.g., "Get me the process information for tag 160-ZV-0291").
The app retrieves and displays the relevant information based on the tag.

## Getting Started

### Prerequisites

- Postgres sql 
- pgvector extension for postgres
- Node.js >= 
- Azure account (for app service hosting)
- Git
- Gemini API key 

### Installation

1. **Clone the Repository**

   ```bash
   # clone the repo
   git clone https://github.com/TensorKartDev/spaces.git
   cd spaces

   # install Spaces
   npm install 
   
   
## Project dependencies
Postgres sql 
pgvector 

### Set Up Python environment for web api
```bash
    # Create a new environment using conda or miniconda 
    conda create -n spaces python=3.10 
    # choose yes type "y"

    # activate the newly created environment 
    conda activate spaces
    
    # install these first 
    pip install request paddlepaddle paddleocr --upgrade

    # install the remaining packages
    pip install -r requirements.txt
```

### Start web api and react app
```bash
    # start Spaces backend web api 
    python app.py

    # Build and run Spaces
    npm run build 
    npm start 
```

## Setting Up PostgreSQL with pgvector

This guide provides instructions on how to set up the stable version of PostgreSQL with the pgvector extension on Windows, Linux, and Mac. pgvector is an extension for storing and querying vector data in PostgreSQL.

## Prerequisites

- PostgreSQL (latest stable version)
- Git
- Build tools (e.g., GCC for Linux, Xcode for Mac, Visual Studio for Windows)

## Installation Instructions

### 1. Install PostgreSQL

#### Windows

1. Download and install PostgreSQL from the [official PostgreSQL website](https://www.postgresql.org/download/windows/).
2. During installation, ensure that you include the `pgAdmin` and `Stack Builder` options.
3. Initialize and start the PostgreSQL server.

#### Linux

For Debian-based distributions (e.g., Ubuntu):

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

For Red Hat-based distributions (e.g., CentOS, Fedora):
```bash
sudo dnf install postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

Mac
```bash
Using Homebrew:
brew update
brew install postgresql
brew services start postgresql
```
Install pgvector Extension
```
# Clone the pgvector Repository
git clone https://github.com/pgvector/pgvector.git
cd pgvector
```

Build and Install pgvector

Windows
Open the Visual Studio Developer Command Prompt.
Navigate to the pgvector directory.
Run the following commands:
```
set PATH=%PATH%;C:\Program Files\PostgreSQL\<your-postgresql-version>\bin
make
make install
```

Replace <your-postgresql-version> with the installed PostgreSQL version directory.
Linux
Ensure that pg_config is in your PATH:
```
export PATH=/usr/pgsql-<your-postgresql-version>/bin:$PATH
```
Replace <your-postgresql-version> with your installed PostgreSQL version.

Run the following commands:
```
make
sudo make install
```
**Mac**
Ensure that pg_config is in your PATH:
```
export PATH=/usr/local/opt/postgresql/bin:$PATH
```
Adoption and Contributions

Your organization uses authentik? We'd love to add your logo to the readme and our website! Email us @ us@tensorkart.com or open a GitHub Issue/PR! For more information on how to contribute to spaces, please refer to our CONTRIBUTING.md file.
