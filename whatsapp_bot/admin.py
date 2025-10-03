from django.contrib import admin
from .models import User, WelcomeVideo, Ad, Comedian, NomineesImage, NBCLink, VotingSession, Vote, Ticket, Payment

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'is_first_time', 'has_used_free_vote', 'created_at', 'last_interaction']
    list_filter = ['is_first_time', 'has_used_free_vote', 'created_at']
    search_fields = ['phone_number']

@admin.register(WelcomeVideo)
class WelcomeVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    ordering = ['order']

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'sponsor_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'sponsor_name']

@admin.register(Comedian)
class ComedianAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']

@admin.register(NomineesImage)
class NomineesImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title']

@admin.register(NBCLink)
class NBCLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'url']

@admin.register(VotingSession)
class VotingSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'start_date', 'end_date', 'winner_announcement_date', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'comedian', 'quantity', 'amount', 'is_paid', 'is_free_vote', 'created_at']
    list_filter = ['is_paid', 'is_free_vote', 'quantity', 'created_at']
    search_fields = ['phone_number', 'comedian__name']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_code', 'vote', 'created_at']
    list_filter = ['created_at']
    search_fields = ['ticket_code', 'vote__phone_number']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'vote', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['payment_id', 'vote__phone_number']
