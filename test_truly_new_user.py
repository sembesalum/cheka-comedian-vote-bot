#!/usr/bin/env python3
"""
Test script to simulate truly new user flow
"""

import requests
import json
import time
import random

def simulate_new_user_message(phone_number, message):
    """Simulate a webhook call for new user"""
    
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "ENTRY_ID",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15551234567",
                                "phone_number_id": "537559402774394"
                            },
                            "messages": [
                                {
                                    "from": phone_number,
                                    "id": "wamid.xxx",
                                    "timestamp": "1234567890",
                                    "type": "text",
                                    "text": {
                                        "body": message
                                    }
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    url = "http://localhost:8000/webhook/"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=webhook_payload, timeout=10)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)

def test_truly_new_user():
    """Test with a completely new phone number"""
    # Generate a random phone number to ensure it's new
    phone_number = f"255{random.randint(100000000, 999999999)}"
    
    print("🧪 Testing Truly New User Flow")
    print("=" * 50)
    print(f"Using phone number: {phone_number}")
    
    print(f"\n1. Testing new user with 'anza' message...")
    success, response = simulate_new_user_message(phone_number, "anza")
    if success:
        print("   ✅ New user flow initiated successfully")
        print("   📹 User should receive welcome message + 3 videos")
    else:
        print(f"   ❌ Failed: {response}")
    
    time.sleep(5)  # Wait for videos to be sent
    
    print(f"\n2. Testing same user again (should be returning user)...")
    success, response = simulate_new_user_message(phone_number, "anza")
    if success:
        print("   ✅ Returning user flow initiated successfully")
        print("   📝 User should receive welcome message only (no videos)")
    else:
        print(f"   ❌ Failed: {response}")
    
    print("\n" + "=" * 50)
    print("🎯 Check the logs at: http://localhost:8000/logs/")
    print("👥 Check users at: http://localhost:8000/admin/users/")
    print("🎥 Check videos at: http://localhost:8000/admin/videos/")

if __name__ == "__main__":
    test_truly_new_user()
