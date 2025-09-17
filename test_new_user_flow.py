#!/usr/bin/env python3
"""
Test script to simulate new user flow with videos
"""

import requests
import json
import time

def simulate_new_user_message(phone_number, message):
    """Simulate a webhook call for new user"""
    
    # Simulate the webhook payload that WhatsApp would send
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
    
    # Send to local webhook
    url = "http://localhost:8000/webhook/"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=webhook_payload, timeout=10)
        print(f"Webhook response: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_new_user_flow():
    """Test new user flow"""
    # Use a unique phone number to simulate new user
    phone_number = "255616107671"  # Different from previous tests
    
    print("🧪 Testing New User Flow with Videos")
    print("=" * 50)
    
    print(f"\n1. Testing new user with 'anza' message...")
    success = simulate_new_user_message(phone_number, "anza")
    if success:
        print("   ✅ New user flow initiated successfully")
        print("   📹 User should receive welcome message + 3 videos")
    else:
        print("   ❌ Failed to initiate new user flow")
    
    time.sleep(3)
    
    print(f"\n2. Testing same user again (should be returning user)...")
    success = simulate_new_user_message(phone_number, "anza")
    if success:
        print("   ✅ Returning user flow initiated successfully")
        print("   📝 User should receive welcome message only (no videos)")
    else:
        print("   ❌ Failed to initiate returning user flow")
    
    print(f"\n3. Testing with 'hi' message...")
    success = simulate_new_user_message(phone_number, "hi")
    if success:
        print("   ✅ 'Hi' message handled successfully")
    else:
        print("   ❌ Failed to handle 'hi' message")
    
    print("\n" + "=" * 50)
    print("🎯 Check the logs at: http://localhost:8000/logs/")
    print("👥 Check users at: http://localhost:8000/admin/users/")
    print("🎥 Check videos at: http://localhost:8000/admin/videos/")

if __name__ == "__main__":
    test_new_user_flow()
