# documents/services/template_matching_service.py
from django.template import Template, Context
from ..models import LegalTemplate

# Finds templates matching violation and location types
# Renders templates with document context data
# Provides preview functionality to see templates before applying
# Offers statistics about available templates
# Handles context preparation for template rendering



class TemplateMatchingService:
    """Service to find and process legal templates based on violation and location types"""

    @staticmethod
    def find_templates(violation_type, location_type):
        """Find all templates matching the violation and location types"""
        return LegalTemplate.objects.filter(
            violation_type=violation_type,
            location_type=location_type
        ).order_by('section_type')

    @staticmethod
    def get_template_by_section(violation_type, location_type, section_type):
        """Find a specific template by violation, location, and section type"""
        try:
            return LegalTemplate.objects.get(
                violation_type=violation_type,
                location_type=location_type,
                section_type=section_type
            )
        except LegalTemplate.DoesNotExist:
            return None

    @staticmethod
    def render_template_content(template_text, context_data):
        """Render template text with context data using Django template system"""
        if not template_text or not context_data:
            return template_text or ''
        
        try:
            template = Template(template_text)
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            # If template rendering fails, return original text
            # Log the error in production
            return template_text

    @staticmethod
    def prepare_document_context(document):
        """Prepare context data for template rendering from a document"""
        user_profile = getattr(document.user, 'profile', None)

        # Build the location string - prefer structured address over general location
        location_str = None
        if document.incident_city and document.incident_state:
            # Use structured address
            if document.incident_street_address:
                location_str = f"{document.incident_street_address}, {document.incident_city}, {document.incident_state}"
            else:
                location_str = f"{document.incident_city}, {document.incident_state}"
        elif document.incident_location:
            # Use general location field as fallback
            location_str = document.incident_location

        # If still no location, use placeholder
        if not location_str:
            location_str = '[LOCATION]'

        # Get user's state for plaintiff residency
        user_state = '[STATE]'
        if user_profile and user_profile.state:
            # State abbreviation to full name mapping
            state_names = {
                'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
                'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
                'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
                'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
                'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
                'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
                'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
                'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
                'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
                'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
                'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
                'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
                'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
            }
            user_state = state_names.get(user_profile.state.upper(), user_profile.state)

        return {
            'plaintiff_name': (
                user_profile.full_legal_name
                if user_profile else
                document.user.get_full_name() or document.user.username
            ),
            'plaintiff_state': user_state,
            'incident_date': (
                document.incident_date.strftime('%B %d, %Y')
                if document.incident_date else
                '[DATE OF INCIDENT]'
            ),
            'incident_location': location_str,
            'incident_city': document.incident_city or '[CITY]',
            'incident_state': document.incident_state or '[STATE]',
            'incident_street_address': document.incident_street_address or '',
            'defendants': document.defendants or '[DEFENDANTS TO BE IDENTIFIED]',
            'description': document.description or '[DESCRIPTION]',
        }

    @classmethod
    def get_available_sections(cls, violation_type, location_type):
        """Get list of available section types for given violation and location"""
        templates = cls.find_templates(violation_type, location_type)
        return [
            {
                'section_type': template.section_type,
                'section_display': template.get_section_type_display() if hasattr(template, 'get_section_type_display') else template.section_type.replace('_', ' ').title(),
                'is_required': getattr(template, 'is_required', True)
            }
            for template in templates
        ]

    @classmethod
    def preview_template(cls, violation_type, location_type, section_type, document=None):
        """Preview what a template would look like when rendered"""
        template = cls.get_template_by_section(violation_type, location_type, section_type)
        if not template:
            return None
        
        if document:
            context = cls.prepare_document_context(document)
            rendered_content = cls.render_template_content(template.template_text, context)
        else:
            rendered_content = template.template_text
        
        return {
            'section_type': template.section_type,
            'template_text': template.template_text,
            'rendered_content': rendered_content,
            'is_required': getattr(template, 'is_required', True)
        }

    @staticmethod
    def get_template_statistics():
        """Get statistics about available templates"""
        from django.db.models import Count
        
        stats = LegalTemplate.objects.values(
            'violation_type', 'location_type'
        ).annotate(
            section_count=Count('section_type')
        ).order_by('violation_type', 'location_type')
        
        return {
            'total_templates': LegalTemplate.objects.count(),
            'by_violation_location': list(stats),
            'violation_types': list(
                LegalTemplate.objects.values_list('violation_type', flat=True).distinct()
            ),
            'location_types': list(
                LegalTemplate.objects.values_list('location_type', flat=True).distinct()
            )
        }