import uuid
import json
import requests
from datetime import datetime
from django.conf import settings
from .logger import log_payment, log_error

def initiate_payment(phone_number, amount, package_id=None, agent_id=None, api_key=None, webhook_url=None):
    """
    Initiates a payment using Swahilies API (or any mobile money API)
    
    Args:
        phone_number (str): Customer's phone number
        amount (float): Payment amount
        package_id (str, optional): Package/plan ID if applicable
        agent_id (str, optional): Agent ID if applicable
        api_key (str): API key for payment gateway
        webhook_url (str): Webhook URL for payment confirmation
    
    Returns:
        dict: Response with payment details or error message
    """
    
    try:
        # Generate unique transaction ID
        transaction_id = uuid.uuid4().hex
        
        # Payment gateway configuration (Swahilies API example)
        payment_gateway_url = 'https://swahiliesapi.invict.site/Api'
        
        # Default API key if not provided (replace with your actual key)
        if not api_key:
            api_key = "YzFhMmU2MzBlYzViNDY3NGIyYjc1N2NjZmU1YTEzNjA="
        
        # Default webhook URL if not provided
        if not webhook_url:
            webhook_url = f"https://{settings.ALLOWED_HOSTS[0]}/webhook/payment/"
        
        # Prepare payment data
        payment_data = {
            "api": 170,
            "code": 104,
            "data": {
                "api_key": api_key,
                "order_id": transaction_id,
                "amount": int(amount),
                "is_live": True,  # Set to False for testing
                "phone_number": phone_number,
                "webhook_url": webhook_url
            }
        }
        
        # Request headers
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Make API request
        response = requests.post(
            payment_gateway_url, 
            json=payment_data, 
            headers=headers,
            timeout=30
        )
        
        # Parse response
        response_data = json.loads(response.text)
        
        if response_data.get('code') == 200:
            # Payment initiated successfully
            reference = json.loads(response_data.get('selcom', '{}')).get('reference', '')
            
            # Log payment initiation
            log_payment(phone_number, amount, 'initiated', transaction_id, {
                'reference': reference,
                'gateway_response': response_data
            })
            
            return {
                'success': True,
                'message': 'Payment initiated successfully. Please check your phone for payment prompt.',
                'transaction_id': transaction_id,
                'reference': reference,
                'gateway_response': response_data
            }
        else:
            log_error(f"Payment initiation failed: {response_data.get('message', 'Unknown error')}", phone_number, {
                'transaction_id': transaction_id,
                'gateway_response': response_data
            })
            
            return {
                'success': False,
                'message': 'Failed to initiate payment',
                'error': response_data.get('message', 'Unknown error'),
                'transaction_id': transaction_id
            }
            
    except requests.exceptions.RequestException as e:
        log_error(f"Payment network error: {str(e)}", phone_number, {'transaction_id': transaction_id})
        return {
            'success': False,
            'message': 'Network error occurred',
            'error': str(e),
            'transaction_id': transaction_id if 'transaction_id' in locals() else None
        }
    except json.JSONDecodeError as e:
        log_error(f"Payment response parsing error: {str(e)}", phone_number, {'transaction_id': transaction_id})
        return {
            'success': False,
            'message': 'Invalid response from payment gateway',
            'error': str(e),
            'transaction_id': transaction_id if 'transaction_id' in locals() else None
        }
    except Exception as e:
        log_error(f"Payment initiation error: {str(e)}", phone_number, {'transaction_id': transaction_id})
        return {
            'success': False,
            'message': 'An unexpected error occurred',
            'error': str(e),
            'transaction_id': transaction_id if 'transaction_id' in locals() else None
        }


def check_payment_status(transaction_id, reference_id=None, api_key=None):
    """
    Checks the status of a payment transaction
    
    Args:
        transaction_id (str): The transaction ID to check
        reference_id (str, optional): Reference ID from payment gateway
        api_key (str): API key for payment gateway
    
    Returns:
        dict: Payment status and details
    """
    
    try:
        # Default API key if not provided
        if not api_key:
            api_key = "YzFhMmU2MzBlYzViNDY3NGIyYjc1N2NjZmU1YTEzNjA="
        
        # Payment gateway status check URL (Swahilies API example)
        status_url = 'https://swahiliesapi.invict.site/Api'
        
        # Prepare status check data
        status_data = {
            "api": 170,
            "code": 105,  # Different code for status check
            "data": {
                "api_key": api_key,
                "order_id": transaction_id,
                "reference_id": reference_id or transaction_id
            }
        }
        
        # Request headers
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Make API request
        response = requests.post(
            status_url, 
            json=status_data, 
            headers=headers,
            timeout=30
        )
        
        # Parse response
        response_data = json.loads(response.text)
        
        if response_data.get('code') == 200:
            # Get transaction status from response
            transaction_status = response_data.get('data', {}).get('status', 'unknown')
            
            # Map gateway status to your system status
            status_mapping = {
                'completed': 'paid',
                'success': 'paid',
                'pending': 'pending',
                'failed': 'failed',
                'cancelled': 'cancelled',
                'expired': 'expired'
            }
            
            mapped_status = status_mapping.get(transaction_status.lower(), 'unknown')
            
            log_payment('system', 0, f'status_check_{mapped_status}', transaction_id, {
                'gateway_status': transaction_status,
                'mapped_status': mapped_status,
                'gateway_response': response_data
            })
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'status': mapped_status,
                'gateway_status': transaction_status,
                'message': f'Payment status: {mapped_status}',
                'details': response_data.get('data', {}),
                'checked_at': datetime.now().isoformat()
            }
        else:
            log_error(f"Payment status check failed: {response_data.get('message', 'Unknown error')}", 'system', {
                'transaction_id': transaction_id,
                'gateway_response': response_data
            })
            
            return {
                'success': False,
                'transaction_id': transaction_id,
                'status': 'unknown',
                'message': 'Failed to check payment status',
                'error': response_data.get('message', 'Unknown error'),
                'checked_at': datetime.now().isoformat()
            }
            
    except requests.exceptions.RequestException as e:
        log_error(f"Payment status check network error: {str(e)}", 'system', {'transaction_id': transaction_id})
        return {
            'success': False,
            'transaction_id': transaction_id,
            'status': 'unknown',
            'message': 'Network error occurred while checking status',
            'error': str(e),
            'checked_at': datetime.now().isoformat()
        }
    except json.JSONDecodeError as e:
        log_error(f"Payment status response parsing error: {str(e)}", 'system', {'transaction_id': transaction_id})
        return {
            'success': False,
            'transaction_id': transaction_id,
            'status': 'unknown',
            'message': 'Invalid response from payment gateway',
            'error': str(e),
            'checked_at': datetime.now().isoformat()
        }
    except Exception as e:
        log_error(f"Payment status check error: {str(e)}", 'system', {'transaction_id': transaction_id})
        return {
            'success': False,
            'transaction_id': transaction_id,
            'status': 'unknown',
            'message': 'An unexpected error occurred',
            'error': str(e),
            'checked_at': datetime.now().isoformat()
        }
