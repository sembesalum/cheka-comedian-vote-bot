import requests
import json
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from .models import Comedian, VotingSession, Vote, Ticket, Payment, User
from django.core.cache import cache
from .session_functions import has_ongoing_session, clear_user_session, send_ongoing_session_message, set_user_session, get_user_session
from .logger import log_error, log_message, log_payment, log_session
from .payment_functions import initiate_payment, check_payment_status


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
        # Also clear any ongoing payment sessions
        clear_payment_session(phone_number)
        send_text_message(phone_number, "Session imefutwa. Unaweza kuanza upya.")
        # Always send welcome message when clearing session
        send_welcome_message(phone_number, is_new_user)
        return

    # Handle status check command (before ongoing session check)
    if text.lower() in ['status', 'hali', 'check']:
        check_payment_status_manual(phone_number)
        return

    # Check if user has an ongoing session
    if has_ongoing_session(phone_number):
        session_data = get_user_session(phone_number)
        
        # Check if waiting for payment phone number
        if session_data and session_data.get('step') == 'waiting_for_payment_phone':
            log_message(phone_number, 'payment_phone_input', f"Received payment phone: {text}")
            handle_payment_phone_input(phone_number, text)
            return
        
        # Check if processing payment
        elif session_data and session_data.get('step') == 'processing_payment':
            send_text_message(phone_number, "Malipo yako yanaendelea. Tafadhali subiri kidogo...")
            return
        
        # Other ongoing session
        log_session(phone_number, 'ongoing_session_detected')
        send_ongoing_session_message(phone_number)
        return

    # Handle start commands and ANY text message
    if text.lower() in ['hi', 'hello', 'hey', 'start', 'kupiga kura', 'anza'] or True:  # Always send welcome
        log_session(phone_number, 'start_new_session')
        
        # Clear any existing sessions when starting new
        clear_user_session(phone_number)
        clear_payment_session(phone_number)
        
        # Send welcome message
        send_welcome_message(phone_number, is_new_user)
        
        # If new user, mark as no longer first-time
        if is_new_user:
            user.is_first_time = False
            user.save()
            log_message(phone_number, 'user_marked_returning', "User marked as returning user")


def handle_button_click(phone_number, button_id):
    """Handle button clicks"""
    if button_id == 'start_voting':
        send_comedians_with_images(phone_number)
    elif button_id == 'show_comedians_list':
        send_comedians_list(phone_number)
    elif button_id == 'play_again':
        # Get user status for welcome message
        user, is_new_user = get_or_create_user(phone_number)
        send_welcome_message(phone_number, is_new_user)
    elif button_id == 'clear_session':
        clear_user_session(phone_number)
        clear_payment_session(phone_number)  # Also clear payment sessions
        send_text_message(phone_number, "Session imefutwa. Unaweza kuanza upya.")
        # Get user status for welcome message
        user, is_new_user = get_or_create_user(phone_number)
        send_welcome_message(phone_number, is_new_user)
    elif button_id.startswith('payment_confirmed_'):
        # User confirmed they have paid
        transaction_id = button_id.replace('payment_confirmed_', '')
        handle_payment_confirmation(phone_number, transaction_id)
    elif button_id.startswith('payment_cancelled_'):
        # User wants to cancel payment
        transaction_id = button_id.replace('payment_cancelled_', '')
        handle_payment_cancellation(phone_number, transaction_id)
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
            # Update vote with selected quantity
            last_vote.quantity = quantity
            last_vote.amount = quantity * 1000  # TZS 1000 per vote
            last_vote.save()
            
            # Ask for payment phone number
            ask_for_payment_phone(phone_number, last_vote)
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

Sasa utaweza kushinda TV, Friji, Brenda na Simu kwa kushiriki kumpigia kura comedian wako pendwa.

