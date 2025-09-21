# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    # Include basic user fields
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    
    class Meta:
        model = UserProfile
        fields = [
            'full_legal_name', 'street_address', 'city', 'state', 
            'zip_code', 'phone_number', 'date_of_birth', 'occupation'
        ]
        widgets = {
            'full_legal_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full legal name as it appears on ID'
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123 Main Street, Apt 4B'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State abbreviation (e.g., PA, NY, CA)'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 123-4567'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your occupation (optional)'
            }),
        }
        labels = {
            'full_legal_name': 'Full Legal Name',
            'street_address': 'Street Address',
            'city': 'City',
            'state': 'State',
            'zip_code': 'ZIP Code',
            'phone_number': 'Phone Number',
            'date_of_birth': 'Date of Birth (Optional)',
            'occupation': 'Occupation (Optional)',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if commit:
            # Update User model fields
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            
            profile.save()
        
        return profile