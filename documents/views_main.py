# documents/views_main.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import LawsuitDocument, DocumentSection
from .forms import LawsuitDocumentForm, DocumentSearchForm
from django.http import JsonResponse
from documents.document_services import LegalDocumentPopulator
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


@login_required
def auto_populate_legal_sections(request, pk):
    """View to automatically populate document with legal templates"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
  
    if not document.description:
        messages.error(request, 'Please add a description of the incident before generating legal sections.')
        return redirect('document_edit', pk=pk)
    
    if not document.incident_location:
        messages.error(request, 'Please specify the incident location before generating legal sections.')
        return redirect('document_edit', pk=pk)
    
    # Populate the document
    populator = LegalDocumentPopulator(document)
    result = populator.auto_populate_document()
    
    # Update document status
    if document.status == 'draft':
        document.status = 'in_progress'
        document.save()
    
    messages.success(
        request, 
        f'Generated {result["sections_created"]} legal sections based on {result["violation_type"].replace("_", " ")} in a {result["location_type"].replace("_", " ")}.'
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