"""
Video evidence management views.
Dedicated workflow for collecting, reviewing, and analyzing video evidence.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from ..models import LawsuitDocument, VideoEvidence
from ..services.whisper_transcript_service import WhisperTranscriptService


@login_required
def evidence_manager(request, pk):
    """
    Main evidence management page for a document.
    Shows all video evidence segments with editing capabilities.
    """
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    evidence_segments = VideoEvidence.objects.filter(document=document)
    
    # Group segments by YouTube URL
    segments_by_video = {}
    for segment in evidence_segments:
        if segment.youtube_url not in segments_by_video:
            segments_by_video[segment.youtube_url] = []
        segments_by_video[segment.youtube_url].append(segment)
    
    context = {
        'document': document,
        'evidence_segments': evidence_segments,
        'segments_by_video': segments_by_video,
        'total_segments': evidence_segments.count(),
        'reviewed_count': evidence_segments.filter(is_reviewed=True).count(),
        'included_count': evidence_segments.filter(include_in_complaint=True).count(),
    }
    
    return render(request, 'documents/evidence_manager.html', context)

@login_required
@require_POST
def extract_evidence_segment(request, pk):
    """
    Extract a new video evidence segment using Whisper API.
    Creates a new VideoEvidence record with raw transcript.
    Requires sufficient API credit and enforces 3-minute max length.
    """
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    try:
        data = json.loads(request.body)
        youtube_url = data.get('youtube_url', '')
        start_time_str = data.get('start_time', '0')
        end_time_str = data.get('end_time', '30')
        
        if not youtube_url:
            return JsonResponse({
                'success': False,
                'error': 'YouTube URL is required'
            })
        
        # Parse timestamps
        start_seconds = WhisperTranscriptService.parse_timestamp(start_time_str)
        end_seconds = WhisperTranscriptService.parse_timestamp(end_time_str)
        
        if start_seconds is None or end_seconds is None:
            return JsonResponse({
                'success': False,
                'error': 'Invalid timestamp format. Use MM:SS or HH:MM:SS'
            })
        
        # Validate 3-minute maximum length
        MAX_EXTRACTION_SECONDS = 180  # 3 minutes
        duration = end_seconds - start_seconds
        
        if duration > MAX_EXTRACTION_SECONDS:
            return JsonResponse({
                'success': False,
                'error': f'Extraction length exceeds maximum of {MAX_EXTRACTION_SECONDS // 60} minutes. Please use shorter segments.'
            })
        
        if duration <= 0:
            return JsonResponse({
                'success': False,
                'error': 'End time must be after start time.'
            })
        
        # Get user's subscription and check API credit
        from accounts.models import Subscription
        try:
            subscription = Subscription.objects.get(user=request.user)
        except Subscription.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No subscription found. Please contact support.',
                'requires_payment': True
            })
        
        # Estimate cost (roughly $0.006 per minute of audio)
        estimated_cost = (duration / 60) * 0.006
        
        # Check if user has sufficient credit
        if not subscription.has_sufficient_credit(estimated_cost):
            return JsonResponse({
                'success': False,
                'error': f'Insufficient API credit. You need approximately ${estimated_cost:.2f} but have ${subscription.api_credit_balance:.2f}. Please upgrade your plan or purchase more credit.',
                'requires_payment': True,
                'current_balance': float(subscription.api_credit_balance),
                'estimated_cost': estimated_cost
            })
        
        # Extract transcript using Whisper
        result = WhisperTranscriptService.get_transcript(
            youtube_url,
            start_time=start_seconds,
            end_time=end_seconds
        )
        
        if not result['success']:
            return JsonResponse(result)
        
        # Create VideoEvidence record
        evidence = VideoEvidence.objects.create(
            document=document,
            youtube_url=youtube_url,
            start_time=start_time_str,
            end_time=end_time_str,
            start_seconds=start_seconds,
            end_seconds=end_seconds,
            raw_transcript=result['text'],
            edited_transcript=result['text'],
            extraction_cost=result.get('cost_estimate', 0)
        )
        
        # Deduct actual cost from user's API credit
        actual_cost = result.get('cost_estimate', estimated_cost)
        subscription.deduct_api_cost(actual_cost)
        
        return JsonResponse({
            'success': True,
            'segment_id': evidence.id,
            'text': result['text'],
            'cost': actual_cost,
            'duration': result.get('duration_minutes', 0),
            'remaining_balance': float(subscription.api_credit_balance)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@login_required
@require_POST
def update_evidence_segment(request, pk, segment_id):
    """
    Update an evidence segment's edited transcript, tags, or notes.
    """
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    segment = get_object_or_404(VideoEvidence, id=segment_id, document=document)
    
    try:
        data = json.loads(request.body)
        
        # Update editable fields
        if 'edited_transcript' in data:
            segment.edited_transcript = data['edited_transcript']
        
        if 'violation_tags' in data:
            segment.violation_tags = data['violation_tags']
        
        if 'notes' in data:
            segment.notes = data['notes']
        
        if 'is_reviewed' in data:
            segment.is_reviewed = data['is_reviewed']
        
        if 'include_in_complaint' in data:
            segment.include_in_complaint = data['include_in_complaint']
        
        segment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Segment updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_POST
def delete_evidence_segment(request, pk, segment_id):
    """Delete a video evidence segment."""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    segment = get_object_or_404(VideoEvidence, id=segment_id, document=document)
    
    segment.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Segment deleted'
    })


@login_required
@require_POST
def add_manual_segment(request, pk):
    """
    Add a video segment with manually entered transcript.
    For when API extraction fails or user prefers manual entry.
    """
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    try:
        data = json.loads(request.body)
        youtube_url = data.get('youtube_url', '')
        start_time_str = data.get('start_time', '0')
        end_time_str = data.get('end_time', '30')
        manual_transcript = data.get('transcript', '')
        
        if not youtube_url or not manual_transcript:
            return JsonResponse({
                'success': False,
                'error': 'URL and transcript are required'
            })
        
        # Parse timestamps
        start_seconds = WhisperTranscriptService.parse_timestamp(start_time_str) or 0
        end_seconds = WhisperTranscriptService.parse_timestamp(end_time_str) or 30
        
        # Create segment
        evidence = VideoEvidence.objects.create(
            document=document,
            youtube_url=youtube_url,
            start_time=start_time_str,
            end_time=end_time_str,
            start_seconds=start_seconds,
            end_seconds=end_seconds,
            raw_transcript=manual_transcript,
            edited_transcript=manual_transcript,
            manually_entered=True
        )
        
        return JsonResponse({
            'success': True,
            'segment_id': evidence.id,
            'message': 'Manual segment added'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
    
    
@login_required
def generate_facts_from_evidence(request, pk):
    """
    Generate Statement of Facts section from video evidence.
    Creates or updates the 'facts' section with content from reviewed segments.
    Also creates a separate 'List of Exhibits' section.
    """
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    from ..services.evidence_to_facts_service import EvidenceToFactsService
    
    # Generate facts from evidence
    result = EvidenceToFactsService.generate_facts_section(document)
    
    if not result['content']:
        messages.warning(
            request,
            result['metadata'].get('error', 'No video evidence to generate facts from.')
        )
        return redirect('evidence_manager', pk=pk)
    
    from ..models import DocumentSection
    
    # Create or update Statement of Facts section (just the numbered facts)
    facts_section, created = DocumentSection.objects.get_or_create(
        document=document,
        section_type='facts',
        defaults={
            'title': 'Statement of Facts',
            'order': 4  # Typical position for facts section
        }
    )
    
    facts_section.content = result['content']
    facts_section.save()
    
    # Create or update List of Exhibits section (separate from facts)
    if result.get('exhibits_list'):
        exhibits_section, created = DocumentSection.objects.get_or_create(
            document=document,
            section_type='exhibits',
            defaults={
                'title': 'List of Exhibits',
                'order': 8  # After jury_demand, before signature
            }
        )
        
        exhibits_section.content = result['exhibits_list']
        exhibits_section.save()
    
    # Show success message with metadata
    messages.success(
        request,
        f'Statement of Facts generated! Created {result["metadata"]["fact_count"]} '
        f'factual statements from {result["metadata"]["segment_count"]} video segments '
        f'with {result["metadata"]["exhibit_count"]} exhibits. '
        f'Review and edit in "Manage Legal Sections".'
    )
    
    return redirect('evidence_manager', pk=pk)


@login_required
def preview_facts_from_evidence(request, pk):
    """
    Preview what the Statement of Facts will look like before generating.
    Returns JSON with formatted facts and exhibits.
    """
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    
    from ..services.evidence_to_facts_service import EvidenceToFactsService
    
    result = EvidenceToFactsService.generate_facts_section(document)
    
    if not result['content']:
        return JsonResponse({
            'success': False,
            'error': 'No video segments marked for inclusion in complaint'
        })
    
    # Split content into individual facts for display
    facts = result['content'].split('\n\n')
    
    return JsonResponse({
        'success': True,
        'facts': facts,
        'exhibits': result.get('exhibits_list', ''),
        'metadata': result['metadata']
    })