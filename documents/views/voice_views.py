# documents/views/voice_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import LawsuitDocument
from datetime import datetime
import json
import re

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
        
        # Create the document
        document = LawsuitDocument.objects.create(
            user=request.user,
            title=f"Voice Recording - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description=transcript,
            incident_date=parse_date_string(parsed.get('incident_date')),
            incident_location=parsed.get('location', ''),
            incident_city=parsed.get('city', ''),
            incident_state=parsed.get('state', ''),
            defendants=parsed.get('defendants', ''),
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
            'error': str(e)
        }, status=400)

def parse_date_string(date_str):
    """Try to parse various date formats"""
    if not date_str or date_str == 'Not found':
        return None
    
    # Try common formats
    formats = ['%B %d, %Y', '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue
    return None