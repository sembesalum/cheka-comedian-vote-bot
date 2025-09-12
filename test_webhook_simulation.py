#!/usr/bin/env python3
"""
Test script to simulate webhook calls for comedian selection
"""

import requests
import json

def simulate_comedian_selection(phone_number, comedian_id):
    """Simulate a webhook call for comedian selection"""
    
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
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "list_reply",
                                        "list_reply": {
                                            "id": comedian_id,
                                            "title": "Selected comedian"
                                        }
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

def test_all_comedians():
    """Test selection of all comedians"""
    phone_number = "255616107670"
    
    comedian_ids = [
        "comedian_eliud",
        "comedian_nanga", 
        "comedian_brother_k",
        "comedian_ndaro",
        "comedian_steve_mweusi"
    ]
    
    print("🧪 Testing Comedian Selection via Webhook")
    print("=" * 50)
    
    for comedian_id in comedian_ids:
        print(f"\nTesting: {comedian_id}")
        success = simulate_comedian_selection(phone_number, comedian_id)
        if success:
            print("   ✅ Success")
        else:
            print("   ❌ Failed")
        
        # Wait a bit between tests
        import time
        time.sleep(2)

if __name__ == "__main__":
    test_all_comedians()
