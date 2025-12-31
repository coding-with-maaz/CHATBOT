"""Database service for MongoDB operations"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseService:
    """MongoDB database service"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.settings = get_settings()
    
    async def connect(self) -> AsyncIOMotorDatabase:
        """Connect to MongoDB"""
        if self.database is not None:
            return self.database
        
        try:
            mongo_uri = self.settings.get_mongo_uri()
            logger.info(f"Connecting to MongoDB: {mongo_uri.split('@')[0]}@***")
            
            # Configure MongoDB client with SSL/TLS settings
            self.client = AsyncIOMotorClient(
                mongo_uri,
                serverSelectionTimeoutMS=30000,  # Increased timeout
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                tls=True,  # Explicitly enable TLS for Atlas
                tlsAllowInvalidCertificates=False,  # Don't allow invalid certs
                retryWrites=True,
                w="majority"
            )
            
            # Test connection
            await self.client.admin.command('ping')
            self.database = self.client[self.settings.MONGO_DB_NAME]
            
            logger.info(f"✅ Connected to MongoDB: {self.settings.MONGO_DB_NAME}")
            return self.database
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            logger.info("✅ MongoDB connection closed")
    
    def get_database(self) -> Optional[AsyncIOMotorDatabase]:
        """Get database instance"""
        return self.database
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            if self.database is None:
                return False
            await self.database.command('ping')
            return True
        except Exception:
            return False
    
    async def get_collection(self, name: str):
        """Get a collection from the database"""
        if self.database is None:
            raise RuntimeError("Database not connected")
        return self.database[name]


# Global instance
_db_service: Optional[DatabaseService] = None


async def get_database_service() -> DatabaseService:
    """Get database service instance"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
        await _db_service.connect()
    return _db_service

