#!/usr/bin/env python3
"""
Test script for Mini Orca API on Orange Pi RV2
"""
import requests
import json
import time
import sys

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        print(f"✓ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_models():
    """Test models list endpoint"""
    print("\n🔍 Testing models endpoint...")
    try:
        response = requests.get(f"{API_URL}/v1/models", timeout=5)
        response.raise_for_status()
        models = response.json()
        print(f"✓ Available models: {json.dumps(models, indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Models list failed: {e}")
        return False

def test_chat_completion():
    """Test chat completion endpoint"""
    print("\n🔍 Testing chat completion...")
    
    payload = {
        "model": "mini-orca-small",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2? Answer briefly."}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        print("⏳ Sending request (this may take 10-30 seconds on Orange Pi)...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        duration = time.time() - start_time
        result = response.json()
        
        print(f"✓ Response received in {duration:.2f}s")
        print(f"\nAssistant: {result['choices'][0]['message']['content']}")
        print(f"\nUsage: {result.get('usage', {})}")
        return True
    except Exception as e:
        print(f"✗ Chat completion failed: {e}")
        return False

def test_streaming():
    """Test streaming chat completion"""
    print("\n🔍 Testing streaming chat...")
    
    payload = {
        "model": "mini-orca-small",
        "messages": [
            {"role": "user", "content": "Count from 1 to 5."}
        ],
        "max_tokens": 30,
        "temperature": 0.5,
        "stream": True
    }
    
    try:
        print("⏳ Starting streaming...")
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            json=payload,
            stream=True,
            timeout=60
        )
        response.raise_for_status()
        
        print("✓ Stream started. Output:")
        print("Assistant: ", end="", flush=True)
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: ') and line != 'data: [DONE]':
                    try:
                        data = json.loads(line[6:])
                        content = data['choices'][0]['delta'].get('content', '')
                        if content:
                            print(content, end="", flush=True)
                    except:
                        pass
        
        print("\n✓ Streaming completed")
        return True
    except Exception as e:
        print(f"\n✗ Streaming failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Mini Orca API Test Suite")
    print("Orange Pi RV2 4GB RAM Edition")
    print("=" * 50)
    print()
    
    results = {
        "Health Check": test_health(),
        "Models List": test_models(),
        "Chat Completion": test_chat_completion(),
        "Streaming Chat": test_streaming(),
    }
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20s}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠ Some tests failed. Check logs:")
        print("   docker-compose logs -f llama-cpp-server")
        sys.exit(1)

if __name__ == "__main__":
    main()
