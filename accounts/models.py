# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

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