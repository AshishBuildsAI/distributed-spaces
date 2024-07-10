# Spaces App

**Spaces** is a versatile document management and question-answering tool that empowers users to upload, organize, and interact with their PDF documents efficiently. The app features flexible architecture, allowing plug-and-play components and cloud-native deployment. Users can create folders called "spaces," add documents, and leverage powerful AI capabilities to generate knowledge maps and extract information seamlessly. The app offers both open-source and premium versions to cater to a wide range of users and organizations.

## Features

- **Generation and Knowledge Map**: Automatically generate comprehensive knowledge maps from your documents, providing a visual and interactive way to explore the information.
- **Privacy and IP Security**: Ensures the highest level of security for your documents, protecting your intellectual property and maintaining privacy.
- **Community Edition**: Open-source version available for individual users and small organizations.
- **Enterprise Edition**: Premium version with enhanced features, support, and scalability for larger organizations.
- **Plugins and Add-Ons**:
  - **Bulletin Generator**: Create automated bulletins based on document content.
  - **Table Parser**: Extract and structure data from tables within your documents.
  - **Image Parser**: Analyze and extract information from images embedded in your PDFs.
  - **RFQ (Request for Quotation)**: Manage and generate RFQs directly from your document content.
  - **More Add-Ons**: Easily integrate additional functionalities as per your requirements.

## Flexibility in Architecture

- **Plug-and-Play**: Easily add or remove components and features to customize the app according to your needs.
- **Cloud Native**: Designed for cloud deployment, ensuring scalability, reliability, and ease of management.

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

