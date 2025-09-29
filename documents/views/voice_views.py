# documents/views/voice_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..models import LawsuitDocument
from datetime import datetime
import json
import traceback

@login_required
def voice_recorder_view(request):
    """Voice recording interface for mobile users"""
    return render(request, 'documents/voice_recorder.html')

@login_required
@require_http_methods(["POST"])
def voice_create_document(request):
    """Create document from voice transcript"""
    try:
        data = json.loads(request.body)
        transcript = data.get('transcript', '')
        parsed = data.get('parsed_data', {})
        
        # Parse the date
        incident_date = parse_date_string(parsed.get('incident_date'))
        
        # Create the document with ALL fields explicitly set
        document = LawsuitDocument.objects.create(
            user=request.user,
            title=f"Voice Recording - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description=transcript or '',
            incident_date=incident_date,
            incident_location=parsed.get('location', ''),
            incident_street_address='',
            incident_city=parsed.get('city', ''),
            incident_state=parsed.get('state', ''),
            incident_zip_code='',
            defendants=parsed.get('defendants', ''),
            youtube_url_1='',
            youtube_url_2='',
            youtube_url_3='',
            youtube_url_4='',
            additional_evidence='',
            include_videos_in_document=False,
            suggested_federal_district='',
            user_confirmed_district='',
            district_lookup_confidence='',
            status='draft'
        )
        
        return JsonResponse({
            'success': True,
            'document_id': document.pk,
            'redirect_url': f'/documents/{document.pk}/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=400)

def parse_date_string(date_str):
    """Try to parse various date formats"""
    if not date_str or date_str == 'Not found':
        return None
    
    formats = ['%B %d, %Y', '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue
    return None