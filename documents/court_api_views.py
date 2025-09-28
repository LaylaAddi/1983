# documents/views/court_api_views.py
"""
API views for court lookup functionality
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from ..services.court_lookup_service import CourtLookupService


@method_decorator(login_required, name='dispatch')
class CourtLookupAPIView(View):
    """API endpoint for court lookup requests"""
    
    def post(self, request):
        """Handle court lookup POST requests"""
        try:
            # Parse JSON data from request
            data = json.loads(request.body)
            city = data.get('city', '').strip()
            state = data.get('state', '').strip()
            county = data.get('county', '').strip() or None
            
            if not city or not state:
                return JsonResponse({
                    'success': False,
                    'error': 'Both city and state are required'
                }, status=400)
            
            # Perform court lookup
            result = CourtLookupService.lookup_court_by_location(
                city=city,
                state=state,
                county=county
            )
            
            if result['success']:
                # Add additional information for the frontend
                response_data = {
                    'success': True,
                    'district': result['district'],
                    'division': result['division'],
                    'state_name': result['state_name'],
                    'confidence': result['confidence'],
                    'formatted_court': result['formatted_court'],
                    'confidence_description': CourtLookupService.get_confidence_description(result['confidence'])
                }
            else:
                response_data = {
                    'success': False,
                    'error': result['error'],
                    'confidence': result.get('confidence', 'none')
                }
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class StateDistrictsAPIView(View):
    """API endpoint to get all districts for a state"""
    
    def get(self, request):
        """Handle GET requests for state districts"""
        state = request.GET.get('state', '').strip().upper()
        
        if not state:
            return JsonResponse({
                'success': False,
                'error': 'State parameter is required'
            }, status=400)
        
        try:
            result = CourtLookupService.get_all_districts_for_state(state)
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class SupportedStatesAPIView(View):
    """API endpoint to get list of supported states"""
    
    def get(self, request):
        """Handle GET requests for supported states"""
        try:
            supported_states = CourtLookupService.get_supported_states()
            return JsonResponse({
                'success': True,
                'supported_states': supported_states,
                'count': len(supported_states)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class ValidateManualCourtAPIView(View):
    """API endpoint to validate manually entered court information"""
    
    def post(self, request):
        """Handle validation of manual court entries"""
        try:
            data = json.loads(request.body)
            court_text = data.get('court_text', '').strip()
            
            if not court_text:
                return JsonResponse({
                    'valid': False,
                    'error': 'Court text is required'
                }, status=400)
            
            # Validate the manual court entry
            result = CourtLookupService.validate_manual_court_entry(court_text)
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'valid': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'valid': False,
                'error': f'Server error: {str(e)}'
            }, status=500)


# Function-based view alternatives (if you prefer these)
@login_required
@require_http_methods(["POST"])
def lookup_court_ajax(request):
    """Function-based view for court lookup (alternative to class-based view)"""
    try:
        data = json.loads(request.body)
        city = data.get('city', '').strip()
        state = data.get('state', '').strip()
        
        if not city or not state:
            return JsonResponse({
                'success': False,
                'error': 'Both city and state are required'
            }, status=400)
        
        result = CourtLookupService.lookup_court_by_location(city, state)
        
        if result['success']:
            result['confidence_description'] = CourtLookupService.get_confidence_description(result['confidence'])
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def test_court_lookup(request):
    """Test endpoint for debugging court lookup"""
    city = request.GET.get('city', '')
    state = request.GET.get('state', '')
    
    if not city or not state:
        return JsonResponse({
            'error': 'Please provide both city and state parameters'
        })
    
    try:
        # Test the lookup
        result = CourtLookupService.lookup_court_by_location(city, state)
        
        # Add debugging information
        debug_info = {
            'input': {'city': city, 'state': state},
            'result': result,
            'supported_states': CourtLookupService.get_supported_states(),
            'test_message': CourtLookupService.test_lookup(city, state)
        }
        
        return JsonResponse(debug_info, json_dumps_params={'indent': 2})
        
    except Exception as e:
        return JsonResponse({
            'error': f'Test failed: {str(e)}',
            'city': city,
            'state': state
        })