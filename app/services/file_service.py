import os
from pathlib import Path
import hashlib
from typing import List, Tuple
import PyPDF2
from docx import Document
import magic
from app.config import settings
from app.models.models import FileMetadata, TextChunk
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        logger.info("Initializing FileService")
        self.folder_path = settings.folder_path
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.mime = magic.Magic(mime=True)
    
    def get_file_checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        logger.info(f"Calculating checksum for file: {file_path}")
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.md5()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
            checksum = file_hash.hexdigest()
            logger.info(f"Checksum calculated: {checksum}")
            return checksum
        except Exception as e:
            logger.error(f"Error calculating checksum: {str(e)}", exc_info=True)
            raise
    
    def get_file_type(self, file_path: Path) -> str:
        """Get file type using python-magic"""
        return self.mime.from_file(str(file_path))
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text based on file type"""
        file_type = self.get_file_type(file_path)
        if file_type == 'application/pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return self.extract_text_from_docx(file_path)
        elif file_type == 'text/plain':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _split_text(self, text: str) -> List[TextChunk]:
        """Split text into chunks"""
        logger.info("Starting text chunking process")
        try:
            chunks = []
            words = text.split()
            current_chunk = []
            current_size = 0
            now = datetime.now()
            
            logger.info(f"Total words to process: {len(words)}")
            
            for i, word in enumerate(words):
                current_chunk.append(word)
                current_size += len(word) + 1  # +1 for space
                
                if current_size >= 1000:  # chunk size
                    chunk_text = " ".join(current_chunk)
                    logger.info(f"Created chunk {len(chunks)} with {len(chunk_text)} characters")
                    chunks.append(TextChunk(
                        file_id="",  # Will be set after file metadata is stored
                        chunk_text=chunk_text,
                        chunk_index=len(chunks),
                        created_at=now
                    ))
                    current_chunk = []
                    current_size = 0
                
                # Log progress every 1000 words
                if i % 1000 == 0:
                    logger.info(f"Processed {i} words out of {len(words)}")
            
            # Add the last chunk if it's not empty
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                logger.info(f"Created final chunk {len(chunks)} with {len(chunk_text)} characters")
                chunks.append(TextChunk(
                    file_id="",  # Will be set after file metadata is stored
                    chunk_text=chunk_text,
                    chunk_index=len(chunks),
                    created_at=now
                ))
            
            logger.info(f"Completed chunking process. Created {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error in text chunking: {str(e)}", exc_info=True)
            raise
    
    def process_file(self, file_path: Path) -> Tuple[FileMetadata, List[TextChunk]]:
        """Process a file and extract text chunks"""
        logger.info(f"Processing file: {file_path}")
        try:
            # Get file metadata
            file_size = os.path.getsize(file_path)
            checksum = self.get_file_checksum(file_path)
            file_type = self.get_file_type(file_path)
            now = datetime.now()
            
            file_metadata = FileMetadata(
                filename=file_path.name,
                file_path=str(file_path),
                file_type=file_type,
                file_size=file_size,
                checksum=checksum,
                created_at=now,
                updated_at=now
            )
            logger.info(f"File metadata created: {file_metadata}")

            # Extract text based on file type
            text = self.extract_text(file_path)
            logger.info(f"Extracted text from file, length: {len(text)}")

            # Split text into chunks
            chunks = self._split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks")

            # Create text chunks
            text_chunks = []
            for i, chunk in enumerate(chunks):
                text_chunks.append(TextChunk(
                    file_id="",  # Will be set after file metadata is stored
                    chunk_text=chunk.chunk_text,  # Use the chunk_text from the TextChunk object
                    chunk_index=i,
                    created_at=now
                ))
            
            return file_metadata, text_chunks
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            raise
    
    def scan_folder(self) -> List[Path]:
        """Scan the folder for files to process"""
        logger.info("Scanning folder for files")
        try:
            folder_path = Path("folder")
            if not folder_path.exists():
                logger.error(f"Folder path does not exist: {folder_path}")
                raise FileNotFoundError(f"Folder path does not exist: {folder_path}")
            
            files = list(folder_path.glob("*"))
            logger.info(f"Found {len(files)} files in folder")
            return files
        except Exception as e:
            logger.error(f"Error scanning folder: {str(e)}", exc_info=True)
            raise 