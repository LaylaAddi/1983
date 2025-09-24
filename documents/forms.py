# documents/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import LawsuitDocument
import re
from urllib.parse import urlparse
from django import forms
from .models import DocumentSection, LawsuitDocument, LegalTemplate
from django.forms import modelformset_factory

class LawsuitDocumentForm(forms.ModelForm):
    class Meta:
        model = LawsuitDocument
        fields = [
            'title', 'description', 'incident_date', 'incident_location',
            'defendants', 'youtube_url_1', 'youtube_url_2', 'youtube_url_3','youtube_url_4', 'additional_evidence'
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
            'youtube_url_1': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (primary video)'
            }),
            'youtube_url_2': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
            }),
            'youtube_url_3': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
            }),
            'youtube_url_4': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
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
            'youtube_url_1': 'Primary Video Evidence',
            'youtube_url_2': 'Additional Video Evidence',
            'youtube_url_3': 'Additional Video Evidence',
            'youtube_url_4': 'Additional Video Evidence',
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


# MANAGEMENT FORMS

class DocumentSectionForm(forms.ModelForm):
    """Form for editing individual sections of a document"""
    class Meta:
        model = DocumentSection
        fields = ['section_type', 'title', 'content', 'order']
        widgets = {
            'section_type': forms.HiddenInput(),
            'title': forms.TextInput(attrs={
                'class': 'form-control section-title',
                'placeholder': 'Section title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control section-content',
                'rows': 8,
                'placeholder': 'Section content...',
                'style': 'font-family: "Times New Roman", serif; line-height: 1.6;'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'style': 'width: 80px;',
                'min': '0',
                'step': '1'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make title field show the display name for section types
        if self.instance and self.instance.section_type:
            section_display = dict(DocumentSection.SECTION_TYPES).get(
                self.instance.section_type, 
                self.instance.section_type.replace('_', ' ').title()
            )
            self.fields['title'].widget.attrs['placeholder'] = section_display


class TemplateInsertForm(forms.Form):
    """Form for inserting legal templates into documents"""
    violation_type = forms.ChoiceField(
        choices=[('', 'Select violation type')] + LegalTemplate.VIOLATION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'violation-type-select'
        }),
        required=True
    )
    location_type = forms.ChoiceField(
        choices=[('', 'Select location type')] + LegalTemplate.LOCATION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'location-type-select'
        }),
        required=True
    )
    section_type = forms.ChoiceField(
        choices=[('', 'Select section type')] + DocumentSection.SECTION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'section-type-select'
        }),
        required=True
    )

    def get_template(self):
        """Get the matching legal template"""
        if self.is_valid():
            try:
                return LegalTemplate.objects.get(
                    violation_type=self.cleaned_data['violation_type'],
                    location_type=self.cleaned_data['location_type'],
                    section_type=self.cleaned_data['section_type']
                )
            except LegalTemplate.DoesNotExist:
                return None
        return None


class BlankSectionForm(forms.Form):
    """Form for adding blank sections"""
    section_type = forms.ChoiceField(
        choices=DocumentSection.SECTION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'blank-section-type'
        }),
        required=True
    )
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Custom section title (optional)'
        }),
        required=False
    )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        section_type = self.cleaned_data.get('section_type')
        
        # Use section type display name if no custom title provided
        if not title and section_type:
            title = dict(DocumentSection.SECTION_TYPES).get(section_type, section_type)
        
        return title


# Create formset for managing multiple sections at once
DocumentSectionFormSet = modelformset_factory(
    DocumentSection,
    form=DocumentSectionForm,
    extra=0,  # Don't add extra empty forms
    can_delete=True,  # Allow deletion of sections
    can_order=True   # Allow reordering
)    


class LawsuitDocumentForm(forms.ModelForm):
    class Meta:
        model = LawsuitDocument
        fields = [
            'title', 'description', 'incident_date', 'incident_location',
            'defendants', 'youtube_url_1', 'youtube_url_2', 'youtube_url_3','youtube_url_4', 'additional_evidence'
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
            'youtube_url_1': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (primary video)'
            }),
            'youtube_url_2': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
            }),
            'youtube_url_3': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
            }),
            'youtube_url_4': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
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
            'youtube_url_1': 'Primary Video Evidence',
            'youtube_url_2': 'Additional Video Evidence',
            'youtube_url_3': 'Additional Video Evidence',
            'youtube_url_4': 'Additional Video Evidence',
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


# NEW SECTION MANAGEMENT FORMS

