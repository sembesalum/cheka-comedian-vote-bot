import json
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Comedian, VotingSession, Vote, Ticket, Payment
from .utils import whatsapp_api_call, process_message
from .logger import log_webhook, log_error, log_message


@csrf_exempt
def webhook(request):
    """WhatsApp webhook endpoint"""
    if request.method == 'GET':
        # Verification logic
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        log_webhook({
            'method': 'GET',
            'mode': mode,
            'token': token[:10] + '...' if token else None,
            'challenge': challenge
        }, 'verification_attempt')
        
        if mode == 'subscribe' and token == settings.WHATSAPP_VERIFY_TOKEN:
            log_webhook({'challenge': challenge}, 'verification_success')
            return HttpResponse(challenge, status=200)
        
        log_webhook({'mode': mode, 'token_match': token == settings.WHATSAPP_VERIFY_TOKEN}, 'verification_failed')
        return HttpResponse('Verification failed', status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entry_time = timezone.now()
            
            log_webhook({
                'method': 'POST',
                'timestamp': entry_time.isoformat(),
                'entries_count': len(data.get('entry', [])),
                'raw_data': data
            }, 'received')
            
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value')
                    if value and 'messages' in value:
                        # Log each message
                        for message in value.get('messages', []):
                            phone_number = message.get('from', 'unknown')
                            message_type = message.get('type', 'unknown')
                            log_message(phone_number, message_type, message)
                        
                        process_message(value)
            
            log_webhook({'status': 'processed'}, 'success')
            return HttpResponse('OK', status=200)
            
        except json.JSONDecodeError as e:
            log_error(f"JSON decode error: {str(e)}", extra_data={'body': request.body})
            return HttpResponse('Invalid JSON', status=400)
        except Exception as e:
            log_error(f"Webhook processing error: {str(e)}", extra_data={'body': request.body})
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


@api_view(['GET'])
def view_logs(request):
    """View logs for debugging on PythonAnywhere"""
    import os
    from django.conf import settings
    
    log_file = os.path.join(settings.BASE_DIR, 'logs', 'whatsapp_bot.log')
    
    try:
        with open(log_file, 'r') as f:
            logs = f.readlines()
        
        # Get last 100 lines
        recent_logs = logs[-100:] if len(logs) > 100 else logs
        
        return Response({
            'log_file': log_file,
            'total_lines': len(logs),
            'recent_lines': len(recent_logs),
            'logs': recent_logs
        })
    except FileNotFoundError:
        return Response({'error': 'Log file not found'}, status=404)
    except Exception as e:
        log_error(f"Error reading logs: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def view_errors(request):
    """View only error logs"""
    import os
    from django.conf import settings
    
    log_file = os.path.join(settings.BASE_DIR, 'logs', 'whatsapp_bot.log')
    
    try:
        with open(log_file, 'r') as f:
            logs = f.readlines()
        
        # Filter error logs
        error_logs = [log for log in logs if 'ERROR' in log]
        
        return Response({
            'log_file': log_file,
            'total_errors': len(error_logs),
            'errors': error_logs[-50:] if len(error_logs) > 50 else error_logs
        })
    except FileNotFoundError:
        return Response({'error': 'Log file not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


def logs_view(request):
    """HTML view for logs"""
    import os
    from django.conf import settings
    
    log_file = os.path.join(settings.BASE_DIR, 'logs', 'whatsapp_bot.log')
    
    try:
        with open(log_file, 'r') as f:
            logs = f.readlines()
        
        # Get last 100 lines
        recent_logs = logs[-100:] if len(logs) > 100 else logs
        
        context = {
            'log_file': log_file,
            'total_lines': len(logs),
            'recent_lines': len(recent_logs),
            'logs': recent_logs
        }
        
        return render(request, 'logs.html', context)
    except FileNotFoundError:
        context = {
            'log_file': log_file,
            'total_lines': 0,
            'recent_lines': 0,
            'logs': ['Log file not found. Bot may not have been used yet.']
        }
        return render(request, 'logs.html', context)
    except Exception as e:
        context = {
            'log_file': log_file,
            'total_lines': 0,
            'recent_lines': 0,
            'logs': [f'Error reading logs: {str(e)}']
        }
        return render(request, 'logs.html', context)
