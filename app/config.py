from pydantic_settings import BaseSettings
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Supabase Configuration
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # File Processing Configuration
    folder_path: Path = Path(os.getenv("FOLDER_PATH", "./folder"))
    chunk_size: int = 10000
    chunk_overlap: int = 200
    
    class Config:
        env_file = ".env"

settings = Settings() 