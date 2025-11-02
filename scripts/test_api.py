#!/usr/bin/env python3
"""
Test script for LLM API Server
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        print("✓ Health check passed")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_list_models():
    """Test list models endpoint"""
    print("\nTesting /v1/models endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/v1/models")
        response.raise_for_status()
        data = response.json()
        print("✓ List models passed")
        print(f"  Available models: {[m['id'] for m in data['data']]}")
        return True
    except Exception as e:
        print(f"✗ List models failed: {e}")
        return False

def test_chat_completion(model="phi3:mini"):
    """Test chat completion endpoint"""
    print(f"\nTesting /v1/chat/completions with model {model}...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": "Say hello in one sentence."}
                ],
                "temperature": 0.7,
                "max_tokens": 100
            }
        )
        response.raise_for_status()
        data = response.json()
        print("✓ Chat completion passed")
        print(f"  Response: {data['choices'][0]['message']['content']}")
        print(f"  Tokens used: {data['usage']['total_tokens']}")
        return True
    except Exception as e:
        print(f"✗ Chat completion failed: {e}")
        return False

def test_streaming(model="phi3:mini"):
    """Test streaming chat completion"""
    print(f"\nTesting streaming with model {model}...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": "Count from 1 to 5."}
                ],
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 100
            },
            stream=True
        )
        response.raise_for_status()
        
        print("✓ Streaming started")
        print("  Response: ", end="", flush=True)
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        data = json.loads(data_str)
                        content = data['choices'][0]['delta'].get('content', '')
                        print(content, end="", flush=True)
                    except json.JSONDecodeError:
                        pass
        
        print("\n✓ Streaming completed")
        return True
    except Exception as e:
        print(f"\n✗ Streaming failed: {e}")
        return False

def main():
    print("=" * 50)
    print("LLM API Server Test Suite")
    print("=" * 50)
    
    # Run tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("List Models", test_list_models()))
    results.append(("Chat Completion", test_chat_completion()))
    results.append(("Streaming", test_streaming()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
