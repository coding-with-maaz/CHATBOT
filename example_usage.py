"""
Example usage of the Chatbot API
This file demonstrates how to interact with the API programmatically
"""

import asyncio
import aiohttp
import json


async def test_chat_api():
    """Test the chat API endpoints"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # 1. Health check
        print("1. Checking health...")
        async with session.get(f"{base_url}/api/health") as response:
            health = await response.json()
            print(f"   Health: {json.dumps(health, indent=2)}")
        
        # 2. Send a chat message
        print("\n2. Sending chat message...")
        chat_data = {
            "message": "Hello! What is Python?",
            "conversation_id": None  # Will be auto-generated
        }
        async with session.post(
            f"{base_url}/api/chat",
            json=chat_data
        ) as response:
            chat_response = await response.json()
            conversation_id = chat_response.get("data", {}).get("conversation_id")
            print(f"   Response: {chat_response.get('data', {}).get('response', '')[:100]}...")
            print(f"   Conversation ID: {conversation_id}")
        
        # 3. Get conversation history
        if conversation_id:
            print(f"\n3. Getting conversation history for {conversation_id}...")
            async with session.get(
                f"{base_url}/api/chat/history/{conversation_id}"
            ) as response:
                history = await response.json()
                print(f"   Messages: {history.get('data', {}).get('message_count', 0)}")
        
        # 4. Get AI info
        print("\n4. Getting AI model info...")
        async with session.get(f"{base_url}/api/ai/info") as response:
            ai_info = await response.json()
            print(f"   Model: {ai_info.get('data', {}).get('model_name', 'N/A')}")
        
        # 5. List conversations
        print("\n5. Listing conversations...")
        async with session.get(f"{base_url}/api/chat/conversations?limit=5") as response:
            conversations = await response.json()
            print(f"   Found {len(conversations.get('data', []))} conversations")


if __name__ == "__main__":
    print("Testing Chatbot API...")
    print("Make sure the server is running on http://localhost:8000\n")
    asyncio.run(test_chat_api())

