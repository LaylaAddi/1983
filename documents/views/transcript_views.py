"""
Views for YouTube transcript extraction.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json


@login_required
@require_POST
def extract_transcript_mock(request):
    """
    Mock transcript extraction for testing UI.
    Returns fake data simulating Whisper API response.
    """
    try:
        data = json.loads(request.body)
        youtube_url = data.get('youtube_url', '')
        start_time = data.get('start_time', '0')
        end_time = data.get('end_time', '30')
        
        # Validate inputs
        if not youtube_url:
            return JsonResponse({
                'success': False,
                'error': 'YouTube URL is required'
            })
        
        # Calculate duration
        try:
            start_sec = parse_time_to_seconds(start_time)
            end_sec = parse_time_to_seconds(end_time)
            duration = end_sec - start_sec
        except:
            duration = 30
        
        # Mock transcript text
        mock_text = (
            f"[MOCK TRANSCRIPT - Testing Mode]\n\n"
            f"This is simulated transcript text from {start_time} to {end_time}. "
            f"In production, this would contain the actual spoken words from the video. "
            f"The officer approached without reasonable suspicion and demanded identification. "
            f"When asked if I was being detained, the officer became aggressive and threatened arrest. "
            f"I clearly stated I was exercising my First Amendment right to record in public. "
            f"The officer then grabbed my camera and placed me in handcuffs without legal justification."
        )
        
        return JsonResponse({
            'success': True,
            'text': mock_text,
            'cost_estimate': round(duration * 0.006 / 60, 3),
            'duration_seconds': duration,
            'is_mock': True
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def parse_time_to_seconds(time_str):
    """Convert MM:SS or HH:MM:SS to seconds."""
    if not time_str:
        return 0
    
    time_str = str(time_str).strip()
    
    if time_str.isdigit():
        return int(time_str)
    
    parts = time_str.split(':')
    if len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:  # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    
    return 0