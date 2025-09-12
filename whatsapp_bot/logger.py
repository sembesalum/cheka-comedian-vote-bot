import logging
import os
from django.conf import settings

def setup_logger():
    """Setup logging configuration for the WhatsApp bot"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'whatsapp_bot.log')),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create specific loggers
    webhook_logger = logging.getLogger('webhook')
    message_logger = logging.getLogger('message')
    error_logger = logging.getLogger('error')
    payment_logger = logging.getLogger('payment')
    
    return {
        'webhook': webhook_logger,
        'message': message_logger,
        'error': error_logger,
        'payment': payment_logger
    }

# Initialize loggers
loggers = setup_logger()

def log_webhook(data, status='received'):
    """Log webhook events"""
    loggers['webhook'].info(f"Webhook {status}: {data}")

def log_message(phone_number, message_type, content):
    """Log message processing"""
    loggers['message'].info(f"Message from {phone_number} - Type: {message_type} - Content: {content}")

def log_error(error_message, phone_number=None, extra_data=None):
    """Log errors with context"""
    context = f"Phone: {phone_number}" if phone_number else "System"
    extra = f" - Extra: {extra_data}" if extra_data else ""
    loggers['error'].error(f"ERROR [{context}]: {error_message}{extra}")

def log_payment(phone_number, amount, status, transaction_id=None):
    """Log payment events"""
    tx_info = f" - TX: {transaction_id}" if transaction_id else ""
    loggers['payment'].info(f"Payment [{phone_number}]: {status} - Amount: {amount}{tx_info}")

def log_session(phone_number, action, session_data=None):
    """Log session management events"""
    data = f" - Data: {session_data}" if session_data else ""
    loggers['message'].info(f"Session [{phone_number}]: {action}{data}")
