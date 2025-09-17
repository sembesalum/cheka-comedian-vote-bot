#!/usr/bin/env python3
"""
Test script to verify both new and returning users get videos
"""

import requests
import json
import time
import random

def simulate_user_message(phone_number, message):
    """Simulate a webhook call"""
    
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

def test_all_users_get_videos():
    """Test that both new and returning users get videos"""
    # Use a unique phone number for new user test
    new_user_phone = f"255{random.randint(100000000, 999999999)}"
    returning_user_phone = f"255{random.randint(100000000, 999999999)}"
    
    print("🧪 Testing All Users Get Videos")
    print("=" * 60)
    
    # Test 1: New User
    print(f"\n1. Testing NEW USER: {new_user_phone}")
    print("   Expected: Welcome message + 3 videos")
    success, response = simulate_user_message(new_user_phone, "anza")
    if success:
        print("   ✅ New user flow completed")
    else:
        print(f"   ❌ Failed: {response}")
    
    time.sleep(5)  # Wait for videos to be sent
    
    # Test 2: Returning User (same phone number)
    print(f"\n2. Testing RETURNING USER: {new_user_phone}")
    print("   Expected: Welcome message + 3 videos (same as new user)")
    success, response = simulate_user_message(new_user_phone, "anza")
    if success:
        print("   ✅ Returning user flow completed")
    else:
        print(f"   ❌ Failed: {response}")
    
    time.sleep(5)  # Wait for videos to be sent
    
    # Test 3: Different returning user
    print(f"\n3. Testing DIFFERENT RETURNING USER: {returning_user_phone}")
    print("   Expected: Welcome message + 3 videos")
    success, response = simulate_user_message(returning_user_phone, "hi")
    if success:
        print("   ✅ Different returning user flow completed")
    else:
        print(f"   ❌ Failed: {response}")
    
    time.sleep(5)  # Wait for videos to be sent
    
    # Test 4: Same returning user again
    print(f"\n4. Testing SAME RETURNING USER AGAIN: {returning_user_phone}")
    print("   Expected: Welcome message + 3 videos (again)")
    success, response = simulate_user_message(returning_user_phone, "start")
    if success:
        print("   ✅ Same returning user flow completed")
    else:
        print(f"   ❌ Failed: {response}")
    
    print("\n" + "=" * 60)
    print("🎯 Check the logs at: http://localhost:8000/logs/")
    print("📋 Expected behavior:")
    print("   - ALL users (new and returning) get 3 videos")
    print("   - Videos sent every time user starts the bot")
    print("   - Welcome message mentions videos for all users")

if __name__ == "__main__":
    test_all_users_get_videos()
