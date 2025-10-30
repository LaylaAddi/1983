"""
Video evidence management views.
Dedicated workflow for collecting, reviewing, and analyzing video evidence.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
import json
from accounts.models import Subscription
from ..models import LawsuitDocument, VideoEvidence, Person, TranscriptQuote
from ..services.whisper_transcript_service import WhisperTranscriptService
from accounts.emails import EmailService
from decimal import Decimal


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

    # Load people for speaker attribution
    people = Person.objects.filter(document=document)

    context = {
        'document': document,
        'evidence_segments': evidence_segments,
        'segments_by_video': segments_by_video,
        'total_segments': evidence_segments.count(),
        'reviewed_count': evidence_segments.filter(is_reviewed=True).count(),
        'included_count': evidence_segments.filter(include_in_complaint=True).count(),
        'people': people,
        'has_people': people.exists(),
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
        source_type = data.get('source_type', 'body_camera')

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
        
        # Calculate duration in minutes
        duration_minutes = duration / 60.0

        # Check if document has enough extraction minutes remaining
        if document.extraction_minutes_remaining < duration_minutes:
            try:
                subscription = Subscription.objects.get(user=request.user)

                if subscription.is_standard:
                    error_msg = (
                        f'Insufficient extraction time. This segment requires {duration_minutes:.1f} minutes, '
                        f'but you have {document.extraction_minutes_remaining:.1f} minutes remaining. '
                        f'<a href="/accounts/pricing/" class="text-warning"><strong>Purchase an add-on bundle</strong></a> '
                        f'to get +15 minutes for $29.'
                    )
                else:
                    error_msg = (
                        f'Insufficient extraction time. This segment requires {duration_minutes:.1f} minutes, '
                        f'but you have {document.extraction_minutes_remaining:.1f} minutes remaining. '
                        f'<a href="/accounts/pricing/" class="text-warning"><strong>Upgrade to Standard plan</strong></a> '
                        f'or purchase an add-on bundle to get more extraction time.'
                    )
            except Subscription.DoesNotExist:
                error_msg = 'No subscription found. Please contact support.'

            return JsonResponse({
                'success': False,
                'error': error_msg,
                'requires_payment': True,
                'remaining_minutes': float(document.extraction_minutes_remaining)
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
            extraction_cost=result.get('cost_estimate', 0),
            source_type=source_type
        )
        
        # Track extraction minutes used
        from decimal import Decimal
        document.extraction_minutes_used += Decimal(str(duration_minutes))
        document.save()
        
        return JsonResponse({
            'success': True,
            'segment_id': evidence.id,
            'text': result['text'],
            'duration_minutes': duration_minutes,
            'remaining_minutes': float(document.extraction_minutes_remaining)
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
        source_type = data.get('source_type', 'body_camera')

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
            manually_entered=True,
            source_type=source_type
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
    
    # Create or update Statement of Facts section
    facts_section, created = DocumentSection.objects.get_or_create(
        document=document,
        section_type='facts',
        defaults={
            'title': 'Statement of Facts',
            'order': 4  # Typical position for facts section
        }
    )

    # APPEND video evidence quotes to existing content instead of replacing
    if facts_section.content and facts_section.content.strip():
        # Existing content present - append video evidence as continuation
        # First, find the last fact number to continue numbering
        import re
        existing_numbers = re.findall(r'^(\d+)\.', facts_section.content, re.MULTILINE)
        if existing_numbers:
            last_number = max(int(n) for n in existing_numbers)
            # Renumber video facts to continue from existing facts
            video_facts = result['content']
            # Replace numbering in video facts to continue sequence
            def renumber(match):
                old_num = int(match.group(1))
                new_num = last_number + old_num
                return f"{new_num}."
            video_facts = re.sub(r'^(\d+)\.', renumber, video_facts, flags=re.MULTILINE)

            # Append with section header
            facts_section.content = (
                f"{facts_section.content.strip()}\n\n"
                f"## Video Evidence\n\n"
                f"{video_facts}"
            )
        else:
            # No existing numbered facts, just append
            facts_section.content = (
                f"{facts_section.content.strip()}\n\n"
                f"## Video Evidence\n\n"
                f"{result['content']}"
            )
    else:
        # No existing content, use video evidence as the entire content
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


# ==================== PERSON MANAGEMENT ====================

@login_required
def get_document_people(request, pk):
    """
    Get all people involved in a document (plaintiff, defendants, witnesses).
    Returns JSON list of people with their details.
    """
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    people = Person.objects.filter(document=document)

    people_data = [{
        'id': person.id,
        'name': person.name,
        'role': person.role,
        'role_display': person.get_role_display(),
        'title': person.title,
        'badge_number': person.badge_number,
        'display_name': person.display_name,
        'color_code': person.color_code,
        'notes': person.notes
    } for person in people]

    return JsonResponse({
        'success': True,
        'people': people_data
    })


@login_required
@require_POST
def add_person(request, pk):
    """
    Add a new person to the document.
    Creates a Person record for speaker attribution.
    """
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)

    try:
        data = json.loads(request.body)

        # Assign default colors based on role
        color_map = {
            'plaintiff': '#0d6efd',  # Blue
            'defendant': '#dc3545',  # Red
            'witness': '#198754',    # Green
            'other': '#6c757d'       # Gray
        }

        person = Person.objects.create(
            document=document,
            name=data.get('name', '').strip(),
            role=data.get('role', 'other'),
            title=data.get('title', '').strip(),
            badge_number=data.get('badge_number', '').strip(),
            notes=data.get('notes', '').strip(),
            color_code=data.get('color_code', color_map.get(data.get('role', 'other'), '#6c757d'))
        )

        return JsonResponse({
            'success': True,
            'person': {
                'id': person.id,
                'name': person.name,
                'role': person.role,
                'role_display': person.get_role_display(),
                'title': person.title,
                'badge_number': person.badge_number,
                'display_name': person.display_name,
                'color_code': person.color_code,
                'notes': person.notes
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def update_person(request, pk, person_id):
    """Update person details"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    person = get_object_or_404(Person, pk=person_id, document=document)

    try:
        data = json.loads(request.body)

        person.name = data.get('name', person.name).strip()
        person.role = data.get('role', person.role)
        person.title = data.get('title', person.title).strip()
        person.badge_number = data.get('badge_number', person.badge_number).strip()
        person.notes = data.get('notes', person.notes).strip()
        person.color_code = data.get('color_code', person.color_code)
        person.save()

        return JsonResponse({
            'success': True,
            'person': {
                'id': person.id,
                'name': person.name,
                'role': person.role,
                'role_display': person.get_role_display(),
                'title': person.title,
                'badge_number': person.badge_number,
                'display_name': person.display_name,
                'color_code': person.color_code,
                'notes': person.notes
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def delete_person(request, pk, person_id):
    """Delete a person (only if they have no quotes)"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    person = get_object_or_404(Person, pk=person_id, document=document)

    # Check if person has any quotes
    if person.quotes.exists():
        return JsonResponse({
            'success': False,
            'error': f'Cannot delete {person.name} - they have {person.quotes.count()} attributed quotes. Remove quotes first.'
        }, status=400)

    person.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def sync_people_from_defendants(request, pk):
    """
    Auto-sync people from document.defendants field.
    Parses the defendants field and creates Person records.
    """
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)

    try:
        # Parse defendants field (assuming format: "Officer John Smith, Detective Jane Doe")
        defendants_text = document.defendants.strip()
        if not defendants_text:
            return JsonResponse({
                'success': False,
                'error': 'No defendants listed in document'
            }, status=400)

        # Split by comma or newline
        import re
        defendant_names = re.split(r'[,\n]+', defendants_text)

        created_count = 0
        skipped_count = 0

        for name_with_title in defendant_names:
            name_with_title = name_with_title.strip()
            if not name_with_title:
                continue

            # Try to extract title (Officer, Detective, etc.)
            title = ''
            name = name_with_title

            # Common titles
            title_patterns = [r'^(Officer|Detective|Sergeant|Lieutenant|Captain|Chief|Deputy)\s+(.+)$']
            for pattern in title_patterns:
                match = re.match(pattern, name_with_title, re.IGNORECASE)
                if match:
                    title = match.group(1)
                    name = match.group(2)
                    break

            # Check if already exists
            if Person.objects.filter(document=document, name=name, role='defendant').exists():
                skipped_count += 1
                continue

            # Create defendant
            Person.objects.create(
                document=document,
                name=name,
                role='defendant',
                title=title,
                color_code='#dc3545'  # Red for defendants
            )
            created_count += 1

        # Also create plaintiff (the user)
        plaintiff_name = f"{request.user.first_name} {request.user.last_name}".strip()
        if not plaintiff_name:
            plaintiff_name = request.user.username

        if not Person.objects.filter(document=document, role='plaintiff').exists():
            Person.objects.create(
                document=document,
                name=plaintiff_name,
                role='plaintiff',
                color_code='#0d6efd'  # Blue for plaintiff
            )
            created_count += 1

        return JsonResponse({
            'success': True,
            'created_count': created_count,
            'skipped_count': skipped_count,
            'message': f'Created {created_count} people ({skipped_count} already existed)'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ==================== TRANSCRIPT QUOTE MANAGEMENT ====================

@login_required
def get_segment_quotes(request, pk, segment_id):
    """Get all quotes for a video evidence segment"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    segment = get_object_or_404(VideoEvidence, pk=segment_id, document=document)

    quotes = TranscriptQuote.objects.filter(video_evidence=segment)

    quotes_data = [{
        'id': quote.id,
        'text': quote.text,
        'start_position': quote.start_position,
        'end_position': quote.end_position,
        'speaker': {
            'id': quote.speaker.id,
            'name': quote.speaker.name,
            'display_name': quote.speaker.display_name,
            'role': quote.speaker.role,
            'color_code': quote.speaker.color_code
        },
        'approximate_timestamp': quote.approximate_timestamp,
        'significance': quote.significance,
        'violation_tags': quote.violation_tags,
        'notes': quote.notes,
        'sort_order': quote.sort_order,
        'include_in_document': quote.include_in_document,
        'formatted_citation': quote.formatted_citation
    } for quote in quotes]

    return JsonResponse({
        'success': True,
        'quotes': quotes_data
    })


@login_required
@require_POST
def add_quote(request, pk, segment_id):
    """
    Add a new transcript quote with speaker attribution.
    Triggered when user highlights text and assigns a speaker.
    """
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    segment = get_object_or_404(VideoEvidence, pk=segment_id, document=document)

    try:
        data = json.loads(request.body)

        speaker_id = data.get('speaker_id')
        if not speaker_id:
            return JsonResponse({
                'success': False,
                'error': 'Speaker is required'
            }, status=400)

        speaker = get_object_or_404(Person, pk=speaker_id, document=document)

        # Get the next sort_order
        max_order = TranscriptQuote.objects.filter(video_evidence=segment).aggregate(
            models.Max('sort_order')
        )['sort_order__max'] or 0

        quote = TranscriptQuote.objects.create(
            video_evidence=segment,
            text=data.get('text', '').strip(),
            start_position=data.get('start_position', 0),
            end_position=data.get('end_position', 0),
            speaker=speaker,
            approximate_timestamp=data.get('approximate_timestamp', '').strip(),
            significance=data.get('significance', '').strip(),
            violation_tags=data.get('violation_tags', '').strip(),
            notes=data.get('notes', '').strip(),
            sort_order=max_order + 1,
            include_in_document=data.get('include_in_document', True)
        )

        return JsonResponse({
            'success': True,
            'quote': {
                'id': quote.id,
                'text': quote.text,
                'start_position': quote.start_position,
                'end_position': quote.end_position,
                'speaker': {
                    'id': speaker.id,
                    'name': speaker.name,
                    'display_name': speaker.display_name,
                    'role': speaker.role,
                    'color_code': speaker.color_code
                },
                'approximate_timestamp': quote.approximate_timestamp,
                'significance': quote.significance,
                'violation_tags': quote.violation_tags,
                'notes': quote.notes,
                'sort_order': quote.sort_order,
                'include_in_document': quote.include_in_document,
                'formatted_citation': quote.formatted_citation
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def update_quote(request, pk, segment_id, quote_id):
    """Update a transcript quote"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    segment = get_object_or_404(VideoEvidence, pk=segment_id, document=document)
    quote = get_object_or_404(TranscriptQuote, pk=quote_id, video_evidence=segment)

    try:
        data = json.loads(request.body)

        if 'speaker_id' in data:
            speaker = get_object_or_404(Person, pk=data['speaker_id'], document=document)
            quote.speaker = speaker

        if 'text' in data:
            quote.text = data['text'].strip()
        if 'start_position' in data:
            quote.start_position = data['start_position']
        if 'end_position' in data:
            quote.end_position = data['end_position']
        if 'approximate_timestamp' in data:
            quote.approximate_timestamp = data['approximate_timestamp'].strip()
        if 'significance' in data:
            quote.significance = data['significance'].strip()
        if 'violation_tags' in data:
            quote.violation_tags = data['violation_tags'].strip()
        if 'notes' in data:
            quote.notes = data['notes'].strip()
        if 'sort_order' in data:
            quote.sort_order = data['sort_order']
        if 'include_in_document' in data:
            quote.include_in_document = data['include_in_document']

        quote.save()

        return JsonResponse({
            'success': True,
            'quote': {
                'id': quote.id,
                'text': quote.text,
                'speaker': {
                    'id': quote.speaker.id,
                    'name': quote.speaker.name,
                    'display_name': quote.speaker.display_name,
                    'role': quote.speaker.role,
                    'color_code': quote.speaker.color_code
                },
                'formatted_citation': quote.formatted_citation
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def delete_quote(request, pk, segment_id, quote_id):
    """Delete a transcript quote"""
    document = get_object_or_404(LawsuitDocument, pk=pk, user=request.user)
    segment = get_object_or_404(VideoEvidence, pk=segment_id, document=document)
    quote = get_object_or_404(TranscriptQuote, pk=quote_id, video_evidence=segment)

    quote.delete()
    return JsonResponse({'success': True})