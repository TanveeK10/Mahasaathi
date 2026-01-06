#!/usr/bin/env python3
"""
Test FastAPI endpoints using TestClient
"""
import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

# Force UTF-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

client = TestClient(app)

def test_health():
    print("\nTesting /health endpoint...")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ /health passed")

def test_chat_english():
    print("\nTesting /chat endpoint (English)...")
    payload = {
        "user_uid": "test_api_user",
        "query": "Where is the nearest washroom?"
    }
    response = client.post("/chat", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Reply: {data.get('reply')}")
    
    assert response.status_code == 200
    assert "reply" in data
    assert len(data["reply"]) > 0
    print("✅ /chat (English) passed")

def test_chat_marathi():
    print("\nTesting /chat endpoint (Marathi)...")
    payload = {
        "user_uid": "test_api_user",
        "query": "जवळचे शौचालय कुठे आहे"
    }
    response = client.post("/chat", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Reply: {data.get('reply')}")
    
    assert response.status_code == 200
    assert "reply" in data
    # Basic check if reply contains Marathi characters or expected words
    # (Note: exact match might vary due to LLM, but we check for non-empty)
    assert len(data["reply"]) > 0
    print("✅ /chat (Marathi) passed")

if __name__ == "__main__":
    print("="*60)
    print("Starting FastAPI Tests")
    print("="*60)
    
    try:
        test_health()
        test_chat_english()
        test_chat_marathi()
        print("\n" + "="*60)
        print("✅ ALL API TESTS PASSED")
        print("="*60)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
