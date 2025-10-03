from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.cache import cache
from .models import User, WelcomeVideo, Comedian, Ad, NomineesImage, NBCLink
from .session_functions import clear_user_session
from .logger import log_session
import json


def user_management(request):
    """User management interface"""
    users = User.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        users = users.filter(phone_number__icontains=search)
    
    context = {
        'users': users,
        'search': search,
        'total_users': User.objects.count(),
        'new_users': User.objects.filter(is_first_time=True).count(),
        'returning_users': User.objects.filter(is_first_time=False).count(),
    }
    
    return render(request, 'admin/user_management.html', context)


def video_management(request):
    """Video management interface"""
    videos = WelcomeVideo.objects.all().order_by('order')
    
    context = {
        'videos': videos,
        'total_videos': videos.count(),
        'active_videos': videos.filter(is_active=True).count(),
    }
    
    return render(request, 'admin/video_management.html', context)


def comedian_management(request):
    """Comedian management interface"""
    comedians = Comedian.objects.all().order_by('name')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        comedians = comedians.filter(name__icontains=search)
    
    # Get the active nominees image
    nominees_image = NomineesImage.objects.filter(is_active=True).first()
    
    # Get the active NBC link
    nbc_link = NBCLink.objects.filter(is_active=True).first()
    
    context = {
        'comedians': comedians,
        'search': search,
        'total_comedians': Comedian.objects.count(),
        'active_comedians': Comedian.objects.filter(is_active=True).count(),
        'nominees_image': nominees_image,
        'nbc_link': nbc_link,
    }
    
    return render(request, 'admin/comedian_management.html', context)


def ads_management(request):
    """Ads management interface"""
    ads = Ad.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        ads = ads.filter(title__icontains=search)
    
    context = {
        'ads': ads,
        'search': search,
        'total_ads': Ad.objects.count(),
        'active_ads': Ad.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'admin/ads_management.html', context)


