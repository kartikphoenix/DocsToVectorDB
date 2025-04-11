from supabase import create_client, Client
from app.config import settings
from app.models.models import FileMetadata, TextChunk, Embedding
from typing import List, Optional, Dict
import hashlib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        logger.info("Initializing DatabaseService")
        try:
            self.supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
            logger.info("Successfully connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}", exc_info=True)
            raise
    
    def store_file_metadata(self, file_metadata: FileMetadata) -> str:
        """Store file metadata and return the file ID"""
        logger.info(f"Storing file metadata: {file_metadata}")
        try:
            data = {
                "filename": file_metadata.filename,
                "file_path": file_metadata.file_path,
                "file_type": file_metadata.file_type,
                "file_size": file_metadata.file_size,
                "checksum": file_metadata.checksum,
                "created_at": file_metadata.created_at.isoformat(),
                "updated_at": file_metadata.updated_at.isoformat()
            }
            result = self.supabase.table("files").insert(data).execute()
            logger.info(f"File metadata stored successfully: {result.data}")
            return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Error storing file metadata: {str(e)}", exc_info=True)
            raise
    
    async def store_text_chunk(self, chunk: TextChunk) -> str:
        """Store a text chunk in the database"""
        logger.info(f"Storing text chunk for file_id: {chunk.file_id}")
        try:
            data = {
                "file_id": chunk.file_id,
                "chunk_text": chunk.chunk_text,
                "chunk_index": chunk.chunk_index,
                "created_at": chunk.created_at.isoformat()
            }
            result = self.supabase.table("text_chunks").insert(data).execute()
            logger.info("Text chunk stored successfully")
            return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Error storing text chunk: {str(e)}", exc_info=True)
            raise
    
    async def store_embedding(self, chunk_id: int, embedding: List[float]) -> None:
        """Store an embedding in the database"""
        logger.info(f"Storing embedding for chunk {chunk_id}")
        try:
            logger.info("Generating embedding...")
            embedding_data = {
                "chunk_id": chunk_id,
                "embedding": embedding
            }
            logger.info(f"Embedding data prepared: {embedding_data}")
            
            result = self.supabase.table("embeddings").insert(embedding_data).execute()
            logger.info(f"Embedding stored successfully: {result}")
        except Exception as e:
            logger.error(f"Error storing embedding: {str(e)}", exc_info=True)
            raise
    
    async def search_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar text chunks using embeddings"""
        logger.info(f"Searching for similar chunks to query: {query[:50]}...")
        try:
            # Generate embedding for the query using embed_service
            logger.info("Generating query embedding...")
            from app.services.embed_service import EmbeddingService
            embed_service = EmbeddingService()
            query_embedding = embed_service.get_embedding(query)
            logger.info("Query embedding generated")
            
            # Search for similar chunks
            logger.info("Searching in database...")
            result = self.supabase.rpc(
                "match_chunks",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.1,
                    "match_count": limit
                }
            ).execute()
            
            logger.info(f"Found {len(result.data)} similar chunks")
            return result.data
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}", exc_info=True)
            raise
    
    def get_file_by_checksum(self, checksum: str) -> Optional[dict]:
        """Get file metadata by checksum"""
        logger.info(f"Looking up file by checksum: {checksum}")
        try:
            result = self.supabase.table("files").select("*").eq("checksum", checksum).execute()
            logger.info(f"File lookup result: {result.data}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error looking up file by checksum: {str(e)}", exc_info=True)
            raise
    
    def get_file_by_id(self, file_id: str) -> Optional[dict]:
        """Get file metadata by ID"""
        logger.info(f"Getting file metadata for ID: {file_id}")
        try:
            result = self.supabase.table("files").select("*").eq("id", file_id).execute()
            if result.data:
                logger.info(f"Found file metadata: {result.data[0]}")
                return result.data[0]
            else:
                logger.warning(f"No file found with ID: {file_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting file by ID: {str(e)}", exc_info=True)
            raise
    
    def get_chunks_by_file_id(self, file_id: str) -> List[Dict]:
        """Get all text chunks for a file"""
        logger.info(f"Getting all chunks for file ID: {file_id}")
        try:
            result = self.supabase.table("text_chunks").select("*").eq("file_id", file_id).order("chunk_index").execute()
            logger.info(f"Found {len(result.data)} chunks for file {file_id}")
            return result.data
        except Exception as e:
            logger.error(f"Error getting chunks by file ID: {str(e)}", exc_info=True)
            raise 