class DocumentSectionForm(forms.ModelForm):
    """Form for editing individual sections of a document"""
    class Meta:
        model = DocumentSection
        fields = ['section_type', 'title', 'content', 'order']
        widgets = {
            'section_type': forms.HiddenInput(),
            'title': forms.TextInput(attrs={
                'class': 'form-control section-title',
                'placeholder': 'Section title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control section-content',
                'rows': 8,
                'placeholder': 'Section content...',
                'style': 'font-family: "Times New Roman", serif; line-height: 1.6;'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'style': 'width: 80px;',
                'min': '0',
                'step': '1'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make title field show the display name for section types
        if self.instance and self.instance.section_type:
            section_display = dict(DocumentSection.SECTION_TYPES).get(
                self.instance.section_type, 
                self.instance.section_type.replace('_', ' ').title()
            )
            self.fields['title'].widget.attrs['placeholder'] = section_display


class TemplateInsertForm(forms.Form):
    """Form for inserting legal templates into documents"""
    violation_type = forms.ChoiceField(
        choices=[('', 'Select violation type')] + LegalTemplate.VIOLATION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'violation-type-select'
        }),
        required=True
    )
    location_type = forms.ChoiceField(
        choices=[('', 'Select location type')] + LegalTemplate.LOCATION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'location-type-select'
        }),
        required=True
    )
    section_type = forms.ChoiceField(
        choices=[('', 'Select section type')] + DocumentSection.SECTION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'section-type-select'
        }),
        required=True
    )

    def get_template(self):
        """Get the matching legal template"""
        if self.is_valid():
            try:
                return LegalTemplate.objects.get(
                    violation_type=self.cleaned_data['violation_type'],
                    location_type=self.cleaned_data['location_type'],
                    section_type=self.cleaned_data['section_type']
                )
            except LegalTemplate.DoesNotExist:
                return None
        return None


class BlankSectionForm(forms.Form):
    """Form for adding blank sections"""
    section_type = forms.ChoiceField(
        choices=DocumentSection.SECTION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'blank-section-type'
        }),
        required=True
    )
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Custom section title (optional)'
        }),
        required=False
    )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        section_type = self.cleaned_data.get('section_type')
        
        # Use section type display name if no custom title provided
        if not title and section_type:
            title = dict(DocumentSection.SECTION_TYPES).get(section_type, section_type)
        
        return title


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


# Create formset for managing multiple sections at once
DocumentSectionFormSet = modelformset_factory(
    DocumentSection,
    form=DocumentSectionForm,
    extra=0,  # Don't add extra empty forms
    can_delete=True,  # Allow deletion of sections
    can_order=True   # Allow reordering
)


class LawsuitDocumentForm(forms.ModelForm):
    class Meta:
        model = LawsuitDocument
        fields = [
            'title', 'description', 'incident_date', 'incident_location',
            'defendants', 'youtube_url_1', 'youtube_url_2', 'youtube_url_3',
            'youtube_url_4', 'additional_evidence', 'include_videos_in_document'
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
            'youtube_url_1': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (primary video)'
            }),
            'youtube_url_2': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
            }),
            'youtube_url_3': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
            }),
            'youtube_url_4': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
            }),
            'additional_evidence': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe other evidence: photos, witnesses, medical records, body cam footage, etc.'
            }),
            'include_videos_in_document': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'include_videos_checkbox'
            }),
        }
        labels = {
            'title': 'Case Title',
            'description': 'Description of Rights Violation',
            'incident_date': 'Date of Incident',
            'incident_location': 'Location of Incident',
            'defendants': 'Defendants (Officers, Agencies, etc.)',
            'youtube_url_1': 'Primary Video Evidence',
            'youtube_url_2': 'Additional Video Evidence',
            'youtube_url_3': 'Additional Video Evidence',
            'youtube_url_4': 'Additional Video Evidence',
            'additional_evidence': 'Additional Evidence',
            'include_videos_in_document': 'Include Videos as Legal Exhibits',
        }
        help_texts = {
            'title': 'Give your case a descriptive title',
            'description': 'Provide a detailed description of what happened and how your civil rights were violated',
            'incident_date': 'When did the incident occur?',
            'incident_location': 'Where did the incident take place?',
            'defendants': 'Who are you filing suit against? Include full names, positions, and departments',
            'youtube_url_1': 'If you have video evidence on YouTube, provide the link',
            'youtube_url_2': 'Additional video evidence (optional)',
            'youtube_url_3': 'Additional video evidence (optional)',
            'youtube_url_4': 'Additional video evidence (optional)',
            'additional_evidence': 'Describe any other evidence you have to support your case',
            'include_videos_in_document': 'Check this box to include video URLs as formal exhibits in your legal document. Leave unchecked to keep videos for reference only.',
        }