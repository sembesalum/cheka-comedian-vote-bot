#!/usr/bin/env python3
"""
Send a complete voting flow test message to 0616107670
"""

import requests
import json

# WhatsApp Configuration
WHATSAPP_TOKEN = 'EAAr1kvlgqhIBPZA0Mq7685iD5aEGm9A2TC5Xp2nVtc8ZCFA2v7vQcdZCg1O1MGpZCchvDwpFvBLOUxyYg7nNJLK84phJhOPw4Hp66vPLcpH1TCg4YyaN78pf8tUzN48rKBR5oeSNU5EbhNNsGw9wAg6KqEoA1ipFNgLZAOjWc9V6VDrhlsQoLHcEUqMST2USjKwZDZD'
WHATSAPP_PHONE_NUMBER_ID = '537559402774394'

def send_interactive_message(phone_number, header_text, body_text, footer_text, buttons):
    """Send an interactive message with buttons"""
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
            "type": "button",
            "header": {
                "type": "text",
                "text": header_text
            },
            "body": {
                "text": body_text
            },
            "footer": {
                "text": footer_text
            },
            "action": {
                "buttons": buttons
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, str(e)

def send_list_message(phone_number, header_text, body_text, footer_text, button_text, sections):
    """Send an interactive list message"""
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
                "text": header_text
            },
            "body": {
                "text": body_text
            },
            "footer": {
                "text": footer_text
            },
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, str(e)

def main():
    phone_number = "255616107670"
    print(f"Sending voting flow test to {phone_number}...")
    print("=" * 60)
    
    # Step 1: Welcome message
    print("1. Sending welcome message...")
    header = "Comedian Bora wa Mwezi"
    body = """Karibu kuchagua comedian bora wa mwezi! 

Sasa utaweza kushinda TV, Friji, Brenda na Simu kwa kushiriki kumpigia kura comedian wako pendwa.

Hii ni ujumbe wa majaribio kutoka kwa bot yako ya WhatsApp."""
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
    
    success, response = send_interactive_message(phone_number, header, body, footer, buttons)
    if success:
        print("✅ Welcome message sent!")
    else:
        print(f"❌ Failed to send welcome message: {response}")
        return
    
    print("\n2. Sending comedian list...")
    # Step 2: Comedian list
    header = "Chagua Comedian"
    body = "Chagua comedian wako pendwa kutoka kwenye orodha hapa chini:"
    footer = "Chagua moja ya comedians hapo juu"
    
    sections = [{
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
    }]
    
    success, response = send_list_message(phone_number, header, body, footer, "Chagua Comedian", sections)
    if success:
        print("✅ Comedian list sent!")
    else:
        print(f"❌ Failed to send comedian list: {response}")
    
    print("\n3. Sending vote confirmation example...")
    # Step 3: Vote confirmation example
    header = "Umemchagua Nanga"
    body = """Kamalisha Kupiga Kura

Chagua idadi ya kura unayotaka kupiga:"""
    footer = "Chagua idadi ya kura"
    
    sections = [{
        "title": "Chagua Idadi ya Kura",
        "rows": [
            {
                "id": "quantity_1",
                "title": "Kura 1 (TZS 1000)",
                "description": "Kura moja na tiket 1"
            },
            {
                "id": "quantity_3", 
                "title": "Kura 3 (TZS 3000)",
                "description": "Kura tatu na tiketi 3"
            },
            {
                "id": "quantity_5",
                "title": "Kura 5 (TZS 5000)",
                "description": "Kura tano na tiketi 6"
            },
            {
                "id": "quantity_12",
                "title": "Kura 12 (TZS 10000)",
                "description": "Kura kumi na mbili"
            }
        ]
    }]
    
    success, response = send_list_message(phone_number, header, body, footer, "Chagua Idadi", sections)
    if success:
        print("✅ Vote confirmation sent!")
    else:
        print(f"❌ Failed to send vote confirmation: {response}")
    
    print("\n" + "=" * 60)
    print("🎉 Voting flow test completed!")
    print("Check WhatsApp on 0616107670 to see the messages!")

if __name__ == "__main__":
    main()
