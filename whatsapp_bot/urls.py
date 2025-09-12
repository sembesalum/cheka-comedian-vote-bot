from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.webhook, name='webhook'),
    path('api/votes/', views.get_votes, name='get_votes'),
    path('api/vote-stats/', views.get_vote_stats, name='get_vote_stats'),
    path('api/create-test-data/', views.create_test_data, name='create_test_data'),
    path('api/logs/', views.view_logs, name='view_logs'),
    path('api/errors/', views.view_errors, name='view_errors'),
    path('logs/', views.logs_view, name='logs_view'),
]
