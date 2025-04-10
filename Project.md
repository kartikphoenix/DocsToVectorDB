# File to Vector DB System Overview

## 1. Project Overview
- This is a File to Vector DB System that converts documents into searchable vector embeddings
- Key purpose: Enable semantic search across documents by converting them into vector representations
- Built with Python, FastAPI, OpenAI embeddings, and Supabase (with pgvector)

## 2. Core Features
- **File Processing**: Supports PDF, DOCX, and TXT files
- **Automatic Monitoring**: Watches a local folder for new files
- **Text Processing**: Chunks text with overlap for better context preservation
- **Vector Embeddings**: Uses OpenAI's text-embedding-3-small model
- **Vector Storage**: Utilizes Supabase's pgvector for efficient vector storage
- **REST API**: Provides easy-to-use endpoints for processing and searching

## 3. Technical Architecture
```
project/
├── folder/                 # Monitored directory for files
├── app/
│   ├── main.py            # FastAPI application entry point
│   ├── services/          # Core business logic
│   │   ├── file_service.py    # File processing
│   │   ├── embed_service.py   # Embedding generation
│   │   └── db_service.py      # Database operations
│   └── api/               # API endpoints
```

## 4. Key Components
- **FastAPI Backend**: Modern, high-performance API framework
- **OpenAI Integration**: For generating text embeddings
- **Supabase Vector DB**: For storing and querying vectors
- **File Processing Pipeline**: Converts documents → text → chunks → embeddings → vector storage

## 5. API Endpoints
- `POST /api/v1/process`: Processes files in the monitored folder
- `GET /api/v1/files`: Lists all processed files
- `POST /api/v1/search`: Performs semantic search queries

## 6. Setup and Configuration
- **Environment Variables**: Supabase, OpenAI credentials, and folder configurations
- **Simple Installation**: Python virtual environment and pip requirements
- **Database Setup**: Automated setup script included

## 7. Demo Flow Suggestion
1. Show the folder structure and file placement
2. Demonstrate file processing
3. Show the vector storage in Supabase
4. Perform example semantic searches
5. Highlight the API documentation at `/docs`

## 8. Technical Requirements
- Python 3.8+
- Supabase account with pgvector
- OpenAI API key
- Local storage for file processing

## 9. Future Potential/Extensions
- Additional file format support
- Real-time file processing
- Advanced search features
- User interface development
- Batch processing capabilities