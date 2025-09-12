def has_ongoing_session(phone_number):
    """Check if user has an ongoing voting session"""
    from .models import Vote
    from django.core.cache import cache
    
    # Check for incomplete votes (not paid)
    incomplete_votes = Vote.objects.filter(
        phone_number=phone_number,
        is_paid=False
    ).exists()
    
    # Check cache for session state
    session_key = f"user_session_{phone_number}"
    cached_session = cache.get(session_key)
    
    return incomplete_votes or cached_session is not None


def clear_user_session(phone_number):
    """Clear user's ongoing session"""
    from .models import Vote
    from django.core.cache import cache
    
    # Delete incomplete votes
    Vote.objects.filter(
        phone_number=phone_number,
        is_paid=False
    ).delete()
    
    # Clear cache
    session_key = f"user_session_{phone_number}"
    cache.delete(session_key)


def send_ongoing_session_message(phone_number):
    """Send message for ongoing session"""
    from .utils import send_interactive_message
    
    header = "Session Inaendelea"
    body = """Umeingilia session ambayo tayar inaendelea.

Tafadhali bonyeza "Anza" ili uanze upya, au bonyeza "#" ili ufute session hii."""
    footer = "Chagua chini"
    
    buttons = [
        {
            "type": "reply",
            "reply": {
                "id": "start_voting",
                "title": "Anza"
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


def set_user_session(phone_number, session_data):
    """Set user session data in cache"""
    from django.core.cache import cache
    
    session_key = f"user_session_{phone_number}"
    cache.set(session_key, session_data, timeout=3600)  # 1 hour timeout


def get_user_session(phone_number):
    """Get user session data from cache"""
    from django.core.cache import cache
    
    session_key = f"user_session_{phone_number}"
    return cache.get(session_key)