@csrf_exempt
def delete_user(request, user_id):
    """Delete user via AJAX"""
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=user_id)
            phone_number = user.phone_number
            
            # Clear user's session before deleting
            clear_user_session(phone_number)
            log_session(phone_number, 'user_deleted', f'User {phone_number} deleted from admin dashboard')
            
            # Delete the user
            user.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'User {phone_number} deleted successfully (session cleared)'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error deleting user: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def add_video(request):
    """Add new welcome video"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', '')
            video_url = data.get('video_url', '')
            order = data.get('order', 0)
            
            if not title or not video_url:
                return JsonResponse({
                    'success': False,
                    'message': 'Title and video URL are required'
                })
            
            video = WelcomeVideo.objects.create(
                title=title,
                video_url=video_url,
                order=order
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Video added successfully',
                'video': {
                    'id': video.id,
                    'title': video.title,
                    'video_url': video.video_url,
                    'order': video.order,
                    'is_active': video.is_active
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error adding video: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def update_video(request, video_id):
    """Update video"""
    if request.method == 'POST':
        try:
            video = get_object_or_404(WelcomeVideo, id=video_id)
            data = json.loads(request.body)
            
            video.title = data.get('title', video.title)
            video.video_url = data.get('video_url', video.video_url)
            video.order = data.get('order', video.order)
            video.is_active = data.get('is_active', video.is_active)
            video.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Video updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating video: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def delete_video(request, video_id):
    """Delete video"""
    if request.method == 'POST':
        try:
            video = get_object_or_404(WelcomeVideo, id=video_id)
            title = video.title
            video.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Video "{title}" deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error deleting video: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def update_comedian_image(request, comedian_id):
    """Update comedian image"""
    if request.method == 'POST':
        try:
            comedian = get_object_or_404(Comedian, id=comedian_id)
            
            if 'image' in request.FILES:
                comedian.image = request.FILES['image']
                comedian.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Image updated for {comedian.name}',
                    'image_url': comedian.image.url if comedian.image else None
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No image file provided'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating image: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def toggle_comedian_status(request, comedian_id):
    """Toggle comedian active status"""
    if request.method == 'POST':
        try:
            comedian = get_object_or_404(Comedian, id=comedian_id)
            comedian.is_active = not comedian.is_active
            comedian.save()
            
            status = 'activated' if comedian.is_active else 'deactivated'
            return JsonResponse({
                'success': True,
                'message': f'{comedian.name} {status} successfully',
                'is_active': comedian.is_active
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating status: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def add_ad(request):
    """Add new ad"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', '')
            sponsor_name = data.get('sponsor_name', 'NBC Kiganjani')
            description = data.get('description', '')
            
            if not title:
                return JsonResponse({
                    'success': False,
                    'message': 'Title is required'
                })
            
            ad = Ad.objects.create(
                title=title,
                sponsor_name=sponsor_name,
                description=description
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Ad added successfully',
                'ad': {
                    'id': ad.id,
                    'title': ad.title,
                    'sponsor_name': ad.sponsor_name,
                    'description': ad.description,
                    'is_active': ad.is_active
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error adding ad: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def update_ad_image(request, ad_id):
    """Update ad image"""
    if request.method == 'POST':
        try:
            ad = get_object_or_404(Ad, id=ad_id)
            
            if 'image' in request.FILES:
                ad.image = request.FILES['image']
                ad.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Image updated for {ad.title}',
                    'image_url': ad.image.url if ad.image else None
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No image file provided'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating image: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def toggle_ad_status(request, ad_id):
    """Toggle ad active status"""
    if request.method == 'POST':
        try:
            ad = get_object_or_404(Ad, id=ad_id)
            ad.is_active = not ad.is_active
            ad.save()
            
            status = 'activated' if ad.is_active else 'deactivated'
            return JsonResponse({
                'success': True,
                'message': f'{ad.title} {status} successfully',
                'is_active': ad.is_active
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating status: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def delete_ad(request, ad_id):
    """Delete ad"""
    if request.method == 'POST':
        try:
            ad = get_object_or_404(Ad, id=ad_id)
            title = ad.title
            ad.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Ad "{title}" deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error deleting ad: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def upload_nominees_image(request):
    """Upload nominees image"""
    if request.method == 'POST':
        try:
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            
            if not title:
                return JsonResponse({
                    'success': False,
                    'message': 'Title is required'
                })
            
            if 'image' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'message': 'Image file is required'
                })
            
            # Deactivate any existing active nominees images
            NomineesImage.objects.filter(is_active=True).update(is_active=False)
            
            # Create new nominees image
            nominees_image = NomineesImage.objects.create(
                title=title,
                description=description,
                image=request.FILES['image'],
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Nominees image uploaded successfully',
                'image_url': nominees_image.image.url
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error uploading image: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def update_nbc_link(request):
    """Update NBC link"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', '')
            url = data.get('url', '')
            
            if not title:
                return JsonResponse({
                    'success': False,
                    'message': 'Title is required'
                })
            
            if not url:
                return JsonResponse({
                    'success': False,
                    'message': 'URL is required'
                })
            
            # Deactivate any existing active NBC links
            NBCLink.objects.filter(is_active=True).update(is_active=False)
            
            # Create or update NBC link
            nbc_link, created = NBCLink.objects.get_or_create(
                title=title,
                defaults={'url': url, 'is_active': True}
            )
            
            if not created:
                nbc_link.url = url
                nbc_link.is_active = True
                nbc_link.save()
            
            return JsonResponse({
                'success': True,
                'message': 'NBC link updated successfully',
                'nbc_link': {
                    'id': nbc_link.id,
                    'title': nbc_link.title,
                    'url': nbc_link.url,
                    'is_active': nbc_link.is_active
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating NBC link: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def dashboard(request):
    """Admin dashboard"""
    context = {
        'total_users': User.objects.count(),
        'new_users_today': User.objects.filter(
            created_at__date=timezone.now().date()
        ).count(),
        'total_comedians': Comedian.objects.count(),
        'active_comedians': Comedian.objects.filter(is_active=True).count(),
        'total_ads': Ad.objects.count(),
        'active_ads': Ad.objects.filter(is_active=True).count(),
        'free_vote_users': User.objects.filter(has_used_free_vote=True).count(),
        'recent_users': User.objects.all()[:10],
    }
    
    return render(request, 'admin/dashboard.html', context)
