"""Test script for chatbot API"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_chat():
    """Test the chat endpoint"""
    print("Testing Chatbot API...")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        r = requests.get(f"{API_BASE}/health")
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: AI Info
    print("\n2. Testing AI info endpoint...")
    try:
        r = requests.get(f"{API_BASE}/ai/info")
        print(f"   Status: {r.status_code}")
        data = r.json()
        print(f"   Model: {data.get('data', {}).get('model_name', 'N/A')}")
        print(f"   Status: {data.get('data', {}).get('status', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Send chat message
    print("\n3. Testing chat endpoint...")
    try:
        payload = {
            "message": "Hello! Please say 'Hi, I am working!' if you can hear me."
        }
        r = requests.post(f"{API_BASE}/chat", json=payload)
        print(f"   Status: {r.status_code}")
        data = r.json()
        
        if r.status_code == 200:
            print(f"   ✅ Success!")
            print(f"   Response: {data.get('response', 'N/A')[:200]}")
            print(f"   Conversation ID: {data.get('conversation_id', 'N/A')}")
        else:
            print(f"   ❌ Error: {data.get('message', 'Unknown error')}")
            print(f"   Full error: {json.dumps(data, indent=2)[:500]}")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_chat()

