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
    youtube_url_1_start_time = models.CharField(max_length=10, blank=True, help_text="Start timestamp (MM:SS)")
    youtube_url_1_end_time = models.CharField(max_length=10, blank=True, help_text="End timestamp (MM:SS)")
    youtube_url_1_transcript = models.TextField(blank=True, help_text="Extracted transcript snippet")
    
    youtube_url_2 = models.URLField(blank=True, help_text="Additional video evidence")
    youtube_url_2_start_time = models.CharField(max_length=10, blank=True, help_text="Start timestamp (MM:SS)")
    youtube_url_2_end_time = models.CharField(max_length=10, blank=True, help_text="End timestamp (MM:SS)")
    youtube_url_2_transcript = models.TextField(blank=True, help_text="Extracted transcript snippet")
    
    youtube_url_3 = models.URLField(blank=True, help_text="Additional video evidence")
    youtube_url_3_start_time = models.CharField(max_length=10, blank=True, help_text="Start timestamp (MM:SS)")
    youtube_url_3_end_time = models.CharField(max_length=10, blank=True, help_text="End timestamp (MM:SS)")
    youtube_url_3_transcript = models.TextField(blank=True, help_text="Extracted transcript snippet")
    
    youtube_url_4 = models.URLField(blank=True, help_text="Additional video evidence")
    youtube_url_4_start_time = models.CharField(max_length=10, blank=True, help_text="Start timestamp (MM:SS)")
    youtube_url_4_end_time = models.CharField(max_length=10, blank=True, help_text="End timestamp (MM:SS)")
    youtube_url_4_transcript = models.TextField(blank=True, help_text="Extracted transcript snippet")
    
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

    @property
    def total_sections(self):
        """Get total number of sections in this document"""
        return self.sections.count()

    @property
    def completed_sections(self):
        """Get number of completed sections"""
        return sum(1 for section in self.sections.all() if section.is_complete)

    @property
    def incomplete_sections(self):
        """Get number of incomplete sections"""
        return self.total_sections - self.completed_sections

    @property
    def completion_percentage(self):
        """Calculate overall document completion percentage"""
        if self.total_sections == 0:
            return 0
        return int((self.completed_sections / self.total_sections) * 100)

    @property
    def is_document_complete(self):
        """Check if all sections are complete"""
        return self.total_sections > 0 and self.completed_sections == self.total_sections

    def get_section_completion_summary(self):
        """
        Get detailed completion summary for all sections.
        Returns list of dicts with section info and completion status.
        """
        sections_data = []
        for section in self.sections.all():
            sections_data.append({
                'type': section.section_type,
                'title': section.get_section_type_display(),
                'is_complete': section.is_complete,
                'completion_percentage': section.completion_percentage,
                'content_length': len(section.content) if section.content else 0,
            })
        return sections_data

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
        ('exhibits', 'List of Exhibits'),  # Optional section
    ]

    # Required sections for a complete document (exhibits is optional)
    REQUIRED_SECTIONS = [
        'introduction',
        'jurisdiction',
        'parties',
        'facts',
        'claims',
        'prayer',
        'jury_demand'
    ]

    document = models.ForeignKey(LawsuitDocument, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    # AI Enhancement tracking
    ai_enhanced = models.BooleanField(default=False, help_text='Whether this section was enhanced using AI')
    ai_cost = models.DecimalField(max_digits=6, decimal_places=4, default=0.0, help_text='Cost of AI enhancement in USD')
    ai_model = models.CharField(max_length=50, blank=True, help_text='AI model used (e.g., gpt-4o)')

    class Meta:
        ordering = ['order']
        unique_together = ['document', 'section_type']

    def __str__(self):
        return f"{self.document.title} - {self.get_section_type_display()}"

    @property
    def is_complete(self):
        """
        Check if section has meaningful content.
        A section is complete if it has content longer than 100 characters
        and doesn't contain placeholder text.
        """
        if not self.content or len(self.content.strip()) < 100:
            return False

        # Check for common placeholder patterns
        placeholder_phrases = [
            '[INSERT',
            '[TO BE COMPLETED]',
            '[PLACEHOLDER]',
            'TODO',
            'TBD',
        ]

        content_upper = self.content.upper()
        for phrase in placeholder_phrases:
            if phrase in content_upper:
                return False

        return True

    @property
    def completion_percentage(self):
        """
        Estimate completion percentage based on content length.
        Assumes a typical section should have at least 500 characters.
        """
        if not self.content:
            return 0

        min_length = 500
        current_length = len(self.content.strip())

        if current_length >= min_length:
            return 100

        return int((current_length / min_length) * 100)
    

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

class VideoEvidence(models.Model):
    """
    Stores video evidence segments with timestamps and transcripts.
    Allows multiple segments per video URL.
    """
    document = models.ForeignKey(
        LawsuitDocument, 
        on_delete=models.CASCADE, 
        related_name='video_evidence'
    )
    
    # Video information
    youtube_url = models.URLField(help_text="Full YouTube URL")
    video_title = models.CharField(max_length=300, blank=True, help_text="Auto-fetched from YouTube")
    
    # Timestamp segment
    start_time = models.CharField(max_length=10, help_text="Start time (MM:SS or HH:MM:SS)")
    end_time = models.CharField(max_length=10, help_text="End time (MM:SS or HH:MM:SS)")
    start_seconds = models.IntegerField(help_text="Start time in seconds for sorting")
    end_seconds = models.IntegerField(help_text="End time in seconds")
    
    # Transcripts
    raw_transcript = models.TextField(blank=True, help_text="Original AI-generated transcript (preserved)")
    edited_transcript = models.TextField(blank=True, help_text="User-edited transcript with speaker attribution")
    
    # Manual entry option
    manually_entered = models.BooleanField(default=False, help_text="True if transcript was manually entered")
    
    # Analysis and categorization
    violation_tags = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Comma-separated violation types: first_amendment,fourth_amendment,etc"
    )
    notes = models.TextField(blank=True, help_text="User notes about this segment")
    
    # Status
    is_reviewed = models.BooleanField(default=False, help_text="User has reviewed and approved")
    include_in_complaint = models.BooleanField(default=False, help_text="Include in final document")
    
    # Metadata
    extraction_cost = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True, help_text="API cost in USD")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['youtube_url', 'start_seconds']
        verbose_name = "Video Evidence Segment"
        verbose_name_plural = "Video Evidence Segments"
    
    def __str__(self):
        return f"{self.youtube_url} ({self.start_time}-{self.end_time})"
    
    @property
    def duration_seconds(self):
        """Calculate segment duration"""
        return self.end_seconds - self.start_seconds
    
    @property
    def youtube_embed_url(self):
        """Generate embeddable YouTube URL with timestamp"""
        from documents.services.whisper_transcript_service import WhisperTranscriptService
        video_id = WhisperTranscriptService.extract_video_id(self.youtube_url)
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}?start={self.start_seconds}"
        return None
    
