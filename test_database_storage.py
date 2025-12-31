"""Test script to verify conversations are being saved to MongoDB"""

import asyncio
from app.services.database import get_database_service
from app.services.chat import get_chat_service
from app.models.chat import ChatMessage

async def test_conversation_storage():
    """Test that conversations are saved to database"""
    print("Testing Conversation Storage...")
    print("=" * 50)
    
    try:
        # Get services
        db_service = await get_database_service()
        chat_service = await get_chat_service()
        
        # Test 1: Check database connection
        print("\n1. Checking database connection...")
        db_healthy = await db_service.health_check()
        print(f"   Database healthy: {db_healthy}")
        
        if not db_healthy:
            print("   ❌ Database not connected!")
            return
        
        # Test 2: Send a test message
        print("\n2. Sending test message...")
        test_message = "Test message to verify database storage"
        result = await chat_service.send_message(test_message)
        
        conversation_id = result["conversation_id"]
        print(f"   ✅ Message sent")
        print(f"   Conversation ID: {conversation_id}")
        print(f"   Response preview: {result['response'][:100]}...")
        
        # Test 3: Verify message was saved
        print("\n3. Verifying message was saved to database...")
        db = db_service.get_database()
        collection = db["conversations"]
        
        # Count messages for this conversation
        count = await collection.count_documents({"conversation_id": conversation_id})
        print(f"   Messages found in DB: {count}")
        
        if count > 0:
            # Get the saved message
            saved_msg = await collection.find_one({"conversation_id": conversation_id})
            print(f"   ✅ Message successfully saved!")
            print(f"   User message: {saved_msg.get('user_message', 'N/A')[:50]}...")
            print(f"   Assistant message: {saved_msg.get('assistant_message', 'N/A')[:50]}...")
            print(f"   Timestamp: {saved_msg.get('timestamp', 'N/A')}")
        else:
            print(f"   ❌ Message NOT found in database!")
        
        # Test 4: Retrieve conversation history
        print("\n4. Testing conversation history retrieval...")
        history = await chat_service.get_conversation_history(conversation_id)
        print(f"   ✅ History retrieved")
        print(f"   Total messages: {history.message_count}")
        print(f"   Messages in history: {len(history.messages)}")
        
        # Test 5: List all conversations
        print("\n5. Testing conversation listing...")
        summaries = await chat_service.get_conversation_summaries(limit=5)
        print(f"   ✅ Found {len(summaries)} conversations")
        for summary in summaries[:3]:
            print(f"   - {summary.conversation_id}: {summary.message_count} messages")
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_conversation_storage())

