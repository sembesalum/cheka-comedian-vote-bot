#!/usr/bin/env python3
"""
Test script to verify session clearing on user deletion
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/salum_sembe/backend/chekabot')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comedian_voting_bot.settings')
django.setup()

from whatsapp_bot.models import User
from whatsapp_bot.session_functions import clear_user_session, has_ongoing_session, set_user_session
from whatsapp_bot.admin_views import delete_user
from django.test import RequestFactory

def test_session_clearing():
    """Test that user deletion clears session"""
    print("🧪 Testing Session Clearing on User Deletion")
    print("=" * 50)
    
    # Create a test user
    phone_number = "255123456789"
    user = User.objects.create(phone_number=phone_number)
    print(f"✅ Created test user: {phone_number}")
    
    # Set a session for the user
    set_user_session(phone_number, {"step": "voting", "comedian": "Test Comedian"})
    print(f"✅ Set session for user: {phone_number}")
    
    # Verify session exists
    has_session = has_ongoing_session(phone_number)
    print(f"✅ User has ongoing session: {has_session}")
    
    # Simulate admin deletion
    factory = RequestFactory()
    request = factory.post(f'/admin/delete-user/{user.id}/')
    
    # Call the delete function
    response = delete_user(request, user.id)
    print(f"✅ Delete response: {response.status_code}")
    
    # Check if user still exists
    try:
        User.objects.get(phone_number=phone_number)
        print("❌ User still exists in database")
    except User.DoesNotExist:
        print("✅ User deleted from database")
    
    # Check if session still exists
    has_session_after = has_ongoing_session(phone_number)
    print(f"✅ User has session after deletion: {has_session_after}")
    
    if not has_session_after:
        print("🎉 SUCCESS: Session was cleared when user was deleted!")
    else:
        print("❌ FAILED: Session was not cleared")
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"   - User created: ✅")
    print(f"   - Session set: ✅")
    print(f"   - User deleted: {'✅' if not User.objects.filter(phone_number=phone_number).exists() else '❌'}")
    print(f"   - Session cleared: {'✅' if not has_session_after else '❌'}")

if __name__ == "__main__":
    test_session_clearing()
