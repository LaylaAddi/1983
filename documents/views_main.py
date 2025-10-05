# documents/views_main.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import LawsuitDocument, DocumentSection
from .forms import LawsuitDocumentForm, DocumentSearchForm
from django.http import JsonResponse
from django.db import models
import json
from django.views.decorators.http import require_POST
from django_weasyprint import WeasyTemplateResponseMixin
from django.views.generic import DetailView


@login_required
def document_create(request):
    """Create a new lawsuit document"""
    from accounts.models import UserProfile
    
    # Check if user has complete profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_complete:
        messages.warning(request, 'Please complete your profile with legal contact information before creating documents.')
        return redirect('profile')
    
    if request.method == 'POST':
        form = LawsuitDocumentForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            
            # TODO: Add court lookup functionality here
            # This is where we'll integrate the court lookup service
            # to automatically populate suggested_federal_district
            
            document.save()
            messages.success(request, f'Document "{document.title}" created successfully!')
            return redirect('document_detail', pk=document.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LawsuitDocumentForm()
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'documents/create.html', context)  

@login_required
def document_list(request):
    """List user's documents with search and filtering"""
    documents = LawsuitDocument.objects.filter(user=request.user)
    
    # Handle search and filtering
    search_form = DocumentSearchForm(request.GET)
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        status_filter = search_form.cleaned_data.get('status_filter')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if search_query:
            documents = documents.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(defendants__icontains=search_query) |
                Q(incident_location__icontains=search_query) |
                Q(incident_city__icontains=search_query) |
                Q(incident_state__icontains=search_query)
            )
        
        if status_filter:
            documents = documents.filter(status=status_filter)
            
        if date_from:
            documents = documents.filter(created_at__date__gte=date_from)
            
        if date_to:
            documents = documents.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(documents.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'documents': page_obj,
    }
    
    return render(request, 'documents/list.html', context)


@login_required
def document_detail(request, pk):
    """View individual document details"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    sections = document.sections.all().order_by('order')
    
    # Video evidence counts
    video_evidence = document.video_evidence.all()
    reviewed_count = video_evidence.filter(is_reviewed=True).count()
    included_count = video_evidence.filter(include_in_complaint=True).count()
    
    context = {
        'document': document,
        'sections': sections,
        'video_evidence_count': video_evidence.count(),
        'video_evidence_reviewed': reviewed_count,
        'video_evidence_included': included_count,
    }
    
    return render(request, 'documents/detail.html', context)

@login_required
def document_edit(request, pk):
    """Edit an existing document"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = LawsuitDocumentForm(request.POST, instance=document)
        if form.is_valid():
            # Check if address fields changed to trigger court lookup
            address_changed = False
            if form.has_changed():
                address_fields = ['incident_city', 'incident_state', 'incident_zip_code', 'incident_street_address']
                if any(field in form.changed_data for field in address_fields):
                    address_changed = True
            
            document = form.save(commit=False)
            
            # TODO: Add court lookup functionality here if address changed
            # if address_changed:
            #     # Run court lookup service and update suggested_federal_district
            #     pass
            
            document.save()
            
            if address_changed:
                messages.info(request, 'Address information updated. The federal court district will be re-evaluated when you generate legal sections.')
            
            messages.success(request, f'Document "{document.title}" updated successfully!')
            return redirect('document_detail', pk=document.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LawsuitDocumentForm(instance=document)
    
    context = {
        'form': form,
        'document': document,
    }
    
    return render(request, 'documents/edit.html', context)

@login_required
def document_delete(request, pk):
    """Delete a document"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    if request.method == 'POST':
        document_title = document.title
        document.delete()
        messages.success(request, f'Document "{document_title}" deleted successfully!')
        return redirect('document_list')
    
    return render(request, 'documents/delete.html', {'document': document})

@login_required
def document_status_update(request, pk):
    """Update document status via AJAX"""
    if request.method == 'POST':
        document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
        
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            
            if new_status in [choice[0] for choice in LawsuitDocument.STATUS_CHOICES]:
                document.status = new_status
                document.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Status updated to {document.get_status_display()}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid status'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def auto_populate_legal_sections(request, pk):
    """View to automatically populate document with legal templates using new orchestrator service"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    # Validate required fields
    if not document.description:
        messages.error(request, 'Please add a description of the incident before generating legal sections.')
        return redirect('document_edit', pk=pk)
    
    # Check for location - either structured address or general location
    if not (document.has_structured_address or document.incident_location):
        messages.error(request, 'Please specify the incident location before generating legal sections.')
        return redirect('document_edit', pk=pk)
    
    # Use the new orchestrator service
    from documents.services import DocumentOrchestratorService
    orchestrator = DocumentOrchestratorService(document)
    result = orchestrator.auto_populate_document()
    
    # Update document status
    if document.status == 'draft':
        document.status = 'in_progress'
        document.save()
    
    # Enhanced success message with more detailed information
    violation_desc = result.get('violation_description', result['violation_type'].replace("_", " "))
    location_desc = result.get('location_description', result['location_type'].replace("_", " "))
    
    if result['sections_created'] > 0 or result['sections_updated'] > 0:
        message_parts = []
        if result['sections_created'] > 0:
            message_parts.append(f"created {result['sections_created']} new sections")
        if result['sections_updated'] > 0:
            message_parts.append(f"updated {result['sections_updated']} existing sections")
        
        action_text = " and ".join(message_parts)
        messages.success(
            request, 
            f'Successfully {action_text} based on {violation_desc} in a {location_desc}. '
            f'Found {result["templates_found"]} matching templates.'
        )
    else:
        messages.warning(
            request,
            f'No sections were generated. This might indicate missing templates for {violation_desc} '
            f'in a {location_desc}. Contact support if this seems incorrect.'
        )
    
    return redirect('document_detail', pk=pk)


@login_required
def document_preview(request, pk):
    """Preview the complete document as it would appear in court"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    sections = DocumentSection.objects.filter(document=document).order_by('order')
    
    context = {
        'document': document,
        'sections': sections,
    }
    
    return render(request, 'documents/document_preview.html', context)


@login_required
def generate_default_sections(request, pk):
    """View to generate all 7 standard legal sections with default content"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    # Use the service to handle the business logic
    from documents.services import SectionGenerationService
    result = SectionGenerationService.create_all_default_sections(document)
    
    # Update document status
    if document.status == 'draft':
        document.status = 'in_progress'
        document.save()
    
    # Handle user messaging based on service results
    if result['sections_created'] > 0:
        messages.success(
            request,
            f'Successfully generated complete legal document with all 7 standard sections. '
            f'Created {result["sections_created"]} new sections, '
            f'{result["sections_updated"]} already existed. '
            f'You can now customize each section using "Manage Legal Sections".'
        )
    else:
        messages.info(
            request,
            f'All 7 standard sections already exist in this document. '
            f'Use "Manage Legal Sections" to edit them.'
        )
    
    return redirect('document_detail', pk=pk)


class DocumentPDFView(WeasyTemplateResponseMixin, DetailView):
    """
    Generate PDF of lawsuit document using django-weasyprint.
    This class-based view handles all the PDF generation automatically.
    """
    model = LawsuitDocument
    template_name = 'documents/document_pdf.html'
    context_object_name = 'document'
    
    def get_queryset(self):
        # Security: only return documents owned by current user
        return LawsuitDocument.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = self.object.sections.all().order_by('order')
        return context
    
    def get_pdf_filename(self):
        # Custom filename for the PDF
        safe_title = self.object.title[:30].replace(' ', '_').replace('/', '-')
        return f"lawsuit_{self.object.pk}_{safe_title}.pdf"