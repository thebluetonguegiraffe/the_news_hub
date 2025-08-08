#!/usr/bin/env python3
"""
Test script for the News RS API
"""

import requests
import json
from datetime import datetime
BASE_URL = "http://localhost:7000"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running.")
        return False

def test_topics_endpoint():
    """Test the topics endpoint"""
    print("\nTesting topics endpoint...")
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = requests.get(f"{BASE_URL}/topics/{today}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API.")
        return False

def test_articles_endpoint():
    """Test the articles endpoint"""
    print("\nTesting articles endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/articles/technology?limit=3")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API.")
        return False

def main():
    """Run all tests"""
    print("Starting API tests...")
    
    tests = [
        test_health,
        test_topics_endpoint,
        test_articles_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")

if __name__ == "__main__":
    main() 