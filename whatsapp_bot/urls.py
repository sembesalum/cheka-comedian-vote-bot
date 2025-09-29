from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('webhook/', views.webhook, name='webhook'),
    path('api/votes/', views.get_votes, name='get_votes'),
    path('api/vote-stats/', views.get_vote_stats, name='get_vote_stats'),
    path('api/create-test-data/', views.create_test_data, name='create_test_data'),
    path('api/logs/', views.view_logs, name='view_logs'),
    path('api/errors/', views.view_errors, name='view_errors'),
    path('logs/', views.logs_view, name='logs_view'),
    
    # Admin interface
    path('admin/', admin_views.dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.user_management, name='user_management'),
    path('admin/comedians/', admin_views.comedian_management, name='comedian_management'),
    path('admin/delete-user/<int:user_id>/', admin_views.delete_user, name='delete_user'),
    path('admin/update-comedian-image/<int:comedian_id>/', admin_views.update_comedian_image, name='update_comedian_image'),
    path('admin/toggle-comedian-status/<int:comedian_id>/', admin_views.toggle_comedian_status, name='toggle_comedian_status'),
]
