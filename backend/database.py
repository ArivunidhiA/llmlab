"""Database connection and session management."""

from supabase import create_client, Client
from config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """Supabase database wrapper."""
    
    _client: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client."""
        if cls._client is None:
            try:
                cls._client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("Connected to Supabase")
            except Exception as e:
                logger.error(f"Failed to connect to Supabase: {e}")
                raise
        return cls._client
    
    @classmethod
    async def test_connection(cls) -> bool:
        """Test database connection."""
        try:
            client = cls.get_client()
            # Test with a simple health check query
            result = client.table("users").select("COUNT(*)").execute()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Dependency for FastAPI
async def get_db() -> Client:
    """FastAPI dependency to get database client."""
    return Database.get_client()
