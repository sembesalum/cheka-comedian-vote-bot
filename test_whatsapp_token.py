#!/usr/bin/env python3
"""
Test script to verify WhatsApp token and send test message
"""

import requests
import json

# WhatsApp Configuration
WHATSAPP_TOKEN = 'EAAr1kvlgqhIBPZA0Mq7685iD5aEGm9A2TC5Xp2nVtc8ZCFA2v7vQcdZCg1O1MGpZCchvDwpFvBLOUxyYg7nNJLK84phJhOPw4Hp66vPLcpH1TCg4YyaN78pf8tUzN48rKBR5oeSNU5EbhNNsGw9wAg6KqEoA1ipFNgLZAOjWc9V6VDrhlsQoLHcEUqMST2USjKwZDZD'
WHATSAPP_PHONE_NUMBER_ID = '537559402774394'

def test_token():
    """Test if the WhatsApp token is valid"""
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}"
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Token test response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Token is valid!")
            print(f"Phone number info: {response.json()}")
            return True
        else:
            print(f"❌ Token test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing token: {str(e)}")
        return False

def send_simple_message(phone_number):
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
        "text": {
            "body": "Hujambo! Hii ni ujumbe wa majaribio kutoka kwa bot yako ya Comedian Voting. Bot inafanya kazi vizuri! 🎉"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Message send response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Message sent successfully!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {str(e)}")
        return False

def main():
    print("Testing WhatsApp API...")
    print("=" * 50)
    
    # Test token first
    if test_token():
        print("\nSending test message to 255616107670...")
        send_simple_message("255616107670")
    else:
        print("\n❌ Cannot send message - token is invalid")
        print("Please check your WhatsApp token in the settings.py file")

if __name__ == "__main__":
    main()
