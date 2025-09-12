#!/usr/bin/env python3
"""
Test script for session management features
"""

import requests
import json

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

def test_session_management():
    phone_number = "255616107670"
    print(f"Testing session management with {phone_number}...")
    print("=" * 60)
    
    # Test 1: Send # to clear session
    print("1. Testing # command to clear session...")
    success, response = send_text_message(phone_number, "#")
    if success:
        print("✅ # command sent successfully!")
    else:
        print(f"❌ Failed to send # command: {response}")
    
    print("\n2. Testing normal message (should show ongoing session if exists)...")
    # Test 2: Send normal message
    success, response = send_text_message(phone_number, "Hello")
    if success:
        print("✅ Normal message sent successfully!")
    else:
        print(f"❌ Failed to send normal message: {response}")
    
    print("\n3. Testing 'anza' command...")
    # Test 3: Send 'anza' command
    success, response = send_text_message(phone_number, "anza")
    if success:
        print("✅ 'Anza' command sent successfully!")
    else:
        print(f"❌ Failed to send 'anza' command: {response}")
    
    print("\n" + "=" * 60)
    print("🎉 Session management test completed!")
    print("Check WhatsApp on 0616107670 to see the messages!")

if __name__ == "__main__":
    test_session_management()
