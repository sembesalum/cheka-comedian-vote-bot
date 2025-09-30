from django.db import models
from django.utils import timezone
import uuid
import random
import string


class User(models.Model):
    """Model to track users and their first-time status"""
    phone_number = models.CharField(max_length=20, unique=True)
    is_first_time = models.BooleanField(default=True)
    has_used_free_vote = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.phone_number} ({'New' if self.is_first_time else 'Returning'})"
    
    class Meta:
        ordering = ['-created_at']


class WelcomeVideo(models.Model):
    """Model to store welcome videos for new users"""
    title = models.CharField(max_length=100)
    video_url = models.URLField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} (Order: {self.order})"
    
    class Meta:
        ordering = ['order']


class Ad(models.Model):
    """Model to store sponsored ads for free votes"""
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    sponsor_name = models.CharField(max_length=100, default="NBC Kiganjani")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.sponsor_name}"
    
    class Meta:
        ordering = ['-created_at']


class Comedian(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='comedians/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class VotingSession(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    winner_announcement_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"
    
    class Meta:
        ordering = ['-created_at']


class Vote(models.Model):
    VOTE_QUANTITY_CHOICES = [
        (1, '1 Vote - FREE (Sponsored by NBC Kiganjani)'),
        (5, '5 Votes - TZS 1,000'),
        (10, '10 Votes - TZS 2,000'),
        (50, '50 Votes - TZS 5,000'),
    ]
    
    comedian = models.ForeignKey(Comedian, on_delete=models.CASCADE)
    voting_session = models.ForeignKey(VotingSession, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    quantity = models.IntegerField(choices=VOTE_QUANTITY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    is_free_vote = models.BooleanField(default=False)
    ad = models.ForeignKey('Ad', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.phone_number} - {self.comedian.name} ({self.quantity} votes)"
    
    class Meta:
        ordering = ['-created_at']


class Ticket(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='tickets')
    ticket_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ticket {self.ticket_code} for {self.vote.comedian.name}"
    
    @classmethod
    def generate_ticket_code(cls):
        """Generate a unique 6-character ticket code"""
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            if not cls.objects.filter(ticket_code=code).exists():
                return code
    
    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = self.generate_ticket_code()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('initiated', 'Initiated'),
        ('completed', 'Completed'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    vote = models.OneToOneField(Vote, on_delete=models.CASCADE, related_name='payment')
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='mobile_money')
    transaction_reference = models.CharField(max_length=100, blank=True)
    gateway_transaction_id = models.CharField(max_length=100, blank=True)
    gateway_reference = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    payment_phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.vote.phone_number} ({self.status})"

    class Meta:
        ordering = ['-created_at']
