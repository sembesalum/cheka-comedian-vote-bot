#!/usr/bin/env python3
"""
Complete test of session management features
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

def test_complete_session_flow():
    phone_number = "255616107670"
    print(f"Testing complete session management flow with {phone_number}...")
    print("=" * 70)
    
    # Step 1: Clear any existing session
    print("1. Clearing any existing session with # command...")
    success, response = send_text_message(phone_number, "#")
    if success:
        print("✅ Session cleared!")
    else:
        print(f"❌ Failed to clear session: {response}")
    
    time.sleep(2)
    
    # Step 2: Start new session
    print("\n2. Starting new session with 'anza'...")
    success, response = send_text_message(phone_number, "anza")
    if success:
        print("✅ New session started!")
    else:
        print(f"❌ Failed to start session: {response}")
    
    time.sleep(2)
    
    # Step 3: Send another message (should show ongoing session)
    print("\n3. Sending another message (should show ongoing session)...")
    success, response = send_text_message(phone_number, "Hello again")
    if success:
        print("✅ Ongoing session message sent!")
    else:
        print(f"❌ Failed to send ongoing session message: {response}")
    
    time.sleep(2)
    
    # Step 4: Clear session again
    print("\n4. Clearing session again with # command...")
    success, response = send_text_message(phone_number, "#")
    if success:
        print("✅ Session cleared again!")
    else:
        print(f"❌ Failed to clear session: {response}")
    
    time.sleep(2)
    
    # Step 5: Start fresh session
    print("\n5. Starting fresh session with 'kupiga kura'...")
    success, response = send_text_message(phone_number, "kupiga kura")
    if success:
        print("✅ Fresh session started!")
    else:
        print(f"❌ Failed to start fresh session: {response}")
    
    print("\n" + "=" * 70)
    print("🎉 Complete session management test completed!")
    print("Check WhatsApp on 0616107670 to see the complete flow!")
    print("\nExpected behavior:")
    print("- # command should clear session and show welcome")
    print("- Any text should show ongoing session message if session exists")
    print("- 'anza' or 'kupiga kura' should start new session")

if __name__ == "__main__":
    test_complete_session_flow()
