# documents/services/violation_analysis_service.py

# What this service does:

# Extracts pattern definitions from the original class into organized constants
# Makes methods static using @classmethod (don't need a document instance)
# Adds helper methods for getting human-readable descriptions
# Improves organization with clear separation of concerns

class ViolationAnalysisService:
    """Service to analyze incident descriptions and determine violation types"""

    # Violation pattern definitions
    VIOLATION_PATTERNS = {
        'interference_recording': [
            'recording', 'filming', 'camera', 'video', 'stopped recording',
            'blocked camera', 'interfered with recording', 'cant record',
            'no filming', 'no cameras', 'put camera away', 'stop recording',
            'turn off camera', 'no video', 'cant film', 'photography',
            'taking pictures', 'photos', 'picture taking'
        ],
        'forced_to_leave_public': [
            'kicked out', 'escorted out', 'forced to leave', 'made me leave',
            'told to leave', 'removed from', 'excluded from', 'banned from',
            'not allowed', 'get out', 'you need to leave', 'asked to leave',
            'escorted away', 'thrown out', 'pushed out', 'ordered to leave'
        ],
        'retaliation_protected_speech': [
            'retaliation', 'retaliated', 'because I complained', 'payback',
            'got back at me', 'targeted me', 'harassment', 'followed up',
            'came back', 'returned later', 'next time', 'remembered me',
            'harassed', 'singled out', 'revenge', 'got even', 'punishment'
        ],
        'threatened_arrest_public': [
            'threatened', 'threat', 'will arrest', 'going to arrest',
            'arrest you if', 'said he would', 'warned me', 'told me I would be arrested',
            'threatened to arrest', 'said I would go to jail', 'going to jail',
            'youre under arrest if', 'arrest threat', 'warned of arrest'
        ]
    }

    # Forum type pattern definitions
    FORUM_PATTERNS = {
        'traditional_public_forum': [
            'sidewalk', 'street', 'plaza', 'park', 'courthouse steps',
            'public square', 'town square', 'public walkway', 'street corner',
            'parking lot', 'public parking', 'outside', 'front of building',
            'public area', 'crosswalk', 'intersection'
        ],
        'designated_public_forum': [
            'city hall', 'dmv', 'government building', 'public meeting',
            'courthouse', 'municipal building', 'town hall', 'civic center',
            'public library', 'community center', 'government office',
            'county building', 'federal building', 'state building'
        ],
        'limited_public_forum': [
            'lobby', 'waiting area', 'public counter', 'service window',
            'reception area', 'public entrance', 'foyer', 'vestibule',
            'public restroom', 'elevator', 'hallway'
        ]
    }

    @classmethod
    def analyze_violation_type(cls, description):
        """Analyze incident description to determine violation type"""
        if not description:
            return 'threatened_arrest_public'  # default
        
        description_lower = description.lower()
        
        # Check patterns in priority order (most specific first)
        for violation_type, patterns in cls.VIOLATION_PATTERNS.items():
            if violation_type == 'threatened_arrest_public':
                continue  # Check this last as it's the default
            
            if any(phrase in description_lower for phrase in patterns):
                return violation_type
        
        # Check threatened arrest patterns last
        if any(phrase in description_lower for phrase in cls.VIOLATION_PATTERNS['threatened_arrest_public']):
            return 'threatened_arrest_public'
        
        # Default fallback
        return 'threatened_arrest_public'

    @classmethod
    def analyze_location_type(cls, location):
        """Analyze location to determine forum type"""
        if not location:
            return 'traditional_public_forum'  # default to strongest protection
        
        location_lower = location.lower()
        
        # Check each forum type
        for forum_type, patterns in cls.FORUM_PATTERNS.items():
            if any(term in location_lower for term in patterns):
                return forum_type
        
        # Default to traditional public forum (strongest protection)
        return 'traditional_public_forum'

    @classmethod
    def get_violation_description(cls, violation_type):
        """Get human-readable description of violation type"""
        descriptions = {
            'interference_recording': 'Interference with Recording',
            'forced_to_leave_public': 'Forced Removal from Public Area',
            'retaliation_protected_speech': 'Retaliation for Protected Speech',
            'threatened_arrest_public': 'Threatened Arrest in Public Area'
        }
        return descriptions.get(violation_type, violation_type.replace('_', ' ').title())

    @classmethod
    def get_forum_description(cls, forum_type):
        """Get human-readable description of forum type"""
        descriptions = {
            'traditional_public_forum': 'Traditional Public Forum',
            'designated_public_forum': 'Designated Public Forum',
            'limited_public_forum': 'Limited Public Forum'
        }
        return descriptions.get(forum_type, forum_type.replace('_', ' ').title())