Andika # ili ufute session yoyote inaendelea."""
    else:
        header = "Karibu Tena! Comedian Bora wa Mwezi"
        body = """Karibu tena!

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
        },
        {
            "type": "reply",
            "reply": {
                "id": "clear_session",
                "title": "Futa Session"
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


def send_comedians_with_images(phone_number):
    """Send comedians with their images separately, then show list button"""
    comedians = Comedian.objects.filter(is_active=True)
    
    if not comedians.exists():
        send_text_message(phone_number, "Hakuna comedians waliopo kwa sasa.")
        return
    
    # Send each comedian with their image
    for comedian in comedians:
        if comedian.image:
            # Send image with comedian name
            send_image_message(phone_number, comedian.image.url, f"🎭 {comedian.name}")
        else:
            # Send just the name if no image
            send_text_message(phone_number, f"🎭 {comedian.name}")
        
        # Small delay between messages
        import time
        time.sleep(1)
    
    # After showing all comedians, send the list button
    send_comedians_list_button(phone_number)


def send_image_message(phone_number, image_url, caption=""):
    """Send an image message"""
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }
    return whatsapp_api_call(payload)


def send_comedians_list_button(phone_number):
    """Send button to show comedians list"""
    header = "Comedians Wameonyeshwa"
    body = "Hapa juu ni comedians wote. Sasa bonyeza 'Chagua Comedian' ili uweze kumpigia kura comedian wako pendwa."
    footer = "Chagua chini ili uendelee"
    
    buttons = [
        {
            "type": "reply",
            "reply": {
                "id": "show_comedians_list",
                "title": "Chagua Comedian"
            }
        }
    ]
    
    send_interactive_message(phone_number, header, body, footer, buttons)


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




def generate_tickets(vote):
    """Generate tickets for a vote"""
    # Generate tickets based on quantity (5 votes = 6 tickets as per requirement)
    ticket_count = vote.quantity
    if vote.quantity == 5:
        ticket_count = 6  # Special case: 5 votes = 6 tickets
    
    for _ in range(ticket_count):
        Ticket.objects.create(vote=vote)


def ask_for_payment_phone(phone_number, vote):
    """Ask user for payment phone number"""
    header = f"Malipo ya {vote.quantity} Kura"
    body = f"""Umempigia kura {vote.comedian.name} - {vote.quantity} kura (TZS {vote.amount:,})

Tafadhali andika nambari ya simu yako ya malipo:
Mfano: 255123456789

