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
            document.save()
            messages.success(request, f'Document "{document.title}" created successfully!')
            return redirect('document_detail', pk=document.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LawsuitDocumentForm()
    
    context = {
        'form': form,
        'profile': profile,  # This line ensures profile data is passed to template
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
                Q(defendants__icontains=search_query)
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
    
    context = {
        'document': document,
        'sections': sections,
    }
    
    return render(request, 'documents/detail.html', context)

@login_required
def document_edit(request, pk):
    """Edit an existing document"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = LawsuitDocumentForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
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


# Replace the existing auto_populate_legal_sections function in views_main.py with this:

@login_required
def auto_populate_legal_sections(request, pk):
    """View to automatically populate document with legal templates using new orchestrator service"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    # Validate required fields
    if not document.description:
        messages.error(request, 'Please add a description of the incident before generating legal sections.')
        return redirect('document_edit', pk=pk)
    
    if not document.incident_location:
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

# @login_required
# def generate_default_sections(request, pk):
#     """Simple test function"""
#     document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
#     messages.success(request, 'Test function works!')
#     return redirect('document_detail', pk=pk)


@login_required
def generate_default_sections(request, pk):
    """Generate all 7 standard legal sections with default content"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    # Default content for each section type
    default_content = {
        'introduction': 'Plaintiff brings this civil rights action seeking damages and injunctive relief for violations of constitutional rights under 42 U.S.C. § 1983.',
        'jurisdiction': 'This Court has jurisdiction over this action pursuant to 28 U.S.C. §§ 1331 and 1343, as this action arises under the Constitution and laws of the United States. Venue is proper in this district under 28 U.S.C. § 1391(b).',
        'parties': f'Plaintiff is a citizen and resident of [STATE]. {document.defendants or "[DEFENDANTS TO BE IDENTIFIED]"} are individuals acting under color of state law.',
        'facts': f'On {document.incident_date.strftime("%B %d, %Y") if document.incident_date else "[DATE]"}, at {document.incident_location or "[LOCATION]"}, the following events occurred: {document.description or "[DESCRIPTION TO BE ADDED]"}',
        'claims': 'COUNT I - VIOLATION OF CIVIL RIGHTS (42 U.S.C. § 1983)\n\nDefendants violated Plaintiff\'s constitutional rights by [SPECIFIC VIOLATIONS TO BE DETAILED].',
        'prayer': 'WHEREFORE, Plaintiff respectfully requests that this Court:\na) Award compensatory and punitive damages;\nb) Enter injunctive relief;\nc) Award attorney\'s fees and costs pursuant to 42 U.S.C. § 1988;\nd) Grant such other relief as this Court deems just and proper.',
        'jury_demand': 'Plaintiff hereby demands a trial by jury on all issues so triable as a matter of right pursuant to Federal Rule of Civil Procedure 38.'
    }
    
    sections_created = 0
    sections_updated = 0
    
    for section_type, content in default_content.items():
        title = dict(DocumentSection.SECTION_TYPES).get(section_type, section_type.replace('_', ' ').title())
        order = list(dict(DocumentSection.SECTION_TYPES).keys()).index(section_type) + 1
        
        section, created = DocumentSection.objects.get_or_create(
            document=document,
            section_type=section_type,
            defaults={
                'title': title,
                'content': content,
                'order': order
            }
        )
        
        if created:
            sections_created += 1
        else:
            # Optionally update existing sections with default content
            # Uncomment these lines if you want to overwrite existing content:
            # section.content = content
            # section.save()
            sections_updated += 1
    
    # Update document status
    if document.status == 'draft':
        document.status = 'in_progress'
        document.save()
    
    messages.success(
        request,
        f'Generated complete legal document with all 7 standard sections. '
        f'Created {sections_created} new sections, {sections_updated} already existed. '
        f'You can now customize each section as needed.'
    )
    
    return redirect('document_detail', pk=pk)    # Add this function to your views_main.py file

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