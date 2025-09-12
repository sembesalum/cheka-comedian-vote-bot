#!/usr/bin/env python3
"""
Simple test script to verify API endpoints
Run this after starting the Django server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("Testing Comedian Voting Bot API Endpoints...")
    print("=" * 50)
    
    # Test 1: Create test data
    print("1. Creating test data...")
    try:
        response = requests.post(f"{BASE_URL}/api/create-test-data/")
        if response.status_code == 200:
            print("✓ Test data created successfully")
        else:
            print(f"✗ Failed to create test data: {response.status_code}")
    except Exception as e:
        print(f"✗ Error creating test data: {e}")
    
    print()
    
    # Test 2: Get votes
    print("2. Getting votes...")
    try:
        response = requests.get(f"{BASE_URL}/api/votes/")
        if response.status_code == 200:
            votes = response.json()
            print(f"✓ Found {len(votes)} votes")
            if votes:
                print(f"  Sample vote: {votes[0]}")
        else:
            print(f"✗ Failed to get votes: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting votes: {e}")
    
    print()
    
    # Test 3: Get vote stats
    print("3. Getting vote statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/vote-stats/")
        if response.status_code == 200:
            stats = response.json()
            print("✓ Vote statistics retrieved successfully")
            print(f"  Session: {stats.get('session', {}).get('name', 'N/A')}")
            print(f"  Total votes: {stats.get('total_votes', 0)}")
            print(f"  Total amount: TZS {stats.get('total_amount', 0)}")
        else:
            print(f"✗ Failed to get vote stats: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting vote stats: {e}")
    
    print()
    
    # Test 4: Test webhook (GET)
    print("4. Testing webhook verification...")
    try:
        response = requests.get(f"{BASE_URL}/webhook/?hub.mode=subscribe&hub.verify_token=c2a49926-a81c-11ef-b864-0242ac120002&hub.challenge=test123")
        if response.status_code == 200:
            print("✓ Webhook verification working")
        else:
            print(f"✗ Webhook verification failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing webhook: {e}")
    
    print()
    print("=" * 50)
    print("API testing completed!")

if __name__ == "__main__":
    test_endpoints()