Nambari hii itatumika kwa malipo ya mobile money."""
    footer = "Andika nambari ya simu"
    
    # Set session to wait for phone number
    set_user_session(phone_number, {
        'comedian_id': vote.comedian.id,
        'vote_id': vote.id,
        'step': 'waiting_for_payment_phone'
    })
    
    send_text_message(phone_number, f"{header}\n\n{body}\n\n{footer}")


def handle_payment_phone_input(phone_number, payment_phone):
    """Handle payment phone number input"""
    # Validate phone number format
    if not payment_phone.isdigit() or len(payment_phone) < 10:
        send_text_message(phone_number, "Nambari ya simu si sahihi. Tafadhali andika nambari sahihi.\n\nMfano: 255123456789")
        return
    
    # Get the vote from session
    session_data = get_user_session(phone_number)
    if not session_data or 'vote_id' not in session_data:
        send_text_message(phone_number, "Kuna hitilafu. Tafadhali anza upya.")
        clear_user_session(phone_number)
        return
    
    try:
        vote = Vote.objects.get(id=session_data['vote_id'])
        
        # Create payment record
        payment = Payment.objects.create(
            vote=vote,
            amount=vote.amount,
            status='pending',
            payment_method='mobile_money',
            payment_phone_number=payment_phone
        )
        
        # Update session
        set_user_session(phone_number, {
            'comedian_id': vote.comedian.id,
            'vote_id': vote.id,
            'payment_id': payment.payment_id,
            'step': 'processing_payment'
        })
        
        # Initiate payment
        initiate_payment_process(phone_number, payment, payment_phone)
        
    except Vote.DoesNotExist:
        send_text_message(phone_number, "Kuna hitilafu. Tafadhali anza upya.")
        clear_user_session(phone_number)


def initiate_payment_process(phone_number, payment, payment_phone):
    """Initiate the actual payment process"""
    try:
        # Send payment initiation message
        send_text_message(phone_number, f"Tunaanzisha malipo ya TZS {payment.amount:,}...\n\nTafadhali subiri kidogo...")
        
        # Initiate payment
        payment_result = initiate_payment(
            phone_number=payment_phone,
            amount=float(payment.amount),
            package_id=f"vote_{payment.vote.id}"
        )
        
        if payment_result['success']:
            # Update payment record
            payment.status = 'initiated'
            payment.gateway_transaction_id = payment_result['transaction_id']
            payment.gateway_reference = payment_result.get('reference', '')
            payment.gateway_response = payment_result.get('gateway_response', {})
            payment.save()
            
            # Send payment prompt message
            send_text_message(phone_number, f"✅ Malipo yameanzishwa!\n\nNambari ya malipo: {payment_result['transaction_id']}\n\nTafadhali angalia simu yako na fanya malipo.\n\nUtapata ujumbe wa uthibitisho baada ya dakika 1 (60 sekunde).")
            
            # Set up payment status checking
            check_payment_status_after_delay(phone_number, payment)
            
        else:
            # Payment initiation failed
            payment.status = 'failed'
            payment.gateway_response = payment_result
            payment.save()
            
            send_text_message(phone_number, f"❌ Malipo hayajaweza kuanzishwa.\n\nHitilafu: {payment_result['message']}\n\nTafadhali jaribu tena baadaye.")
            clear_user_session(phone_number)
            
    except Exception as e:
        log_error(f"Payment initiation error: {str(e)}", phone_number, {'payment_id': payment.payment_id})
        send_text_message(phone_number, "Kuna hitilafu katika malipo. Tafadhali jaribu tena baadaye.")
        clear_user_session(phone_number)


def clear_payment_session(phone_number):
    """Clear any ongoing payment sessions for a user"""
    try:
        # Find any pending payments for this user
        pending_payments = Payment.objects.filter(
            vote__phone_number=phone_number,
            status__in=['pending', 'initiated']
        )
        
        for payment in pending_payments:
            payment.status = 'cancelled'
            payment.save()
            log_payment(phone_number, payment.amount, 'cancelled_by_user', payment.gateway_transaction_id)
        
        log_message(phone_number, 'payment_session_cleared', f"Cleared {pending_payments.count()} pending payments")
        
    except Exception as e:
        log_error(f"Error clearing payment session: {str(e)}", phone_number)


def send_payment_status_message(phone_number, payment, status):
    """Send payment status message with interactive buttons"""
    header = "⏳ Malipo yako bado yanasubiri uthibitisho"
    body = f"""Hali: {status}

Nambari ya malipo: {payment.gateway_transaction_id}

Utapata ujumbe wa uthibitisho mara tu malipo yatakapokamilika.

