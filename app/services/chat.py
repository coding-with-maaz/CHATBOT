"""Chat service combining database and Gemini"""

from typing import List, Optional, Dict
from datetime import datetime, timezone
from app.models.chat import ChatMessage, ConversationHistory, ConversationSummary
from app.utils.logger import get_logger
from app.utils.helpers import generate_conversation_id, get_utc_now

# Import here to avoid circular imports
from app.services.database import DatabaseService, get_database_service
from app.services.gemini import GeminiService, get_gemini_service
from app.services.openai_service import OpenAIService, get_openai_service
from app.config.settings import get_settings

logger = get_logger(__name__)


class ChatService:
    """Chat service for managing conversations"""
    
    def __init__(self, db_service: "DatabaseService", ai_service):
        self.db_service = db_service
        self.ai_service = ai_service  # Can be GeminiService or OpenAIService
        self.settings = get_settings()
        self.conversations_collection = None
    
    async def _get_collection(self):
        """Get conversations collection"""
        if self.conversations_collection is None:
            # Ensure database is connected before getting collection
            db = self.db_service.get_database()
            if db is None:
                logger.info("Database not connected, attempting to connect...")
                try:
                    await self.db_service.connect()
                    db = self.db_service.get_database()
                    if db is None:
                        raise RuntimeError("Database connection returned None")
                    logger.info("✅ Database connected successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to connect to database: {e}", exc_info=True)
                    raise
            
            try:
                self.conversations_collection = await self.db_service.get_collection("conversations")
                logger.debug(f"✅ Got conversations collection: {self.conversations_collection}")
            except Exception as e:
                logger.error(f"❌ Failed to get conversations collection: {e}", exc_info=True)
                raise
        
        return self.conversations_collection
    
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        chat_history: Optional[List[ChatMessage]] = None
    ) -> Dict:
        """
        Send a message and get AI response
        
        Args:
            message: User message
            conversation_id: Optional conversation ID
            chat_history: Optional chat history
        
        Returns:
            Dictionary with response and conversation details
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = generate_conversation_id()
        
        # Convert chat history to format expected by Gemini
        history = None
        if chat_history:
            history = [
                {"role": msg.role, "content": msg.content}
                for msg in chat_history
            ]
        
        # Generate response using AI service (OpenAI or Gemini)
        try:
            response_text = await self.ai_service.generate_response(message, history)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
        
        # Store conversation in database (always attempt to save)
        try:
            await self._store_message(conversation_id, message, response_text)
            logger.info(f"✅ Successfully saved conversation: {conversation_id}")
        except Exception as e:
            error_str = str(e)
            logger.error(f"❌ Failed to store conversation: {e}", exc_info=True)
            # Check if it's a connection issue
            if "SSL" in error_str or "connection" in error_str.lower() or "timeout" in error_str.lower():
                logger.warning(f"⚠️ Database connection issue - conversation not saved: {error_str}")
            # Continue even if storage fails, but log the error
            # In production, you might want to use a message queue or retry mechanism
        
        return {
            "response": response_text,
            "conversation_id": conversation_id,
            "timestamp": get_utc_now()
        }
    
    async def _store_message(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str
    ) -> None:
        """Store message in database"""
        try:
            # Ensure database is connected
            db = self.db_service.get_database()
            if db is None:
                logger.warning("Database not connected, attempting to reconnect...")
                try:
                    await self.db_service.connect()
                    db = self.db_service.get_database()
                except Exception as conn_error:
                    error_str = str(conn_error)
                    logger.error(f"❌ Cannot connect to database: {error_str}")
                    raise Exception(f"Database connection failed: {error_str}")
            
            if db is None:
                raise Exception("Database connection is None after connect attempt")
            
            collection = await self._get_collection()
            if collection is None:
                raise Exception("Failed to get collection from database")
            
            now = get_utc_now()
            
            message_doc = {
                "conversation_id": conversation_id,
                "user_message": user_message,
                "assistant_message": assistant_message,
                "timestamp": now,
                "created_at": now,
                "message_length": len(user_message) + len(assistant_message)
            }
            
            logger.debug(f"Attempting to insert message document: {message_doc}")
            result = await collection.insert_one(message_doc)
            
            if result.inserted_id:
                logger.info(f"✅ Successfully stored message (ID: {result.inserted_id}) for conversation: {conversation_id}")
            else:
                logger.warning(f"⚠️ Insert operation completed but no inserted_id returned for conversation: {conversation_id}")
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"❌ Error storing message to database: {error_str}", exc_info=True)
            # Re-raise to let caller know storage failed
            raise
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> ConversationHistory:
        """Get conversation history"""
        try:
            # Ensure database is connected
            db = self.db_service.get_database()
            if db is None:
                await self.db_service.connect()
            
            collection = await self._get_collection()
            cursor = collection.find(
                {"conversation_id": conversation_id}
            ).sort("timestamp", 1).limit(limit)
            
            messages = []
            created_at = None
            updated_at = None
            
            async for doc in cursor:
                if created_at is None:
                    created_at = doc.get("created_at")
                
                messages.append(ChatMessage(
                    role="user",
                    content=doc.get("user_message", ""),
                    timestamp=doc.get("timestamp")
                ))
                messages.append(ChatMessage(
                    role="assistant",
                    content=doc.get("assistant_message", ""),
                    timestamp=doc.get("timestamp")
                ))
                updated_at = doc.get("timestamp")
            
            return ConversationHistory(
                conversation_id=conversation_id,
                messages=messages,
                created_at=created_at,
                updated_at=updated_at,
                message_count=len(messages)
            )
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            raise
    
    async def get_conversation_summaries(
        self,
        limit: int = 20
    ) -> List[ConversationSummary]:
        """Get conversation summaries from database"""
        try:
            # Ensure database is connected
            db = self.db_service.get_database()
            if db is None:
                try:
                    await self.db_service.connect()
                    db = self.db_service.get_database()
                except Exception as conn_error:
                    logger.error(f"Failed to connect to database: {conn_error}")
                    return []  # Return empty list if can't connect
            
            if db is None:
                logger.warning("Database not available, returning empty conversations list")
                return []
            
            collection = await self._get_collection()
            
            # Check if collection has any documents
            count = await collection.count_documents({})
            if count == 0:
                logger.info("No conversations found in database")
                return []
            
            # Aggregate pipeline to get conversation summaries
            # Sort by timestamp first to get proper first/last messages
            pipeline = [
                {
                    "$sort": {"timestamp": 1}  # Sort ascending for chronological order
                },
                {
                    "$group": {
                        "_id": "$conversation_id",
                        "first_message": {"$first": "$user_message"},
                        "last_message": {"$last": "$user_message"},
                        "message_count": {"$sum": 1},
                        "created_at": {"$min": "$created_at"},
                        "updated_at": {"$max": "$timestamp"}
                    }
                },
                {
                    "$sort": {"updated_at": -1}  # Sort by most recent first
                },
                {
                    "$limit": limit
                }
            ]
            
            summaries = []
            async for doc in collection.aggregate(pipeline):
                # Ensure conversation_id is a string
                conv_id = str(doc["_id"]) if doc.get("_id") else None
                if not conv_id:
                    continue
                
                summaries.append(ConversationSummary(
                    conversation_id=conv_id,
                    first_message=doc.get("first_message"),
                    last_message=doc.get("last_message"),
                    message_count=doc.get("message_count", 0),
                    created_at=doc.get("created_at"),
                    updated_at=doc.get("updated_at")
                ))
            
            logger.info(f"✅ Retrieved {len(summaries)} conversation summaries from database")
            return summaries
            
        except Exception as e:
            error_str = str(e)
            # Check if it's a connection/SSL error
            if "SSL" in error_str or "connection" in error_str.lower() or "timeout" in error_str.lower():
                logger.warning(f"Database connection issue, returning empty list: {e}")
                return []  # Return empty list for connection issues
            else:
                logger.error(f"❌ Error retrieving conversation summaries: {e}", exc_info=True)
                # Return empty list instead of raising to allow UI to work
                return []
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        try:
            # Ensure database is connected
            db = self.db_service.get_database()
            if db is None:
                await self.db_service.connect()
            
            collection = await self._get_collection()
            result = await collection.delete_many({"conversation_id": conversation_id})
            logger.info(f"Deleted {result.deleted_count} messages for conversation: {conversation_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            raise


# Global instance
_chat_service: Optional[ChatService] = None


async def get_chat_service() -> ChatService:
    """Get chat service instance"""
    global _chat_service
    if _chat_service is None:
        db_service = await get_database_service()
        settings = get_settings()
        
        # Choose AI provider based on settings
        if settings.AI_PROVIDER.lower() == "openai":
            try:
                ai_service = get_openai_service()
                logger.info("Using OpenAI as AI provider")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}, falling back to Gemini")
                ai_service = get_gemini_service()
        else:
            try:
                ai_service = get_gemini_service()
                logger.info("Using Gemini as AI provider")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}, trying OpenAI")
                try:
                    ai_service = get_openai_service()
                    logger.info("Using OpenAI as fallback AI provider")
                except Exception as e2:
                    logger.error(f"Both AI providers failed: {e2}")
                    raise
        
        _chat_service = ChatService(db_service, ai_service)
    return _chat_service

