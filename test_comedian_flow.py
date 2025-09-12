#!/usr/bin/env python3
"""
Test script to simulate comedian selection flow
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/salum_sembe/backend/chekabot')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comedian_voting_bot.settings')
django.setup()

from whatsapp_bot.models import Comedian, VotingSession
from whatsapp_bot.utils import handle_list_selection

def test_comedian_selection():
    """Test comedian selection with actual list IDs"""
    print("🧪 Testing Comedian Selection Flow")
    print("=" * 50)
    
    # Get comedians and create the same IDs as in the actual flow
    comedians = Comedian.objects.filter(is_active=True)
    
    print("Testing each comedian selection:")
    for comedian in comedians:
        # Create the same ID format as in send_comedians_list
        comedian_id = f"comedian_{comedian.name.lower().replace(' ', '_')}"
        print(f"\nTesting: {comedian.name}")
        print(f"List ID: {comedian_id}")
        
        # Test the selection logic
        try:
            # Simulate the selection
            comedian_id_from_list = comedian_id.replace('comedian_', '')
            print(f"ID from list: {comedian_id_from_list}")
            
            # Test database lookup
            found_comedian = Comedian.objects.get(
                name__iexact=comedian_id_from_list.replace('_', ' ')
            )
            print(f"✅ Found comedian: {found_comedian.name}")
            
        except Comedian.DoesNotExist:
            print(f"❌ Comedian not found!")
            
            # Try alternative
            try:
                comedian_name = comedian_id_from_list.replace('_', ' ').title()
                found_comedian = Comedian.objects.get(name__iexact=comedian_name)
                print(f"✅ Found with alternative: {found_comedian.name}")
            except Comedian.DoesNotExist:
                print(f"❌ Alternative also failed!")

def test_actual_flow():
    """Test the actual flow with a mock phone number"""
    print("\n🔄 Testing Actual Flow")
    print("=" * 50)
    
    # Test with each comedian
    comedians = Comedian.objects.filter(is_active=True)
    test_phone = "255616107670"
    
    for comedian in comedians:
        comedian_id = f"comedian_{comedian.name.lower().replace(' ', '_')}"
        print(f"\nTesting flow for {comedian.name} (ID: {comedian_id})")
        
        try:
            # This will actually try to send WhatsApp messages
            handle_list_selection(test_phone, comedian_id)
            print(f"✅ Flow completed for {comedian.name}")
        except Exception as e:
            print(f"❌ Error in flow for {comedian.name}: {e}")

if __name__ == "__main__":
    test_comedian_selection()
    # Uncomment the next line to test actual WhatsApp flow
    # test_actual_flow()
