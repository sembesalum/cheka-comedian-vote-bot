#!/usr/bin/env python3
"""
Test script to send a WhatsApp message to a specific phone number
"""

import requests
import json
from django.conf import settings
import os
import sys

# Add the project directory to Python path
sys.path.append('/Users/salum_sembe/backend/chekabot')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comedian_voting_bot.settings')

import django
django.setup()

from whatsapp_bot.utils import send_text_message, send_interactive_message

def send_test_message():
    phone_number = "255616107670"  # Add country code for Tanzania
    print(f"Sending test message to {phone_number}...")
    
    # Send welcome message
    header = "Comedian Bora wa Mwezi - Test"
    body = """Karibu kuchagua comedian bora wa mwezi! 

Hii ni ujumbe wa majaribio kutoka kwa bot yako ya WhatsApp.

Sasa utaweza kushinda TV, Friji, Brenda na Simu kwa kushiriki kumpigia kura comedian wako pendwa."""
    footer = "Chagua chini ili uanze"
    
    buttons = [
        {
            "type": "reply",
            "reply": {
                "id": "start_voting",
                "title": "Bonyeza Kupiga Kura"
            }
        }
    ]
    
    try:
        result = send_interactive_message(phone_number, header, body, footer, buttons)
        if result:
            print("✅ Test message sent successfully!")
            print(f"Response: {result}")
        else:
            print("❌ Failed to send message")
    except Exception as e:
        print(f"❌ Error sending message: {str(e)}")

if __name__ == "__main__":
    send_test_message()
