# documents/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import LawsuitDocument
import re
from urllib.parse import urlparse

class LawsuitDocumentForm(forms.ModelForm):
    class Meta:
        model = LawsuitDocument
        fields = [
            'title', 'description', 'incident_date', 'incident_location',
            'defendants', 'youtube_url', 'additional_evidence'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title for your case (e.g., "Police Excessive Force - January 2024")'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the civil rights violation that occurred...'
            }),
            'incident_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'incident_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address, city, state where the incident occurred'
            }),
            'defendants': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List the names, positions, and departments of all defendants (officers, supervisors, agencies, etc.)'
            }),
            'youtube_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (optional)'
            }),
            'additional_evidence': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe other evidence: photos, witnesses, medical records, body cam footage, etc.'
            })
        }
        labels = {
            'title': 'Case Title',
            'description': 'Description of Rights Violation',
            'incident_date': 'Date of Incident',
            'incident_location': 'Location of Incident',
            'defendants': 'Defendants (Officers, Agencies, etc.)',
            'youtube_url': 'YouTube Video Evidence (Optional)',
            'additional_evidence': 'Additional Evidence'
        }
        help_texts = {
            'title': 'Give your case a descriptive title',
            'description': 'Provide a detailed description of what happened and how your civil rights were violated',
            'incident_date': 'When did the incident occur?',
            'incident_location': 'Where did the incident take place?',
            'defendants': 'Who are you filing suit against? Include full names, positions, and departments',
            'youtube_url': 'If you have video evidence on YouTube, provide the link',
            'additional_evidence': 'Describe any other evidence you have to support your case'
        }

    def clean_youtube_url(self):
        url = self.cleaned_data.get('youtube_url')
        if url:
            # Validate YouTube URL format
            youtube_patterns = [
                r'youtube\.com/watch\?v=',
                r'youtu\.be/',
                r'youtube\.com/embed/',
                r'youtube\.com/v/'
            ]
            
            if not any(re.search(pattern, url, re.IGNORECASE) for pattern in youtube_patterns):
                raise ValidationError("Please enter a valid YouTube URL")
                
            # Ensure it's HTTPS for security
            parsed_url = urlparse(url)
            if parsed_url.scheme == 'http':
                url = url.replace('http://', 'https://')
                
        return url

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 10:
            raise ValidationError("Case title should be at least 10 characters long")
        return title.strip() if title else title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 50:
            raise ValidationError("Please provide a more detailed description (at least 50 characters)")
        return description.strip() if description else description

    def clean_defendants(self):
        defendants = self.cleaned_data.get('defendants')
        if defendants and len(defendants.strip()) < 10:
            raise ValidationError("Please provide more details about the defendants")
        return defendants.strip() if defendants else defendants


class DocumentSectionForm(forms.Form):
    """Form for editing individual sections of a document"""
    section_type = forms.CharField(widget=forms.HiddenInput())
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Section title'
        })
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Section content...'
        })
    )

class DocumentSearchForm(forms.Form):
    """Form for searching user's documents"""
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search your documents...'
        })
    )
    status_filter = forms.ChoiceField(
        choices=[('', 'All Status')] + LawsuitDocument.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )