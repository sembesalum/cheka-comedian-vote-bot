import requests
import json
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from .models import Comedian, VotingSession, Vote, Ticket, Payment, User, WelcomeVideo
from django.core.cache import cache
from .session_functions import has_ongoing_session, clear_user_session, send_ongoing_session_message, set_user_session, get_user_session
from .logger import log_error, log_message, log_payment, log_session


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
        result = response.json()
        log_message('system', 'api_call', f"Success: {result}")
        return result
    except requests.exceptions.RequestException as e:
        log_error(f"WhatsApp API Error: {str(e)}", extra_data={'payload': payload})
        return None


def get_or_create_user(phone_number):
    """Get or create user and return user object and is_new flag"""
    try:
        user = User.objects.get(phone_number=phone_number)
        log_message(phone_number, 'user_found', f"Returning user: {user.phone_number}")
        return user, False
    except User.DoesNotExist:
        user = User.objects.create(phone_number=phone_number)
        log_message(phone_number, 'user_created', f"New user created: {user.phone_number}")
        return user, True


def send_video_message(phone_number, video_url, caption=""):
    """Send video message via WhatsApp"""
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "video",
        "video": {
            "link": video_url,
            "caption": caption
        }
    }
    
    result = whatsapp_api_call(payload)
    if result:
        log_message(phone_number, 'video_sent', f"Video sent: {video_url}")
    return result


def send_welcome_videos(phone_number):
    """Send welcome videos to new users"""
    videos = WelcomeVideo.objects.filter(is_active=True).order_by('order')
    
    if not videos.exists():
        log_message(phone_number, 'no_videos', "No welcome videos found")
        return
    
    log_message(phone_number, 'sending_videos', f"Sending {videos.count()} welcome videos")
    
    for i, video in enumerate(videos, 1):
        caption = f"Video {i}: {video.title}" if video.title else f"Video {i}"
        send_video_message(phone_number, video.video_url, caption)
        
        # Small delay between videos to avoid rate limiting
        import time
        time.sleep(1)


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
    log_message(phone_number, 'text', text)

    # Get or create user
    user, is_new_user = get_or_create_user(phone_number)

    # Check for clear session command
    if text == '#':
        log_session(phone_number, 'clear_session')
        clear_user_session(phone_number)
        send_text_message(phone_number, "Session imefutwa. Unaweza kuanza upya.")
        send_welcome_message(phone_number, is_new_user)
        return

    # Check if user has an ongoing session
    if has_ongoing_session(phone_number):
        log_session(phone_number, 'ongoing_session_detected')
        send_ongoing_session_message(phone_number)
        return

    # Handle start commands
    if text.lower() in ['hi', 'hello', 'hey', 'start', 'kupiga kura', 'anza']:
        log_session(phone_number, 'start_new_session')
        
        # Send welcome message
        send_welcome_message(phone_number, is_new_user)
        
        # Send welcome videos to ALL users (new and returning)
        send_welcome_videos(phone_number)
        
        # If new user, mark as no longer first-time
        if is_new_user:
            user.is_first_time = False
            user.save()
            log_message(phone_number, 'user_marked_returning', "User marked as returning user")
    else:
        log_session(phone_number, 'unknown_command', text)
        send_welcome_message(phone_number, is_new_user)


def handle_button_click(phone_number, button_id):
    """Handle button clicks"""
    if button_id == 'start_voting':
        send_comedians_list(phone_number)
    elif button_id == 'play_again':
        # Get user status for welcome message
        user, is_new_user = get_or_create_user(phone_number)
        send_welcome_message(phone_number, is_new_user)
    elif button_id == 'clear_session':
        clear_user_session(phone_number)
        send_text_message(phone_number, "Session imefutwa. Unaweza kuanza upya.")
        # Get user status for welcome message
        user, is_new_user = get_or_create_user(phone_number)
        send_welcome_message(phone_number, is_new_user)
    else:
        # Get user status for welcome message
        user, is_new_user = get_or_create_user(phone_number)
        send_welcome_message(phone_number, is_new_user)


