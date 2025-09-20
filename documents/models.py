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
    
    # Basic Info
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lawsuit_documents')
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Brief description of the civil rights violation")
    
    # Case Details
    incident_date = models.DateField(null=True, blank=True)
    incident_location = models.CharField(max_length=300, blank=True)
    defendants = models.TextField(blank=True, help_text="Names and positions of defendants")
    
    # Evidence
    youtube_url = models.URLField(blank=True, help_text="YouTube video showing the violation")
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