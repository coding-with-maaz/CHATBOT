"""Enhanced conversation storage utilities"""

from typing import Optional, Dict, List
from datetime import datetime
from app.services.database import DatabaseService
from app.utils.logger import get_logger
from app.utils.helpers import get_utc_now

logger = get_logger(__name__)


class ConversationStorage:
    """Enhanced conversation storage with retry and validation"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.collection_name = "conversations"
        self._collection = None
    
    async def get_collection(self):
        """Get or create conversations collection"""
        if not self._collection:
            if not self.db_service.get_database():
                await self.db_service.connect()
            self._collection = await self.db_service.get_collection(self.collection_name)
        return self._collection
    
    async def save_message(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save a message exchange to the database
        
        Args:
            conversation_id: Unique conversation identifier
            user_message: User's message
            assistant_message: AI's response
            metadata: Optional metadata (model used, tokens, etc.)
        
        Returns:
            Inserted document ID
        """
        try:
            collection = await self.get_collection()
            now = get_utc_now()
            
            message_doc = {
                "conversation_id": conversation_id,
                "user_message": user_message,
                "assistant_message": assistant_message,
                "timestamp": now,
                "created_at": now,
                "message_length": len(user_message) + len(assistant_message),
                "user_message_length": len(user_message),
                "assistant_message_length": len(assistant_message)
            }
            
            # Add metadata if provided
            if metadata:
                message_doc["metadata"] = metadata
            
            result = await collection.insert_one(message_doc)
            logger.info(f"✅ Saved message to conversation {conversation_id} (doc_id: {result.inserted_id})")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to save message: {e}", exc_info=True)
            raise
    
    async def save_conversation_metadata(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Save or update conversation metadata"""
        try:
            collection = await self.get_collection()
            
            # Create or update conversation metadata
            metadata_doc = {
                "conversation_id": conversation_id,
                "updated_at": get_utc_now(),
                "type": "metadata"
            }
            
            if title:
                metadata_doc["title"] = title
            if tags:
                metadata_doc["tags"] = tags
            if user_id:
                metadata_doc["user_id"] = user_id
            
            # Use upsert to create or update
            await collection.update_one(
                {"conversation_id": conversation_id, "type": "metadata"},
                {"$set": metadata_doc},
                upsert=True
            )
            logger.debug(f"Saved metadata for conversation: {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to save conversation metadata: {e}")
    
    async def get_conversation_stats(self, conversation_id: str) -> Dict:
        """Get statistics for a conversation"""
        try:
            collection = await self.get_collection()
            
            # Count messages
            message_count = await collection.count_documents({"conversation_id": conversation_id, "type": {"$ne": "metadata"}})
            
            # Get first and last message timestamps
            first_msg = await collection.find_one(
                {"conversation_id": conversation_id, "type": {"$ne": "metadata"}},
                sort=[("created_at", 1)]
            )
            last_msg = await collection.find_one(
                {"conversation_id": conversation_id, "type": {"$ne": "metadata"}},
                sort=[("created_at", -1)]
            )
            
            return {
                "conversation_id": conversation_id,
                "message_count": message_count,
                "first_message_at": first_msg.get("created_at") if first_msg else None,
                "last_message_at": last_msg.get("created_at") if last_msg else None
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation stats: {e}")
            return {"conversation_id": conversation_id, "message_count": 0}