def handle_list_selection(phone_number, list_id):
    """Handle list selections"""
    log_message(phone_number, 'list_selection', f"Selected: {list_id}")
    
    if list_id.startswith('comedian_'):
        # Convert back from ID format to comedian name
        comedian_id = list_id.replace('comedian_', '')
        log_message(phone_number, 'comedian_selection', f"Looking for comedian with ID: {comedian_id}")
        
        # Find comedian by matching the ID format
        try:
            comedian = Comedian.objects.get(
                name__iexact=comedian_id.replace('_', ' ')
            )
            log_message(phone_number, 'comedian_found', f"Found comedian: {comedian.name}")
            send_vote_confirmation(phone_number, comedian.name)
        except Comedian.DoesNotExist:
            log_error(f"Comedian not found for ID: {comedian_id}", phone_number)
            # Try alternative matching
            comedian_name = comedian_id.replace('_', ' ').title()
            log_message(phone_number, 'comedian_retry', f"Trying alternative name: {comedian_name}")
            try:
                comedian = Comedian.objects.get(name__iexact=comedian_name)
                log_message(phone_number, 'comedian_found_alt', f"Found comedian with alternative: {comedian.name}")
                send_vote_confirmation(phone_number, comedian.name)
            except Comedian.DoesNotExist:
                log_error(f"Comedian not found with alternative: {comedian_name}", phone_number)
                send_text_message(phone_number, "Comedian huyo hajapatikana. Tafadhali chagua kutoka kwenye orodha.")
                send_comedians_list(phone_number)
    elif list_id.startswith('quantity_'):
        quantity = int(list_id.replace('quantity_', ''))
        log_message(phone_number, 'quantity_selection', f"Selected quantity: {quantity}")
        # Get the last vote for this phone number
        last_vote = Vote.objects.filter(phone_number=phone_number).order_by('-created_at').first()
        if last_vote:
            process_payment(phone_number, last_vote, quantity)
        else:
            log_error("No vote found for quantity selection", phone_number)
            user, is_new_user = get_or_create_user(phone_number)
            send_welcome_message(phone_number, is_new_user)
    else:
        log_message(phone_number, 'unknown_selection', f"Unknown selection: {list_id}")
        user, is_new_user = get_or_create_user(phone_number)
        send_welcome_message(phone_number, is_new_user)


def send_welcome_message(phone_number, is_new_user=False):
    """Send welcome message with voting button"""
    if is_new_user:
        header = "Karibu! Comedian Bora wa Mwezi"
        body = """Karibu kuchagua comedian bora wa mwezi! 🎉

Kama mtumiaji mpya, utapata videos maalum za kukaribisha! 📹

Sasa utaweza kushinda TV, Friji, Brenda na Simu kwa kushiriki kumpigia kura comedian wako pendwa.

Andika # ili ufute session yoyote inaendelea."""
    else:
        header = "Karibu Tena! Comedian Bora wa Mwezi"
        body = """Karibu tena! Utapata videos maalum za kukaribisha! 📹

Sasa utaweza kushinda TV, Friji, Brenda na Simu kwa kushiriki kumpigia kura comedian wako pendwa.

Andika # ili ufute session yoyote inaendelea."""
    
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
        
        # Set session data
        set_user_session(phone_number, {
            'comedian_id': comedian.id,
            'vote_id': vote.id,
            'step': 'quantity_selection'
        })
        
        header = f"Umemchagua {comedian_name}"
        body = "Kamalisha Kupiga Kura\n\nChagua idadi ya kura unayotaka kupiga:"
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
            
            # Log payment
            log_payment(phone_number, vote.amount, 'completed', payment.payment_id)
            
            # Clear session after successful payment
            clear_user_session(phone_number)
            log_session(phone_number, 'session_cleared_after_payment')
            
            # Send confirmation message
            send_payment_confirmation(phone_number, vote)
            
    except Exception as e:
        log_error(f"Payment processing error: {str(e)}", phone_number, {'vote_id': vote.id, 'quantity': quantity})
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
