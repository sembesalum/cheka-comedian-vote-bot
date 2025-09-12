import requests
import json
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from .models import Comedian, VotingSession, Vote, Ticket, Payment


def whatsapp_api_call(payload):
    """Make API call to WhatsApp"""
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(
            f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {str(e)}")
        return None


def send_text_message(phone_number, message):
    """Send a simple text message"""
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    return whatsapp_api_call(payload)


def send_interactive_message(phone_number, header_text, body_text, footer_text, buttons):
    """Send an interactive message with buttons"""
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
    return whatsapp_api_call(payload)


def send_list_message(phone_number, header_text, body_text, footer_text, button_text, sections):
    """Send an interactive list message"""
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
    return whatsapp_api_call(payload)


def process_message(data):
    """Process incoming WhatsApp messages"""
    try:
        for message in data.get('messages', []):
            phone_number = message.get('from')
            message_type = message.get('type')
            
            if message_type == 'text':
                text = message.get('text', {}).get('body', '').lower().strip()
                handle_text_message(phone_number, text)
            elif message_type == 'interactive':
                interactive = message.get('interactive', {})
                if interactive.get('type') == 'button_reply':
                    button_id = interactive.get('button_reply', {}).get('id')
                    handle_button_click(phone_number, button_id)
                elif interactive.get('type') == 'list_reply':
                    list_id = interactive.get('list_reply', {}).get('id')
                    handle_list_selection(phone_number, list_id)
    except Exception as e:
        print(f"Error processing message: {str(e)}")


def handle_text_message(phone_number, text):
    """Handle text messages"""
    if text in ['hi', 'hello', 'start', 'kupiga kura']:
        send_welcome_message(phone_number)
    else:
        send_welcome_message(phone_number)


def handle_button_click(phone_number, button_id):
    """Handle button clicks"""
    if button_id == 'start_voting':
        send_comedians_list(phone_number)
    elif button_id == 'play_again':
        send_welcome_message(phone_number)
    else:
        send_welcome_message(phone_number)


def handle_list_selection(phone_number, list_id):
    """Handle list selections"""
    if list_id.startswith('comedian_'):
        comedian_name = list_id.replace('comedian_', '').replace('_', ' ')
        send_vote_confirmation(phone_number, comedian_name)
    elif list_id.startswith('quantity_'):
        quantity = int(list_id.replace('quantity_', ''))
        # Get the last vote for this phone number
        last_vote = Vote.objects.filter(phone_number=phone_number).order_by('-created_at').first()
        if last_vote:
            process_payment(phone_number, last_vote, quantity)
    else:
        send_welcome_message(phone_number)


def send_welcome_message(phone_number):
    """Send welcome message with voting button"""
    header = "Comedian Bora wa Mwezi"
    body = """Karibu kuchagua comedian bora wa mwezi, Sasa utaweza kushinda TV, Friji, Brenda na Simu kwa kushiriki kumpigia kura comedian wako pendwa."""
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
    
    send_interactive_message(phone_number, header, body, footer, buttons)


def send_comedians_list(phone_number):
    """Send list of comedians"""
    header = "Chagua Comedian"
    body = "Chagua comedian wako pendwa kutoka kwenye orodha hapa chini:"
    footer = "Chagua moja ya comedians hapo juu"
    
    comedians = Comedian.objects.filter(is_active=True)
    sections = [{
        "title": "Comedians",
        "rows": []
    }]
    
    for comedian in comedians:
        sections[0]["rows"].append({
            "id": f"comedian_{comedian.name.lower().replace(' ', '_')}",
            "title": comedian.name,
            "description": f"Piga kura kwa {comedian.name}"
        })
    
    send_list_message(phone_number, header, body, footer, "Chagua Comedian", sections)


def send_vote_confirmation(phone_number, comedian_name):
    """Send vote confirmation with quantity options"""
    try:
        comedian = Comedian.objects.get(name=comedian_name)
        
        # Create a temporary vote record
        active_session = VotingSession.objects.filter(is_active=True).first()
        if not active_session:
            send_text_message(phone_number, "Hakuna kipindi cha kupiga kura kwa sasa. Tafadhali jaribu tena baadaye.")
            return
        
        # Store comedian selection in session or create a temporary vote
        vote = Vote.objects.create(
            comedian=comedian,
            voting_session=active_session,
            phone_number=phone_number,
            quantity=1,  # Default, will be updated
            amount=1000,  # Default, will be updated
            is_paid=False
        )
        
        header = f"Umemchagua {comedian_name}"
        body = "Kamalisha Kupiga Kura\n\nChagua idadi ya kura unayotaka kupiga:"
        footer = "Chagua idadi ya kura"
        
        sections = [{
            "title": "Chagua Idadi ya Kura",
            "rows": [
                {
                    "id": "quantity_1",
                    "title": "Kura 1 na Tiket 1 ya Kushinda (TZS 1000)",
                    "description": "Kura moja tu"
                },
                {
                    "id": "quantity_3",
                    "title": "Kura 3 na Tiketi 3 za Kushinda (TZS 3000)",
                    "description": "Kura tatu"
                },
                {
                    "id": "quantity_5",
                    "title": "Kura 5 na Tickets 6 za kushinda (TZS 5000)",
                    "description": "Kura tano"
                },
                {
                    "id": "quantity_12",
                    "title": "Kura 12 na Tiket 12 za Kushinda (TZS 10000)",
                    "description": "Kura kumi na mbili"
                }
            ]
        }]
        
        send_list_message(phone_number, header, body, footer, "Chagua Idadi", sections)
        
    except Comedian.DoesNotExist:
        send_text_message(phone_number, "Comedian huyo hajapatikana. Tafadhali chagua kutoka kwenye orodha.")
        send_comedians_list(phone_number)


def process_payment(phone_number, vote, quantity):
    """Process payment and generate tickets"""
    try:
        with transaction.atomic():
            # Update vote with selected quantity
            vote.quantity = quantity
            vote.amount = quantity * 1000  # TZS 1000 per vote
            vote.save()
            
            # Create payment record
            payment = Payment.objects.create(
                vote=vote,
                amount=vote.amount,
                status='completed',  # Dummy payment - always successful
                payment_method='dummy',
                transaction_reference=f'DUMMY_{vote.id}_{int(timezone.now().timestamp())}'
            )
            
            # Mark vote as paid
            vote.is_paid = True
            vote.save()
            
            # Generate tickets
            generate_tickets(vote)
            
            # Send confirmation message
            send_payment_confirmation(phone_number, vote)
            
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        send_text_message(phone_number, "Kuna hitilafu katika malipo. Tafadhali jaribu tena.")


def generate_tickets(vote):
    """Generate tickets for a vote"""
    # Generate tickets based on quantity (5 votes = 6 tickets as per requirement)
    ticket_count = vote.quantity
    if vote.quantity == 5:
        ticket_count = 6  # Special case: 5 votes = 6 tickets
    
    for _ in range(ticket_count):
        Ticket.objects.create(vote=vote)


def send_payment_confirmation(phone_number, vote):
    """Send payment confirmation with tickets"""
    tickets = vote.tickets.all()
    ticket_codes = [ticket.ticket_code for ticket in tickets]
    
    header = f"Ahsante kwa kupigia kura {vote.comedian.name}"
    body = f"""Votes Details 
Umempigia kura {vote.quantity}

Umepata tickets {len(ticket_codes)} ambazo ni:
{chr(10).join(ticket_codes)}

Washindi watangazwa tarehe {vote.voting_session.winner_announcement_date.strftime('%d.%m.%Y')}

Vigezo na Masharti kuzingazitwa"""
    footer = "Asante kwa kushiriki"
    
    buttons = [
        {
            "type": "reply",
            "reply": {
                "id": "play_again",
                "title": "Cheza Tena"
            }
        }
    ]
    
    send_interactive_message(phone_number, header, body, footer, buttons)
