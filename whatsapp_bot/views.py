import json
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Comedian, VotingSession, Vote, Ticket, Payment
from .utils import whatsapp_api_call, process_message


@csrf_exempt
def webhook(request):
    """WhatsApp webhook endpoint"""
    if request.method == 'GET':
        # Verification logic
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        
        if mode == 'subscribe' and token == settings.WHATSAPP_VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        return HttpResponse('Verification failed', status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entry_time = timezone.now()
            print(f"Webhook received at {entry_time}")
            
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value')
                    if value and 'messages' in value:
                        process_message(value)
            return HttpResponse('OK', status=200)
        except Exception as e:
            print(f"Webhook error at {timezone.now()}: {str(e)}")
            return HttpResponse('Error', status=500)


@api_view(['GET'])
def get_votes(request):
    """API endpoint to view all votes"""
    votes = Vote.objects.select_related('comedian', 'voting_session').all()
    data = []
    
    for vote in votes:
        data.append({
            'id': vote.id,
            'comedian': vote.comedian.name,
            'phone_number': vote.phone_number,
            'quantity': vote.quantity,
            'amount': float(vote.amount),
            'is_paid': vote.is_paid,
            'created_at': vote.created_at.isoformat(),
            'tickets': [ticket.ticket_code for ticket in vote.tickets.all()]
        })
    
    return Response(data)


@api_view(['GET'])
def get_vote_stats(request):
    """API endpoint to get voting statistics"""
    active_session = VotingSession.objects.filter(is_active=True).first()
    if not active_session:
        return Response({'error': 'No active voting session'}, status=404)
    
    votes = Vote.objects.filter(voting_session=active_session)
    
    comedian_stats = {}
    for comedian in Comedian.objects.filter(is_active=True):
        comedian_votes = votes.filter(comedian=comedian)
        total_votes = sum(vote.quantity for vote in comedian_votes)
        total_amount = sum(float(vote.amount) for vote in comedian_votes)
        
        comedian_stats[comedian.name] = {
            'total_votes': total_votes,
            'total_amount': total_amount,
            'vote_count': comedian_votes.count()
        }
    
    return Response({
        'session': {
            'name': active_session.name,
            'end_date': active_session.end_date.isoformat(),
            'winner_announcement_date': active_session.winner_announcement_date.isoformat()
        },
        'comedian_stats': comedian_stats,
        'total_votes': sum(vote.quantity for vote in votes),
        'total_amount': sum(float(vote.amount) for vote in votes)
    })


@api_view(['POST'])
def create_test_data(request):
    """Create test data for development"""
    # Create comedians
    comedians_data = ['Eliud', 'Nanga', 'Brother K', 'Ndaro', 'Steve Mweusi']
    for name in comedians_data:
        Comedian.objects.get_or_create(name=name)
    
    # Create voting session
    session, created = VotingSession.objects.get_or_create(
        name="Comedian Bora wa Mwezi - October 2024",
        defaults={
            'end_date': timezone.now() + timezone.timedelta(days=30),
            'winner_announcement_date': timezone.now() + timezone.timedelta(days=35)
        }
    )
    
    return Response({'message': 'Test data created successfully'})