Je, umeshafanya malipo au unataka kughairi?"""
    footer = "Chagua chini"
    
    buttons = [
        {
            "type": "reply",
            "reply": {
                "id": f"payment_confirmed_{payment.gateway_transaction_id}",
                "title": "Nimeshalipia"
            }
        },
        {
            "type": "reply",
            "reply": {
                "id": f"payment_cancelled_{payment.gateway_transaction_id}",
                "title": "Nimeghairi"
            }
        }
    ]
    
    send_interactive_message(phone_number, header, body, footer, buttons)


def handle_payment_confirmation(phone_number, transaction_id):
    """Handle when user confirms they have paid"""
    try:
        # Find the payment by transaction ID
        payment = Payment.objects.filter(
            gateway_transaction_id=transaction_id,
            vote__phone_number=phone_number,
            status__in=['pending', 'initiated']
        ).first()
        
        if not payment:
            send_text_message(phone_number, "Malipo huo haujapatikana. Tafadhali jaribu tena.")
            return
        
        # Check payment status again
        status_result = check_payment_status(
            transaction_id=payment.gateway_transaction_id,
            reference_id=payment.gateway_reference
        )
        
        if status_result['success']:
            if status_result['status'] == 'paid':
                # Payment confirmed successful
                payment.status = 'paid'
                payment.vote.is_paid = True
                payment.vote.save()
                payment.save()
                
                # Generate tickets
                generate_tickets(payment.vote)
                
                # Send success message
                send_payment_confirmation(phone_number, payment.vote)
                clear_user_session(phone_number)
                log_payment(phone_number, payment.amount, 'confirmed_paid', payment.gateway_transaction_id)
                
            else:
                # Payment still not confirmed by gateway
                send_text_message(phone_number, f"⏳ Malipo bado haujathibitishwa na mfumo wa malipo.\n\nHali: {status_result['status']}\n\nTafadhali subiri kidogo au wasiliana na msaada wa kiufundi.")
                log_payment(phone_number, payment.amount, 'user_confirmed_but_gateway_pending', payment.gateway_transaction_id)
        else:
            # Status check failed
            send_text_message(phone_number, f"❌ Hajaweza kuangalia hali ya malipo.\n\nHitilafu: {status_result.get('message', 'Unknown error')}\n\nTafadhali jaribu tena baadaye.")
            
    except Exception as e:
        log_error(f"Error handling payment confirmation: {str(e)}", phone_number)
        send_text_message(phone_number, "Kuna hitilafu katika kuthibitisha malipo. Tafadhali jaribu tena baadaye.")


def handle_payment_cancellation(phone_number, transaction_id):
    """Handle when user wants to cancel payment"""
    try:
        # Find the payment by transaction ID
        payment = Payment.objects.filter(
            gateway_transaction_id=transaction_id,
            vote__phone_number=phone_number,
            status__in=['pending', 'initiated']
        ).first()
        
        if not payment:
            send_text_message(phone_number, "Malipo huo haujapatikana. Tafadhali jaribu tena.")
            return
        
        # Cancel the payment
        payment.status = 'cancelled'
        payment.save()
        
        # Clear user session
        clear_user_session(phone_number)
        clear_payment_session(phone_number)
        
        # Send cancellation message
        send_text_message(phone_number, "❌ Malipo yameghairiwa.\n\nSession imefutwa. Unaweza kuanza upya.")
        
        # Send welcome message
        user, is_new_user = get_or_create_user(phone_number)
        send_welcome_message(phone_number, is_new_user)
        
        log_payment(phone_number, payment.amount, 'cancelled_by_user', payment.gateway_transaction_id)
        
    except Exception as e:
        log_error(f"Error handling payment cancellation: {str(e)}", phone_number)
        send_text_message(phone_number, "Kuna hitilafu katika kughairi malipo. Tafadhali jaribu tena baadaye.")


def check_payment_status_manual(phone_number):
    """Manually check payment status for a user"""
    try:
        # Find any pending payments for this user
        pending_payments = Payment.objects.filter(
            vote__phone_number=phone_number,
            status__in=['pending', 'initiated']
        )
        
        if not pending_payments.exists():
            send_text_message(phone_number, "Hakuna malipo yanayosubiri uthibitisho.")
            return
        
        for payment in pending_payments:
            # Check payment status
            status_result = check_payment_status(
                transaction_id=payment.gateway_transaction_id,
                reference_id=payment.gateway_reference
            )
            
            if status_result['success']:
                if status_result['status'] == 'paid':
                    # Payment successful
                    payment.status = 'paid'
                    payment.vote.is_paid = True
                    payment.vote.save()
                    payment.save()
                    
                    # Generate tickets
                    generate_tickets(payment.vote)
                    
                    # Send success message
                    send_payment_confirmation(phone_number, payment.vote)
                    clear_user_session(phone_number)
                    log_payment(phone_number, payment.amount, 'completed_manual', payment.gateway_transaction_id)
                    return
                    
                elif status_result['status'] in ['failed', 'cancelled', 'expired']:
                    # Payment failed
                    payment.status = status_result['status']
                    payment.save()
                    
                    send_text_message(phone_number, f"❌ Malipo yamekataliwa au yameisha muda.\n\nHali: {status_result['status']}\n\nTafadhali jaribu tena.")
                    clear_user_session(phone_number)
                    log_payment(phone_number, payment.amount, f'failed_manual_{status_result["status"]}', payment.gateway_transaction_id)
                    return
                    
                else:
                    # Still pending - send interactive message with buttons
                    send_payment_status_message(phone_number, payment, status_result['status'])
                    return
            else:
                # Status check failed
                send_text_message(phone_number, f"❌ Hajaweza kuangalia hali ya malipo.\n\nHitilafu: {status_result.get('message', 'Unknown error')}\n\nTafadhali jaribu tena baadaye.")
                return
                
    except Exception as e:
        log_error(f"Error checking payment status manually: {str(e)}", phone_number)
        send_text_message(phone_number, "Kuna hitilafu katika kuangalia hali ya malipo. Tafadhali jaribu tena baadaye.")


def check_payment_status_after_delay(phone_number, payment):
    """Check payment status after a delay"""
    import threading
    import time
    
    def check_status():
        try:
            # Wait 60 seconds before first check
            time.sleep(60)
            
            # Check if payment still exists and is not cancelled
            try:
                payment.refresh_from_db()
                if payment.status in ['cancelled', 'paid', 'failed', 'expired']:
                    log_message(phone_number, 'payment_already_processed', f"Payment {payment.gateway_transaction_id} already processed with status: {payment.status}")
                    return  # Payment already processed
            except Payment.DoesNotExist:
                log_message(phone_number, 'payment_not_found', f"Payment {payment.gateway_transaction_id} no longer exists")
                return  # Payment no longer exists
            
            # Check payment status
            status_result = check_payment_status(
                transaction_id=payment.gateway_transaction_id,
                reference_id=payment.gateway_reference
            )
            
            if status_result['success']:
                if status_result['status'] == 'paid':
                    # Payment successful
                    payment.status = 'paid'
                    payment.vote.is_paid = True
                    payment.vote.save()
                    payment.save()
                    
                    # Generate tickets
                    generate_tickets(payment.vote)
                    
                    # Send success message
                    send_payment_confirmation(phone_number, payment.vote)
                    clear_user_session(phone_number)
                    log_payment(phone_number, payment.amount, 'completed', payment.gateway_transaction_id)
                    
                elif status_result['status'] in ['failed', 'cancelled', 'expired']:
                    # Payment failed
                    payment.status = status_result['status']
                    payment.save()
                    
                    send_text_message(phone_number, f"❌ Malipo yamekataliwa au yameisha muda.\n\nHali: {status_result['status']}\n\nTafadhali jaribu tena.")
                    clear_user_session(phone_number)
                    log_payment(phone_number, payment.amount, f'failed_{status_result["status"]}', payment.gateway_transaction_id)
                    
                elif status_result['status'] == 'unknown':
                    # Status unknown, check if payment is still pending after reasonable time
                    # If it's been more than 5 minutes, assume it failed
                    time_since_initiated = time.time() - payment.created_at.timestamp()
                    if time_since_initiated > 300:  # 5 minutes
                        payment.status = 'expired'
                        payment.save()
                        
                        send_text_message(phone_number, f"⏰ Malipo yameisha muda.\n\nMalipo hayajakamilika ndani ya muda uliopangwa.\n\nTafadhali jaribu tena.")
                        clear_user_session(phone_number)
                        log_payment(phone_number, payment.amount, 'expired_timeout', payment.gateway_transaction_id)
                    else:
                        # Still within reasonable time, send status message with buttons
                        send_payment_status_message(phone_number, payment, status_result['status'])
                        log_message(phone_number, 'payment_status_unknown', f"Payment {payment.gateway_transaction_id} status unknown, sent interactive message")
                else:
                    # Still pending, send status message with buttons
                    send_payment_status_message(phone_number, payment, status_result['status'])
                    log_message(phone_number, 'payment_still_pending', f"Payment {payment.gateway_transaction_id} still pending, sent interactive message")
            else:
                # Status check failed, send status message with buttons
                send_payment_status_message(phone_number, payment, 'unknown')
                log_error(f"Payment status check failed: {status_result.get('message', 'Unknown error')}", phone_number, {'payment_id': payment.gateway_transaction_id})
                
        except Exception as e:
            log_error(f"Error in payment status check thread: {str(e)}", phone_number, {'payment_id': payment.gateway_transaction_id})
            # Send status message with buttons as fallback
            try:
                send_payment_status_message(phone_number, payment, 'unknown')
            except:
                send_text_message(phone_number, "Kuna hitilafu katika kuangalia hali ya malipo. Tafadhali tumia 'status' au 'hali' kuangalia tena.")
    
    # Start the status checking in a separate thread
    thread = threading.Thread(target=check_status)
    thread.daemon = True
    thread.start()


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