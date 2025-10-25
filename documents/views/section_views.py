# documents/views/section_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models

from ..forms import DocumentSectionFormSet, TemplateInsertForm, BlankSectionForm
from ..models import DocumentSection, LawsuitDocument


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
            deleted_count = 0
            for obj in formset.deleted_objects:
                obj.delete()
                deleted_count += 1

            if deleted_count > 0:
                messages.success(request, f'Successfully deleted {deleted_count} section(s)!')
            else:
                messages.success(request, 'Document sections updated successfully!')
            return redirect('manage_document_sections', pk=document.pk)
        else:
            # Add detailed error messages for debugging
            error_details = []
            for i, form in enumerate(formset):
                if form.errors:
                    error_details.append(f"Section {i+1}: {form.errors}")
            if formset.non_form_errors():
                error_details.append(f"General errors: {formset.non_form_errors()}")

            error_msg = 'Please correct the errors below.'
            if error_details:
                error_msg += ' Details: ' + ' | '.join(error_details)

            messages.error(request, error_msg)
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