class PurchasedDocument(models.Model):
    """Tracks which documents user has purchased for pay-per-document plan"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='purchased_documents')
    document = models.ForeignKey('LawsuitDocument', on_delete=models.CASCADE, related_name='purchases')
    
    # Payment info
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=255)
    discount_code_used = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'document']

    def __str__(self):
        return f"{self.user.username} - {self.document.title}"


class Person(models.Model):
    """
    Tracks people involved in the case (plaintiff, defendants, witnesses).
    Used for speaker attribution in video transcripts.
    """
    ROLE_CHOICES = [
        ('plaintiff', 'Plaintiff'),
        ('defendant', 'Defendant'),
        ('witness', 'Witness'),
        ('other', 'Other'),
    ]

    document = models.ForeignKey(
        LawsuitDocument,
        on_delete=models.CASCADE,
        related_name='people'
    )

    name = models.CharField(max_length=200, help_text="Full name of the person")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, help_text="Role in the case")
    title = models.CharField(max_length=200, blank=True, help_text="Job title or position (e.g., 'Officer', 'Detective')")
    badge_number = models.CharField(max_length=50, blank=True, help_text="Badge number for law enforcement")
    notes = models.TextField(blank=True, help_text="Additional notes about this person")

    # Display preferences for quotes
    color_code = models.CharField(max_length=7, default='#6c757d', help_text="Color for highlighting (hex code)")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['role', 'name']
        verbose_name_plural = "People"
        unique_together = ['document', 'name', 'role']

    def __str__(self):
        if self.title:
            return f"{self.name} ({self.title}) - {self.get_role_display()}"
        return f"{self.name} - {self.get_role_display()}"

    @property
    def display_name(self):
        """Display name with title if available"""
        return f"{self.title} {self.name}" if self.title else self.name


class TranscriptQuote(models.Model):
    """
    Stores highlighted transcript segments with speaker attribution.
    Allows users to organize and tag who said what in video evidence.
    """
    video_evidence = models.ForeignKey(
        VideoEvidence,
        on_delete=models.CASCADE,
        related_name='quotes'
    )

    # The quoted text
    text = models.TextField(help_text="The actual quoted text from the transcript")

    # Position in transcript (for highlighting UI)
    start_position = models.IntegerField(help_text="Character start position in edited_transcript")
    end_position = models.IntegerField(help_text="Character end position in edited_transcript")

    # Speaker attribution
    speaker = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='quotes',
        help_text="Who said this quote"
    )

    # Timestamp context (within the segment)
    approximate_timestamp = models.CharField(
        max_length=20,
        blank=True,
        help_text="Approximate timestamp within segment (MM:SS)"
    )

    # Categorization and significance
    significance = models.CharField(
        max_length=300,
        blank=True,
        help_text="Why this quote is significant (e.g., 'Unlawful demand for ID')"
    )

    violation_tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated violation types: fourth_amendment,first_amendment,excessive_force,etc"
    )

    # User notes
    notes = models.TextField(blank=True, help_text="Additional context or notes about this quote")

    # Ordering and organization
    sort_order = models.IntegerField(default=0, help_text="Manual sort order within segment")

    # Include in document
    include_in_document = models.BooleanField(
        default=True,
        help_text="Include this quote in AI-generated document"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['video_evidence', 'sort_order', 'start_position']
        verbose_name = "Transcript Quote"
        verbose_name_plural = "Transcript Quotes"

    def __str__(self):
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"{self.speaker.name}: \"{preview}\""

    @property
    def full_timestamp(self):
        """Get full timestamp including video segment start time"""
        if self.approximate_timestamp:
            return f"{self.video_evidence.start_time}+{self.approximate_timestamp}"
        return self.video_evidence.start_time

    @property
    def formatted_citation(self):
        """Generate formatted citation for legal document"""
        return f'At {self.full_timestamp}, {self.speaker.display_name} stated: "{self.text}"'