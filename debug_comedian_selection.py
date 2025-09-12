#!/usr/bin/env python3
"""
Debug script to test comedian selection
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/salum_sembe/backend/chekabot')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comedian_voting_bot.settings')
django.setup()

from whatsapp_bot.models import Comedian

def debug_comedian_selection():
    """Debug comedian selection logic"""
    print("🔍 Debugging Comedian Selection")
    print("=" * 50)
    
    # Get all comedians
    comedians = Comedian.objects.filter(is_active=True)
    print(f"Found {comedians.count()} active comedians:")
    
    for comedian in comedians:
        # Show how the ID is created
        comedian_id = f"comedian_{comedian.name.lower().replace(' ', '_')}"
        print(f"  - Name: '{comedian.name}'")
        print(f"    ID: '{comedian_id}'")
        
        # Test the reverse conversion
        test_id = comedian_id.replace('comedian_', '')
        test_name1 = test_id.replace('_', ' ')
        test_name2 = test_id.replace('_', ' ').title()
        
        print(f"    Reverse 1: '{test_name1}'")
        print(f"    Reverse 2: '{test_name2}'")
        
        # Test database lookup
        try:
            found1 = Comedian.objects.get(name__iexact=test_name1)
            print(f"    ✅ Found with method 1: {found1.name}")
        except Comedian.DoesNotExist:
            print(f"    ❌ Not found with method 1")
        
        try:
            found2 = Comedian.objects.get(name__iexact=test_name2)
            print(f"    ✅ Found with method 2: {found2.name}")
        except Comedian.DoesNotExist:
            print(f"    ❌ Not found with method 2")
        
        print()

if __name__ == "__main__":
    debug_comedian_selection()
