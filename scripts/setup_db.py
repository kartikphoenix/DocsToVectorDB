from supabase import create_client
from app.config import settings
import os

def setup_database():
    # Initialize Supabase client
    supabase = create_client(settings.supabase_url, settings.supabase_key)
    
    # Enable pgvector extension
    supabase.rpc('create_extension', {'extension_name': 'vector'}).execute()
    
    # Create files table
    supabase.rpc('create_table', {
        'table_name': 'files',
        'columns': [
            {'name': 'id', 'type': 'uuid', 'primary_key': True},
            {'name': 'filename', 'type': 'text', 'not_null': True},
            {'name': 'file_path', 'type': 'text', 'not_null': True},
            {'name': 'file_type', 'type': 'text', 'not_null': True},
            {'name': 'file_size', 'type': 'integer', 'not_null': True},
            {'name': 'checksum', 'type': 'text', 'not_null': True},
            {'name': 'created_at', 'type': 'timestamp', 'not_null': True},
            {'name': 'updated_at', 'type': 'timestamp', 'not_null': True}
        ]
    }).execute()
    
    # Create chunks table
    supabase.rpc('create_table', {
        'table_name': 'chunks',
        'columns': [
            {'name': 'id', 'type': 'uuid', 'primary_key': True},
            {'name': 'file_id', 'type': 'uuid', 'not_null': True},
            {'name': 'chunk_text', 'type': 'text', 'not_null': True},
            {'name': 'chunk_index', 'type': 'integer', 'not_null': True},
            {'name': 'created_at', 'type': 'timestamp', 'not_null': True}
        ],
        'foreign_keys': [
            {'column': 'file_id', 'references': 'files(id)', 'on_delete': 'CASCADE'}
        ]
    }).execute()
    
    # Create embeddings table
    supabase.rpc('create_table', {
        'table_name': 'embeddings',
        'columns': [
            {'name': 'id', 'type': 'uuid', 'primary_key': True},
            {'name': 'chunk_id', 'type': 'uuid', 'not_null': True},
            {'name': 'embedding', 'type': 'vector(1536)', 'not_null': True},
            {'name': 'created_at', 'type': 'timestamp', 'not_null': True}
        ],
        'foreign_keys': [
            {'column': 'chunk_id', 'references': 'chunks(id)', 'on_delete': 'CASCADE'}
        ]
    }).execute()
    
    # Create function for similarity search
    supabase.rpc('create_function', {
        'function_name': 'match_chunks',
        'parameters': [
            {'name': 'query_embedding', 'type': 'vector(1536)'},
            {'name': 'match_threshold', 'type': 'float'},
            {'name': 'match_count', 'type': 'integer'}
        ],
        'returns': 'table',
        'body': '''
            SELECT 
                c.chunk_text,
                f.filename,
                1 - (e.embedding <=> query_embedding) as similarity
            FROM embeddings e
            JOIN chunks c ON c.id = e.chunk_id
            JOIN files f ON f.id = c.file_id
            WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
            ORDER BY similarity DESC
            LIMIT match_count;
        '''
    }).execute()

if __name__ == "__main__":
    setup_database()
    print("Database setup completed successfully!") 