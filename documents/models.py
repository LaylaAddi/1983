# documents/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class LawsuitDocument(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('filed', 'Filed'),
    ]
    
    include_videos_in_document = models.BooleanField(
        default=False,
        help_text="Include video URLs as formal exhibits in the legal document"
    )
    
    # Basic Info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lawsuit_documents')
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Brief description of the civil rights violation")
    
    # Case Details
    incident_date = models.DateField(null=True, blank=True)
    incident_location = models.CharField(max_length=300, blank=True, help_text="Full address or description of where incident occurred")
    
    # NEW: Structured incident address fields for court lookup
    incident_street_address = models.CharField(max_length=200, blank=True, help_text="Street address where incident occurred")
    incident_city = models.CharField(max_length=100, blank=True, help_text="City where incident occurred")
    incident_state = models.CharField(max_length=50, blank=True, help_text="State where incident occurred")
    incident_zip_code = models.CharField(max_length=20, blank=True, help_text="ZIP code where incident occurred")
    
    # Federal court information (auto-populated based on incident location)
    use_manual_court = models.BooleanField(default=False, help_text="Whether user manually entered court district")
    suggested_federal_district = models.TextField(blank=True, help_text="Auto-suggested federal district court")
    user_confirmed_district = models.TextField(blank=True, help_text="User-confirmed federal district court")
    district_lookup_confidence = models.CharField(max_length=20, blank=True, choices=[
        ('high', 'High Confidence'),
        ('medium', 'Medium Confidence'),
        ('low', 'Low Confidence'),
        ('manual', 'Manually Selected')
    ])
    
    defendants = models.TextField(blank=True, help_text="Names and positions of defendants")
    
    # Evidence
    youtube_url_1 = models.URLField(blank=True, help_text="Primary video evidence")
    youtube_url_2 = models.URLField(blank=True, help_text="Additional video evidence")
    youtube_url_3 = models.URLField(blank=True, help_text="Additional video evidence")
    youtube_url_4 = models.URLField(blank=True, help_text="Additional video evidence")
    
    additional_evidence = models.TextField(blank=True, help_text="Description of other evidence")
    
    # Document Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Generated Files
    pdf_file = models.FileField(upload_to='documents/pdfs/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('document_detail', kwargs={'pk': self.pk})
    
    @property
    def full_incident_address(self):
        """Return the complete incident address formatted"""
        parts = [
            self.incident_street_address,
            self.incident_city,
            self.incident_state,
            self.incident_zip_code
        ]
        return ", ".join(part for part in parts if part.strip())
    
    @property
    def has_structured_address(self):
        """Check if structured address fields are filled"""
        return bool(self.incident_city and self.incident_state)

class DocumentSection(models.Model):
    """Sections within a lawsuit document"""
    SECTION_TYPES = [
        ('introduction', 'Introduction'),
        ('jurisdiction', 'Jurisdiction and Venue'),
        ('parties', 'Parties'),
        ('facts', 'Statement of Facts'),
        ('claims', 'Claims for Relief'),
        ('prayer', 'Prayer for Relief'),
        ('jury_demand', 'Jury Trial Demand'),
    ]
    
    document = models.ForeignKey(LawsuitDocument, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['document', 'section_type']
        
    def __str__(self):
        return f"{self.document.title} - {self.get_section_type_display()}"
    

class LegalTemplate(models.Model):
    """Store legal boilerplate templates for different violation types"""
    VIOLATION_TYPES = [
        ('threatened_arrest_public', 'Threatened Arrest in Public Area'),
        ('interference_recording', 'Interference with Recording'),
        ('forced_to_leave_public', 'Forced to Leave Public Area'),
        ('retaliation_protected_speech', 'Retaliation for Protected Speech'),
    ]
    
    LOCATION_TYPES = [
        ('traditional_public_forum', 'Traditional Public Forum'),
        ('designated_public_forum', 'Designated Public Forum'),
        ('limited_public_forum', 'Limited Public Forum'),
    ]
    
    violation_type = models.CharField(max_length=50, choices=VIOLATION_TYPES)
    location_type = models.CharField(max_length=50, choices=LOCATION_TYPES)
    section_type = models.CharField(max_length=20)  # matches DocumentSection.SECTION_TYPES
    template_text = models.TextField()
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['violation_type', 'location_type', 'section_type']
    
    def __str__(self):
        return f"{self.get_violation_type_display()} - {self.section_type}"