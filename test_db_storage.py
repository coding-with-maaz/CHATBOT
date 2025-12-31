"""Test script to verify database storage"""

import asyncio
import sys
from app.services.database import get_database_service
from app.services.chat import get_chat_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def test_database_storage():
    """Test if conversations are being saved to database"""
    
    print("=" * 60)
    print("Testing Database Storage")
    print("=" * 60)
    
    # Test 1: Database connection
    print("\n1. Testing database connection...")
    try:
        db_service = await get_database_service()
        health = await db_service.health_check()
        print(f"   ✅ Database health: {health}")
        
        if not health:
            print("   ❌ Database is not healthy!")
            return False
            
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False
    
    # Test 2: Send a message and check if it's saved
    print("\n2. Sending a test message...")
    try:
        chat_service = await get_chat_service()
        result = await chat_service.send_message("Test message for database storage")
        conv_id = result.get("conversation_id")
        print(f"   ✅ Message sent, conversation_id: {conv_id}")
        
        # Wait a moment for storage
        await asyncio.sleep(1)
        
    except Exception as e:
        print(f"   ❌ Failed to send message: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Check if conversation was saved
    print("\n3. Checking if conversation was saved...")
    try:
        collection = await db_service.get_collection("conversations")
        count = await collection.count_documents({"conversation_id": conv_id})
        print(f"   Found {count} messages for conversation {conv_id}")
        
        if count > 0:
            print("   ✅ Conversation was saved successfully!")
            
            # Show the saved message
            async for doc in collection.find({"conversation_id": conv_id}).limit(1):
                print(f"\n   Saved message:")
                print(f"   - User: {doc.get('user_message', 'N/A')[:50]}")
                print(f"   - AI: {doc.get('assistant_message', 'N/A')[:50]}")
                print(f"   - Timestamp: {doc.get('timestamp')}")
            return True
        else:
            print("   ❌ Conversation was NOT saved!")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to check storage: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Check all conversations
    print("\n4. Checking all conversations...")
    try:
        collection = await db_service.get_collection("conversations")
        total_count = await collection.count_documents({})
        print(f"   Total messages in database: {total_count}")
        
        # Get unique conversations
        pipeline = [
            {"$group": {"_id": "$conversation_id"}},
            {"$count": "total"}
        ]
        async for doc in collection.aggregate(pipeline):
            print(f"   Unique conversations: {doc.get('total', 0)}")
            
    except Exception as e:
        print(f"   ❌ Failed to check conversations: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        result = asyncio.run(test_database_storage())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

