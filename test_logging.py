#!/usr/bin/env python3
"""
Test script to generate logs for testing the logging system
"""

import requests
import json
import time

# WhatsApp Configuration
WHATSAPP_TOKEN = 'EAAr1kvlgqhIBPZA0Mq7685iD5aEGm9A2TC5Xp2nVtc8ZCFA2v7vQcdZCg1O1MGpZCchvDwpFvBLOUxyYg7nNJLK84phJhOPw4Hp66vPLcpH1TCg4YyaN78pf8tUzN48rKBR5oeSNU5EbhNNsGw9wAg6KqEoA1ipFNgLZAOjWc9V6VDrhlsQoLHcEUqMST2USjKwZDZD'
WHATSAPP_PHONE_NUMBER_ID = '537559402774394'

def send_text_message(phone_number, message):
    """Send a simple text message"""
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, str(e)

def test_api_endpoints():
    """Test API endpoints to generate logs"""
    base_url = "http://localhost:8000"
    
    print("Testing API endpoints to generate logs...")
    print("=" * 50)
    
    # Test 1: Create test data
    print("1. Creating test data...")
    try:
        response = requests.post(f"{base_url}/api/create-test-data/")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    time.sleep(1)
    
    # Test 2: Get votes
    print("2. Getting votes...")
    try:
        response = requests.get(f"{base_url}/api/votes/")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    time.sleep(1)
    
    # Test 3: Get vote stats
    print("3. Getting vote stats...")
    try:
        response = requests.get(f"{base_url}/api/vote-stats/")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    time.sleep(1)
    
    # Test 4: Test webhook verification
    print("4. Testing webhook verification...")
    try:
        response = requests.get(f"{base_url}/webhook/?hub.mode=subscribe&hub.verify_token=c2a49926-a81c-11ef-b864-0242ac120002&hub.challenge=test123")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    time.sleep(1)
    
    # Test 5: Test webhook with wrong token
    print("5. Testing webhook with wrong token...")
    try:
        response = requests.get(f"{base_url}/webhook/?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge=test123")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

def test_whatsapp_messages():
    """Test WhatsApp messages to generate logs"""
    phone_number = "255616107670"
    
    print(f"\nTesting WhatsApp messages to {phone_number}...")
    print("=" * 50)
    
    messages = [
        "Hello",
        "#",
        "anza",
        "kupiga kura",
        "test message"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"{i}. Sending: '{message}'")
        success, response = send_text_message(phone_number, message)
        if success:
            print("   ✅ Sent successfully")
        else:
            print(f"   ❌ Failed: {response}")
        time.sleep(2)

def test_log_endpoints():
    """Test log viewing endpoints"""
    base_url = "http://localhost:8000"
    
    print("\nTesting log endpoints...")
    print("=" * 50)
    
    # Test JSON logs endpoint
    print("1. Testing JSON logs endpoint...")
    try:
        response = requests.get(f"{base_url}/api/logs/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Log file: {data['log_file']}")
            print(f"   ✅ Total lines: {data['total_lines']}")
            print(f"   ✅ Recent lines: {data['recent_lines']}")
        else:
            print(f"   ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    time.sleep(1)
    
    # Test errors endpoint
    print("2. Testing errors endpoint...")
    try:
        response = requests.get(f"{base_url}/api/errors/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total errors: {data['total_errors']}")
        else:
            print(f"   ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    time.sleep(1)
    
    # Test HTML logs view
    print("3. Testing HTML logs view...")
    try:
        response = requests.get(f"{base_url}/logs/")
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ Content length: {len(response.text)} characters")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Logging System")
    print("=" * 60)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test WhatsApp messages
    test_whatsapp_messages()
    
    # Test log endpoints
    test_log_endpoints()
    
    print("\n" + "=" * 60)
    print("🎉 Logging test completed!")
    print("\nYou can now view logs at:")
    print("📊 HTML View: http://localhost:8000/logs/")
    print("📋 JSON API: http://localhost:8000/api/logs/")
    print("❌ Errors Only: http://localhost:8000/api/errors/")
