### Architecture

The system uses RAG (Retrieval Augmented Generation) for question answering.

Two main workflows:
1. **Data Ingestion Workflow**: Loads context documents and creates a vector database
2. **Chat Workflow**: Processes user queries and generates responses

## Prerequisites

- Python 3.8 or higher
- GPU (required for execution)
- pip (Python package manager)
- Git

### GPU Options
If you don't have a local GPU, you can use:
- Cloud Provider (AWS, GCP, etc.)
- On-Demand GPU Cloud (vast.ai, RunPod, etc.)
- Cloud GPU IDE (e.g., Lightning Studio)

## Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Download Documentation**
   ```bash
   # Download Hyperledger Fabric documentation
   wget -r -A.html -P rtdocs https://hyperledger-fabric.readthedocs.io/en/release-2.5/
   
   # After 1-2 minutes press ctrl+c as it starts downloading previous versions
   
   # Process the downloaded files
   cd rtdocs
   tar -czvf readthedocs.tar.gz release-2.5/
   mv readthedocs.tar.gz ..
   cd ..
   rm -rf hyperledger-fabric.readthedocs.io
   tar -xzvf readthedocs.tar.gz
   rm readthedocs.tar.gz
   
   # Verify the documentation is in place
   ls -la rtdocs/hyperledger-fabric.readthedocs.io/en/release-2.5
   ```

3. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/MacOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   Create a `.env` file in the `app` directory with the following variables:
   ```env
   # API Configuration
   HOST=0.0.0.0
   PORT=8000
   DEBUG=True

   # Google API Configuration
   GOOGLE_API_KEY=your_google_api_key

   # Agent Configuration
   GEMINI_MODEL=gemini-2.0-flash
   QUERY_AGENT_MODEL=gemini-2.0-flash
   QUERY_AGENT_MAX_TOKENS=150
   QUERY_AGENT_TEMPERATURE=0.7
   RETRIEVAL_AGENT_MODEL=all-MiniLM-L6-v2
   RETRIEVAL_AGENT_TOP_K=3
   RESPONSE_AGENT_MODEL=gemini-2.0-flash
   RESPONSE_AGENT_MAX_TOKENS=500
   RESPONSE_AGENT_TEMPERATURE=0.7
   ```

6. **Process Documentation**
   ```bash
   # Navigate to the scripts directory
   cd app/scripts

   # Process the documentation (use absolute path)
   python ingest_docs.py /absolute/path/to/rtdocs/hyperledger-fabric.readthedocs.io/en/release-2.5

   # Verify the processed documents
   ls -la processed_docs.json
   cat processed_docs.json | head -n 20
   ```

7. **Start the server**
   ```bash
   # From the project root directory (where app folder is located)
   cd /path/to/project/root
   
   # Start the server using the module path
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   For Windows PowerShell:
   ```powershell
   # From the project root directory (where app folder is located)
   cd /path/to/project/root
   
   # Start the server using the module path
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Usage

1. **First, load the documentation**
   ```bash
   # Navigate to the scripts directory where processed_docs.json is located
   cd app/scripts

   # Load processed RTDocs documentation from the JSON file
   curl --header "Content-Type: application/json" \
        --request POST \
        --data @processed_docs.json \
        http://127.0.0.1:8000/documents

   # Verify the documents were loaded
   curl http://127.0.0.1:8000/status
   ```

2. **Then, query the system**
   ```bash
   # Example query about Hyperledger Fabric installation
   curl --header "Content-Type: application/json" \
        --request POST \
        --data '{"id": "123", "content": "How to install Hyperledger fabric?"}' \
        http://127.0.0.1:8000/query
   ```

3. **If needed, clear and reload documents**
   ```bash
   # Clear existing documents
   curl --request DELETE http://127.0.0.1:8000/documents

   # Verify documents are cleared (total_documents should be 0)
   curl http://127.0.0.1:8000/status

   # Reload documents
   curl --header "Content-Type: application/json" \
        --request POST \
        --data @processed_docs.json \
        http://127.0.0.1:8000/documents

   # Verify documents are reloaded
   curl http://127.0.0.1:8000/status
   ```

The API expects requests in the following format:
- `id`: A unique identifier for the query
- `content`: The actual question text

Common responses:
- Success: `{"id": "123", "message": {"content": "Answer here...", "type": 1, "id": "uuid"}}`
- No context: `{"id": "123", "message": {"content": "I am sorry, but I cannot answer the query as there is no context provided.", "type": 1, "id": "uuid"}}`
- Error: `{"detail": "Error message"}`

## Project Structure

```
app/
├── api/            # API endpoints and routes
│   ├── __init__.py
│   └── endpoints.py
├── agents/         # AI agent implementations
│   ├── __init__.py
│   ├── base_agent.py
│   ├── query_agent.py
│   ├── retrieval_agent.py
│   └── response_agent.py
├── core/           # Core application logic
│   ├── __init__.py
│   └── orchestrator.py
├── scripts/        # Utility scripts
│   └── ingest_docs.py
├── __init__.py     # Package initialization
├── config.py       # Configuration settings
├── main.py         # Application entry point
└── requirements.txt # Project dependencies
```
