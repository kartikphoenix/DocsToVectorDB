from fastapi import APIRouter, HTTPException
from app.services.file_service import FileService
from app.services.embed_service import EmbeddingService
from app.services.db_service import DatabaseService
from app.models.models import SearchQuery, SearchResult
from typing import List
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
file_service = FileService()
embed_service = EmbeddingService()
db_service = DatabaseService()

@router.post("/process")
async def process_files():
    """Process all files in the folder"""
    logger.info("Starting file processing")
    try:
        # Scan folder for files
        files = file_service.scan_folder()
        logger.info(f"Found {len(files)} files to process")
        
        for file_path in files:
            if file_path.is_file():
                try:
                    logger.info(f"Processing file: {file_path}")
                    # Process file and get metadata and chunks
                    file_metadata, chunks = file_service.process_file(file_path)
                    logger.info(f"File processed successfully. Metadata: {file_metadata}")
                    logger.info(f"Generated {len(chunks)} text chunks")
                    
                    # Store file metadata
                    file_id = db_service.store_file_metadata(file_metadata)
                    logger.info(f"Stored file metadata with ID: {file_id}")
                    
                    # Process each chunk
                    for chunk in chunks:
                        try:
                            # Update chunk with file_id
                            chunk.file_id = file_id
                            
                            # Store text chunk
                            chunk_id = await db_service.store_text_chunk(chunk)
                            logger.info(f"Stored text chunk with ID: {chunk_id}")
                            
                            # Generate embedding
                            embedding = embed_service.get_embedding(chunk.chunk_text)
                            logger.info(f"Generated embedding for chunk {chunk_id}")
                            
                            # Store embedding
                            await db_service.store_embedding(chunk_id, embedding)
                            logger.info(f"Stored embedding for chunk {chunk_id}")
                            
                        except Exception as e:
                            logger.error(f"Error processing chunk: {str(e)}", exc_info=True)
                            continue
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}", exc_info=True)
                    continue
            
            else:
                logger.warning(f"Skipping non-file entry: {file_path}")
        
        return {"message": "File processing completed"}
        
    except Exception as e:
        logger.error(f"Error in process_files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_files():
    """List all processed files"""
    try:
        logger.info("Fetching list of processed files")
        result = db_service.supabase.table("files").select("*").execute()
        logger.info(f"Found {len(result.data)} files")
        return result.data
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search(query: SearchQuery):
    """Search for content using natural language and return all chunks from relevant files"""
    logger.info(f"Processing search query: {query.query}")
    try:
        # Search for similar chunks
        results = await db_service.search_similar(query.query, query.limit)
        logger.info(f"Found {len(results)} similar chunks")
        
        # Get unique file IDs from results
        file_ids = set(result["file_id"] for result in results)
        logger.info(f"Found {len(file_ids)} relevant files")
        
        # Format results
        formatted_results = []
        for file_id in file_ids:
            # Get file metadata
            file = db_service.get_file_by_id(file_id)
            if not file:
                continue
                
            # Get all chunks for this file
            chunks = db_service.get_chunks_by_file_id(file_id)
            
            # Find the matching chunks for this file
            matching_chunks = [r for r in results if r["file_id"] == file_id]
            
            # Combine all chunks in order
            all_chunks = []
            for chunk in chunks:
                # Check if this chunk was a match
                matching_chunk = next((m for m in matching_chunks if m["id"] == chunk["id"]), None)
                similarity = matching_chunk["similarity"] if matching_chunk else None
                
                all_chunks.append({
                    "text": chunk["chunk_text"],
                    "similarity": similarity,
                    "chunk_index": chunk["chunk_index"]
                })
            
            formatted_results.append({
                "filename": file["filename"],
                "chunks": all_chunks
            })
        
        return {"results": formatted_results}
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 