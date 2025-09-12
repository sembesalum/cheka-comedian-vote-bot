#!/usr/bin/env python3
"""
Test script to simulate WhatsApp message flow
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

def send_interactive_list(phone_number):
    """Send the comedian list to test selection"""
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Comedian Bora wa Mwezi"
            },
            "body": {
                "text": "Chagua comedian wako pendwa kutoka kwenye orodha hapa chini:"
            },
            "footer": {
                "text": "Chagua moja ya comedians hapo juu"
            },
            "action": {
                "button": "Chagua Comedian",
                "sections": [
                    {
                        "title": "Comedians",
                        "rows": [
                            {
                                "id": "comedian_eliud",
                                "title": "Eliud",
                                "description": "Piga kura kwa Eliud"
                            },
                            {
                                "id": "comedian_nanga",
                                "title": "Nanga",
                                "description": "Piga kura kwa Nanga"
                            },
                            {
                                "id": "comedian_brother_k",
                                "title": "Brother K",
                                "description": "Piga kura kwa Brother K"
                            },
                            {
                                "id": "comedian_ndaro",
                                "title": "Ndaro",
                                "description": "Piga kura kwa Ndaro"
                            },
                            {
                                "id": "comedian_steve_mweusi",
                                "title": "Steve Mweusi",
                                "description": "Piga kura kwa Steve Mweusi"
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, str(e)

def test_complete_flow():
    """Test the complete WhatsApp flow"""
    phone_number = "255616107670"
    
    print("🧪 Testing Complete WhatsApp Flow")
    print("=" * 50)
    
    # Step 1: Start the flow
    print("1. Starting flow with 'anza'...")
    success, response = send_text_message(phone_number, "anza")
    if success:
        print("   ✅ Started successfully")
    else:
        print(f"   ❌ Failed: {response}")
    
    time.sleep(3)
    
    # Step 2: Send comedian list directly
    print("\n2. Sending comedian list...")
    success, response = send_interactive_list(phone_number)
    if success:
        print("   ✅ List sent successfully")
    else:
        print(f"   ❌ Failed: {response}")
    
    print("\n" + "=" * 50)
    print("🎯 Now try selecting a comedian from the list!")
    print("Check the logs at: http://localhost:8000/logs/")
    print("Check errors at: http://localhost:8000/api/errors/")

if __name__ == "__main__":
    test_complete_flow()
