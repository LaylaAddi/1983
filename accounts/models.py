# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Legal contact information
    full_legal_name = models.CharField(max_length=200, blank=True, 
                                      help_text="Full name as it should appear in legal documents")
    street_address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Optional additional fields
    date_of_birth = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    
    # API Usage Tracking (ADMIN ONLY - hidden from users)
    total_api_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=0.0000,
        help_text="Total API costs incurred (USD) - admin view only"
    )
    api_cost_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.50,
        help_text="Maximum allowed API spending (USD) - default $0.50 for free users"
    )
    api_limit_reached_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp when user hit their API limit"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [self.street_address, self.city, self.state, self.zip_code]
        return ", ".join(part for part in parts if part)
    
    @property
    def is_complete(self):
        """Check if profile has all required legal information"""
        required_fields = [
            self.full_legal_name, self.street_address, 
            self.city, self.state, self.zip_code, self.phone_number
        ]
        return all(field.strip() if field else False for field in required_fields)
    
    @property
    def remaining_api_budget(self):
        """Calculate remaining budget."""
        return float(self.api_cost_limit) - float(self.total_api_cost)
    
    @property
    def is_over_limit(self):
        """Check if user has exceeded their API limit."""
        return self.total_api_cost >= self.api_cost_limit
    
    @property
    def usage_percentage(self):
        """Return percentage of limit used."""
        if self.api_cost_limit == 0:
            return 100
        return (float(self.total_api_cost) / float(self.api_cost_limit)) * 100
    
    def add_api_cost(self, cost):
        """Add cost to user's total and save."""
        if isinstance(cost, float):
            cost = Decimal(str(cost))
        
        self.total_api_cost += cost
        
        if self.is_over_limit and not self.api_limit_reached_at:
            self.api_limit_reached_at = timezone.now()
        
        self.save()
    
    def reset_api_usage(self):
        """Reset API usage back to zero (admin action)."""
        self.total_api_cost = Decimal('0.0000')
        self.api_limit_reached_at = None
        self.save()

# Signal to create profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)