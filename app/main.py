from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
from app.config import settings

app = FastAPI(
    title="File to Vector DB System",
    description="A system that processes files, generates embeddings, and stores them in a vector database for semantic search",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "File to Vector DB System",
        "version": "1.0.0",
        "docs_url": "/docs"
    } 