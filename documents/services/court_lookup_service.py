# documents/services/court_lookup_service.py
"""
Main court lookup service that delegates to state-specific lookup services
"""

from typing import Dict, Optional, List

class CourtLookupService:
    """Main service that delegates to state-specific lookup services"""
    
    # Cache for loaded state services
    _state_services = {}
    
    @classmethod
    def lookup_court_by_location(cls, city: str, state: str, county: Optional[str] = None) -> Dict:
        """
        Lookup federal district court by delegating to state-specific service
        """
        if not city or not state:
            return {
                'success': False,
                'error': 'City and state are required',
                'confidence': 'none'
            }
        
        city = city.strip().title()
        state = state.upper().strip()
        county = county.strip().title() if county else None
        
        # Get state-specific service
        state_service = cls._get_state_service(state)
        
        if not state_service:
            return {
                'success': False,
                'error': f'State {state} not yet supported in court database',
                'confidence': 'none'
            }
        
        # Delegate to state service
        try:
            return state_service.lookup_court(city, county)
        except Exception as e:
            return {
                'success': False,
                'error': f'Error looking up court for {city}, {state}: {str(e)}',
                'confidence': 'none'
            }
    
    @classmethod
    def _get_state_service(cls, state: str):
        """Get or load the state-specific lookup service"""
        if state in cls._state_services:
            return cls._state_services[state]
        
        # Map state codes to service classes
        state_service_map = {
            'NY': ('new_york_lookup', 'NewYorkStateLookup'),
            'PA': ('pennsylvania_lookup', 'PennsylvaniaStateLookup'),
            # Add more states as we create them
            # 'CA': ('california_lookup', 'CaliforniaStateLookup'),
            # 'TX': ('texas_lookup', 'TexasStateLookup'),
        }
        
        if state not in state_service_map:
            return None
        
        module_name, class_name = state_service_map[state]
        
        try:
            # Import the state-specific module
            module = __import__(f'documents.services.court_data.states.{module_name}', fromlist=[class_name])
            
            # Get the service class
            service_class = getattr(module, class_name)
            
            # Create and cache the service instance
            cls._state_services[state] = service_class()
            return cls._state_services[state]
                
        except (ImportError, AttributeError) as e:
            print(f"Error loading state service for {state}: {e}")
            return None
    
    @classmethod
    def get_supported_states(cls) -> List[str]:
        """Get list of states currently supported"""
        return ['NY', 'PA']  # Will expand as we add more states
    
    @classmethod
    def get_confidence_description(cls, confidence: str) -> str:
        """Get human-readable description of confidence level"""
        descriptions = {
            'high': 'High confidence - Location matches known court division or county',
            'medium': 'Medium confidence - Location matches geographic patterns',
            'low': 'Low confidence - Using default district for state, please verify',
            'manual': 'Manually selected by user',
            'none': 'Unable to determine court location'
        }
        return descriptions.get(confidence, 'Unknown confidence level')
    
    @classmethod
    def test_lookup(cls, city: str, state: str) -> str:
        """Test method for debugging court lookups"""
        result = cls.lookup_court_by_location(city, state)
        if result['success']:
            return f"SUCCESS: {result['formatted_court']} (Confidence: {result['confidence']})"
        else:
            return f"ERROR: {result['error']}"
    
    @classmethod
    def validate_manual_court_entry(cls, court_text: str) -> Dict:
        """Validate manually entered court information"""
        if not court_text or len(court_text.strip()) < 10:
            return {
                'valid': False,
                'error': 'Court information must be at least 10 characters'
            }
        
        # Check for required components
        text_upper = court_text.upper()
        has_district_court = 'DISTRICT COURT' in text_upper
        has_united_states = 'UNITED STATES' in text_upper
        
        if not has_district_court:
            return {
                'valid': False,
                'error': 'Must include "District Court" in the court name'
            }
        
        if not has_united_states:
            return {
                'valid': False,
                'error': 'Must include "United States" in the court name'
            }
        
        return {
            'valid': True,
            'formatted': court_text.strip()
        }
    
    @classmethod
    def get_all_districts_for_state(cls, state: str) -> Dict:
        """Get all federal districts for a given state"""
        state = state.upper().strip()
        
        state_service = cls._get_state_service(state)
        if not state_service:
            return {
                'success': False,
                'error': f'State {state} not found'
            }
        
        try:
            districts = state_service.get_all_districts()
            return {
                'success': True,
                'state_name': state_service.districts['name'],
                'districts': districts
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting districts for {state}: {str(e)}'
            }