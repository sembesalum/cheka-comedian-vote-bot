#!/usr/bin/env python3
"""
Test script to verify the real video is sent
"""

import requests
import json
import time

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

def test_real_video():
    """Test that the real video is sent"""
    phone_number = "255616107670"  # Your phone number
    
    print("🧪 Testing Real Video Sending")
    print("=" * 60)
    
    # Test with "Hey" command
    print(f"\n1. Testing with 'Hey' command to {phone_number}")
    print("   Expected: Welcome message + 1 real video")
    success, response = simulate_user_message(phone_number, "Hey")
    if success:
        print("   ✅ Hey command completed")
    else:
        print(f"   ❌ Failed: {response}")
    
    time.sleep(3)  # Wait for video to be sent
    
    # Test with "hi" command
    print(f"\n2. Testing with 'hi' command to {phone_number}")
    print("   Expected: Welcome message + 1 real video")
    success, response = simulate_user_message(phone_number, "hi")
    if success:
        print("   ✅ Hi command completed")
    else:
        print(f"   ❌ Failed: {response}")
    
    print("\n" + "=" * 60)
    print("🎯 Check the logs at: http://localhost:8000/logs/")
    print("📋 Expected behavior:")
    print("   - Both 'Hey' and 'hi' should trigger welcome + video")
    print("   - Video URL should be: https://momoabucket.s3.us-west-1.amazonaws.com/tcadata/fe51c7c5-95ff-4ffb-9126-ce50afc0d6a1.MP4")

if __name__ == "__main__":
    test_real_video()
