# documents/forms.py - Just add court fields to your current working form

from django import forms
from django.core.exceptions import ValidationError
from .models import LawsuitDocument, DocumentSection, LegalTemplate
import re
from urllib.parse import urlparse
from django.forms import modelformset_factory

class LawsuitDocumentForm(forms.ModelForm):
    # US States choices for dropdown
    STATE_CHOICES = [
        ('', 'Select State'),
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('DC', 'District of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'),
        ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
        ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'),
        ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'),
        ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
        ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'),
        ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'),
        ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'),
        ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'),
        ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')
    ]
    
    # Override the incident_state field to use choices
    incident_state = forms.ChoiceField(
        choices=STATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    user_confirmed_district = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., United States District Court for the Eastern District of Michigan'
        }),
        help_text='Manually enter or override the federal district court'
    )

    class Meta:
        model = LawsuitDocument
        fields = [
            'title', 
            'description', 
            'incident_date', 
            # Use both location fields
            'incident_location', 
            'user_confirmed_district',
            'incident_street_address', 
            'incident_city', 
            'incident_state', 
            'incident_zip_code',
            'defendants', 
            'youtube_url_1', 
            'youtube_url_1_start_time',
            'youtube_url_1_end_time', 
            'youtube_url_1_transcript',
            'youtube_url_2', 
            'youtube_url_2_start_time',
            'youtube_url_2_end_time', 
            'youtube_url_2_transcript',
            'youtube_url_3', 
            'youtube_url_3_start_time',
            'youtube_url_3_end_time', 
            'youtube_url_3_transcript',
            'youtube_url_4', 
            'youtube_url_4_start_time',
            'youtube_url_4_end_time', 
            'youtube_url_4_transcript',
            'additional_evidence', 
            'include_videos_in_document',
            
            'suggested_federal_district', 
            'user_confirmed_district', 
            'district_lookup_confidence'
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
                'placeholder': 'General description or additional location details (optional)'
            }),
            # NEW: Structured address fields
            'incident_street_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '400 Main St (or general area description)'
            }),
            'incident_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Clarion'
            }),
            'incident_state': forms.Select(attrs={
                'class': 'form-control'
            }),
            'incident_zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '16214'
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
             'youtube_url_1_start_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0:00'}),
            'youtube_url_1_end_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0:30'}),
            'youtube_url_2': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
            }),
             'youtube_url_2_start_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0:00'}),
            'youtube_url_2_end_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0:30'}),
            'youtube_url_3': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
            }),
             'youtube_url_3_start_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0:00'}),
            'youtube_url_3_end_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0:30'}),
            'youtube_url_4': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... (additional video)'
            }),
             'youtube_url_4_start_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0:00'}),
             'youtube_url_4_end_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0:30'}),
             'additional_evidence': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe other evidence: photos, witnesses, medical records, body cam footage, etc.'
            }),
            'include_videos_in_document': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'include_videos_checkbox'
            }),
            # ADD: Hidden court fields to prevent constraint errors
            'suggested_federal_district': forms.HiddenInput(),
            'user_confirmed_district': forms.HiddenInput(),
            'district_lookup_confidence': forms.HiddenInput(),
        }
        labels = {
            'title': 'Case Title',
            'description': 'Description of Rights Violation',
            'incident_date': 'Date of Incident',
            'incident_location': 'Additional Location Details',
            'incident_street_address': 'Street Address',
            'incident_city': 'City',
            'incident_state': 'State',
            'incident_zip_code': 'ZIP Code',
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
            'incident_location': 'Any additional details about the location (business name, landmarks, etc.)',
            'incident_street_address': 'Street address or general area where the incident occurred',
            'incident_city': 'City where the incident occurred',
            'incident_state': 'State where the incident occurred (2-letter code, e.g. PA)',
            'incident_zip_code': 'ZIP code of the incident location',
            'defendants': 'Who are you filing suit against? Include full names, positions, and departments',
            'youtube_url_1': 'If you have video evidence on YouTube, provide the link',
            'youtube_url_2': 'Additional video evidence (optional)',
            'youtube_url_3': 'Additional video evidence (optional)',
            'youtube_url_4': 'Additional video evidence (optional)',
            'additional_evidence': 'Describe any other evidence you have to support your case',
            'include_videos_in_document': 'Check this box to include video URLs as formal exhibits in your legal document.',
        }

    def clean_youtube_url_1(self):
        return self._clean_youtube_url(self.cleaned_data.get('youtube_url_1'))
    
    def clean_youtube_url_2(self):
        return self._clean_youtube_url(self.cleaned_data.get('youtube_url_2'))
    
    def clean_youtube_url_3(self):
        return self._clean_youtube_url(self.cleaned_data.get('youtube_url_3'))
    
    def clean_youtube_url_4(self):
        return self._clean_youtube_url(self.cleaned_data.get('youtube_url_4'))

    def _clean_youtube_url(self, url):
        """Helper method to validate YouTube URLs"""
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

    def clean_incident_state(self):
        """Validate state selection"""
        state = self.cleaned_data.get('incident_state')
        if state and state not in [choice[0] for choice in self.STATE_CHOICES[1:]]:  # Skip empty choice
            raise ValidationError("Please select a valid state")
        return state

    def clean_incident_zip_code(self):
        """Validate ZIP code format"""
        zip_code = self.cleaned_data.get('incident_zip_code')
        if zip_code:
            # Remove any spaces or hyphens
            zip_code = re.sub(r'[\s-]', '', zip_code)
            # Validate format (5 digits or 5+4 digits)
            if not re.match(r'^\d{5}(\d{4})?$', zip_code):
                raise ValidationError("Please enter a valid ZIP code (e.g., 16214 or 16214-1234)")
        return zip_code
    

    def clean(self):
        """Cross-field validation and court lookup"""
        cleaned_data = super().clean()
        
        # Check if either structured address or general location is provided
        city = cleaned_data.get('incident_city')
        state = cleaned_data.get('incident_state')
        general_location = cleaned_data.get('incident_location')
        user_confirmed = cleaned_data.get('user_confirmed_district')
        
        if not (city and state) and not general_location:
            raise ValidationError(
                "Please provide either a city and state, or use the additional location details field."
            )
        
        # DEBUGGING: Add print statements to see what's happening
        print(f"DEBUG: Court lookup starting - City: '{city}', State: '{state}'")
        print(f"DEBUG: User confirmed district: '{user_confirmed}'")
        
        # If user manually entered a district, prioritize that and set confidence to 'manual'
        if user_confirmed and user_confirmed.strip():
            cleaned_data['user_confirmed_district'] = user_confirmed.strip()
            cleaned_data['district_lookup_confidence'] = 'manual'
            print(f"DEBUG: Using manual override: {user_confirmed}")
            # Also set suggested_federal_district to keep data in sync
            cleaned_data['suggested_federal_district'] = user_confirmed.strip()
        # Otherwise, do automatic court lookup
        elif city and state:
            try:
                print("DEBUG: Attempting to import CourtLookupService")
                from .services.court_lookup_service import CourtLookupService
                print("DEBUG: Import successful, calling lookup")
                court_result = CourtLookupService.lookup_court_by_location(city, state)
                print(f"DEBUG: Court result: {court_result}")
                
                if court_result and court_result.get('court_name'):
                    cleaned_data['suggested_federal_district'] = court_result['court_name']
                    cleaned_data['district_lookup_confidence'] = court_result.get('confidence', 'medium')
                    print(f"DEBUG: Set court fields - District: {court_result['court_name']}")
                    
                    # Auto-confirm high confidence results
                    if court_result.get('confidence') == 'high':
                        cleaned_data['user_confirmed_district'] = court_result['court_name']
                        print("DEBUG: Auto-confirmed high confidence result")
                    else:
                        # Clear any previous user confirmation if we got a new auto-suggestion
                        cleaned_data['user_confirmed_district'] = ''
                else:
                    print("DEBUG: No court result returned - clearing court fields")
                    # No court found - clear the fields so the warning shows
                    cleaned_data['suggested_federal_district'] = ''
                    cleaned_data['district_lookup_confidence'] = ''
                    cleaned_data['user_confirmed_district'] = ''
                        
            except Exception as e:
                # Don't break form submission if court lookup fails
                print(f"DEBUG: Court lookup error: {e}")
                import traceback
                traceback.print_exc()
                # Clear court fields on error
                cleaned_data['suggested_federal_district'] = ''
                cleaned_data['district_lookup_confidence'] = ''
        else:
            print(f"DEBUG: Skipping court lookup - City: '{city}', State: '{state}'")
        
        return cleaned_data


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