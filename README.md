# File to Vector DB System

A Python system that monitors a local folder, processes files, generates embeddings, and stores them in Supabase's vector database for semantic search capabilities.

## Features

- Monitor and process files from a local folder
- Support for PDF, DOCX, and TXT files
- Text chunking with overlap
- OpenAI embeddings generation
- Vector storage in Supabase (pgvector)
- Semantic search capabilities
- FastAPI backend with RESTful endpoints

## Project Structure

```
project/
├── folder/                 # Directory to place files for processing
├── app/
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration settings
│   ├── services/
│   │   ├── file_service.py # File processing logic
│   │   ├── embed_service.py # Embedding generation
│   │   └── db_service.py   # Database operations
│   ├── models/             # Data models
│   └── api/                # API endpoints
├── scripts/
│   └── setup_db.py         # Database setup script
└── requirements.txt        # Dependencies
```

## Prerequisites

- Python 3.8+
- Supabase account with pgvector extension enabled
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_api_key
FOLDER_PATH=./folder
EMBEDDING_MODEL=text-embedding-3-small
```

5. Set up the database:
```bash
python scripts/setup_db.py
```

## Usage

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Place files in the `folder` directory

3. Process files:
```bash
curl -X POST http://localhost:8000/api/v1/process
```

4. List processed files:
```bash
curl http://localhost:8000/api/v1/files
```

5. Search for content:
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "your search query", "limit": 5}'
```

## API Endpoints

- `POST /api/v1/process`: Process files in the folder
- `GET /api/v1/files`: List processed files
- `POST /api/v1/search`: Search with a text query

## Configuration

The system can be configured through environment variables:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `FOLDER_PATH`: Path to the folder containing files to process
- `EMBEDDING_MODEL`: OpenAI embedding model to use

## License

MIT 