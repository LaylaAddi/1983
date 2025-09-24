# documents/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import LawsuitDocument, DocumentSection
from .forms import LawsuitDocumentForm, DocumentSearchForm
from django.http import JsonResponse
from documents.services import LegalDocumentPopulator
from django.db import models
import json

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

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                # def document_create(request):
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                #     """Create a new lawsuit document"""
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                #     if request.method == 'POST':
def document_detail(request, pk):
    document = get_object_or_404(LawsuitDocument, pk=pk)
    
    # Prepare status choices with selected flags
    status_choices = []
    for value, label in LawsuitDocument.STATUS_CHOICES:
        status_choices.append({
            'value': value,
            'label': label,
            'selected': document.status == value
        })
    
    context = {
        'document': document,
        'status_choices': status_choices,
    }
    return render(request, 'your_template.html', context)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               #         form = LawsuitDocumentForm(request.POST)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                #     return render(request, 'documents/create.html', {'form': form})

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
    
    # Check if document has required information
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

# Add this code to the BOTTOM of your existing documents/views.py file
# Don't replace anything - just add this after your existing views

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import DocumentSectionFormSet, TemplateInsertForm, BlankSectionForm
from .models import DocumentSection

@login_required
def manage_document_sections(request, pk):
    """Main view for managing document sections"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    # Get existing sections for this document
    sections = DocumentSection.objects.filter(document=document).order_by('order')
    
    if request.method == 'POST':
        formset = DocumentSectionFormSet(request.POST, queryset=sections)
        if formset.is_valid():
            instances = formset.save(commit=False)
            
            # Set the document for any new instances
            for instance in instances:
                instance.document = document
                instance.save()
            
            # Handle deletions
            for obj in formset.deleted_objects:
                obj.delete()
            
            messages.success(request, 'Document sections updated successfully!')
            return redirect('manage_document_sections', pk=document.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        formset = DocumentSectionFormSet(queryset=sections)
    
    # Forms for adding new sections
    template_form = TemplateInsertForm()
    blank_form = BlankSectionForm()
    
    context = {
        'document': document,
        'formset': formset,
        'template_form': template_form,
        'blank_form': blank_form,
        'sections': sections,
    }
    
    return render(request, 'documents/manage_sections.html', context)


@login_required
@require_POST
def insert_template_section(request, pk):
    """Insert a legal template as a new section"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    form = TemplateInsertForm(request.POST)
    
    if form.is_valid():
        template = form.get_template()
        if template:
            # Check if section already exists
            existing_section = DocumentSection.objects.filter(
                document=document,
                section_type=template.section_type
            ).first()
            
            if existing_section:
                # Update existing section
                existing_section.content = template.template_text
                existing_section.title = dict(DocumentSection.SECTION_TYPES).get(
                    template.section_type, 
                    template.section_type.replace('_', ' ').title()
                )
                existing_section.save()
                messages.success(request, f'Updated existing section: {existing_section.get_section_type_display()}')
            else:
                # Get the next order number
                max_order = DocumentSection.objects.filter(document=document).aggregate(
                    max_order=models.Max('order')
                )['max_order'] or 0
                
                # Create new section from template
                section = DocumentSection.objects.create(
                    document=document,
                    section_type=template.section_type,
                    title=dict(DocumentSection.SECTION_TYPES).get(
                        template.section_type,
                        template.section_type.replace('_', ' ').title()
                    ),
                    content=template.template_text,
                    order=max_order + 1
                )
                
                messages.success(request, f'Added new section: {section.get_section_type_display()}')
        else:
            messages.error(request, 'No template found for the selected criteria.')
    else:
        messages.error(request, 'Invalid template selection.')
    
    return redirect('manage_document_sections', pk=document.pk)

@login_required
@require_POST  
def add_blank_section(request, pk):
    """Add a blank section to the document"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    form = BlankSectionForm(request.POST)
    
    if form.is_valid():
        # Get the next order number
        max_order = DocumentSection.objects.filter(document=document).aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0
        
        # Create new blank section
        section = DocumentSection.objects.create(
            document=document,
            section_type=form.cleaned_data['section_type'],
            title=form.cleaned_data['title'],
            content='[Enter your content here]',
            order=max_order + 1
        )
        
        messages.success(request, f'Added blank section: {section.title}')
    else:
        messages.error(request, 'Invalid section data.')
    
    return redirect('manage_document_sections', pk=document.pk)


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