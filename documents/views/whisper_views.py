"""
Real Whisper API transcript extraction views.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from ..services.whisper_transcript_service import WhisperTranscriptService


@login_required
@require_POST
def extract_transcript_whisper(request):
    """
    Extract transcript using real Whisper API.
    Requires OpenAI credit on account.
    """
    try:
        data = json.loads(request.body)
        youtube_url = data.get('youtube_url', '')
        start_time_str = data.get('start_time', '0')
        end_time_str = data.get('end_time', '30')
        
        # Validate inputs
        if not youtube_url:
            return JsonResponse({
                'success': False,
                'error': 'YouTube URL is required'
            })
        
        # Parse timestamps to seconds
        start_seconds = WhisperTranscriptService.parse_timestamp(start_time_str)
        end_seconds = WhisperTranscriptService.parse_timestamp(end_time_str)
        
        # Call Whisper service
        result = WhisperTranscriptService.get_transcript(
            youtube_url,
            start_time=start_seconds,
            end_time=end_seconds
        )
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })