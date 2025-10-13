# documents\document_services.py
from django.template import Template, Context
from .models import LawsuitDocument, DocumentSection, LegalTemplate

class LegalDocumentPopulator:
    """Service to automatically populate documents with appropriate legal templates"""
    
    def __init__(self, lawsuit_document):
        self.document = lawsuit_document
        
    def analyze_violation_type(self):
        """Analyze the document to determine violation type"""
        description = self.document.description.lower()
        
        # Recording interference patterns
        if any(phrase in description for phrase in [
            'recording', 'filming', 'camera', 'video', 'stopped recording', 
            'blocked camera', 'interfered with recording', 'cant record',
            'no filming', 'no cameras', 'put camera away', 'stop recording',
            'turn off camera', 'no video', 'cant film', 'photography',
            'taking pictures', 'photos', 'picture taking'
        ]):
            return 'interference_recording'
        
        # Forced removal patterns  
        elif any(phrase in description for phrase in [
            'kicked out', 'escorted out', 'forced to leave', 'made me leave',
            'told to leave', 'removed from', 'excluded from', 'banned from',
            'not allowed', 'get out', 'you need to leave', 'asked to leave',
            'escorted away', 'thrown out', 'pushed out', 'ordered to leave'
        ]):
            return 'forced_to_leave_public'
        
        # Retaliation patterns
        elif any(phrase in description for phrase in [
            'retaliation', 'retaliated', 'because I complained', 'payback',
            'got back at me', 'targeted me', 'harassment', 'followed up',
            'came back', 'returned later', 'next time', 'remembered me',
            'harassed', 'singled out', 'revenge', 'got even', 'punishment'
        ]):
            return 'retaliation_protected_speech'
        
        # Threatened arrest patterns (most common, so check last)
        elif any(phrase in description for phrase in [
            'threatened', 'threat', 'will arrest', 'going to arrest',
            'arrest you if', 'said he would', 'warned me', 'told me I would be arrested',
            'threatened to arrest', 'said I would go to jail', 'going to jail',
            'youre under arrest if', 'arrest threat', 'warned of arrest'
        ]):
            return 'threatened_arrest_public'
        
        else:
            # Default to threatened arrest for ambiguous cases
            return 'threatened_arrest_public'
    
    def analyze_location_type(self):
        """Analyze the location to determine forum type"""
        location = self.document.incident_location.lower()
        
        # Traditional public forums (strongest First Amendment protection)
        if any(term in location for term in [
            'sidewalk', 'street', 'plaza', 'park', 'courthouse steps',
            'public square', 'town square', 'public walkway', 'street corner',
            'parking lot', 'public parking', 'outside', 'front of building',
            'public area', 'crosswalk', 'intersection'
        ]):
            return 'traditional_public_forum'
        
        # Designated public forums (government opens for public use)
        elif any(term in location for term in [
            'city hall', 'dmv', 'government building', 'public meeting',
            'courthouse', 'municipal building', 'town hall', 'civic center',
            'public library', 'community center', 'government office',
            'county building', 'federal building', 'state building'
        ]):
            return 'designated_public_forum'
        
        # Limited public forums (restricted access but still public)
        elif any(term in location for term in [
            'lobby', 'waiting area', 'public counter', 'service window',
            'reception area', 'public entrance', 'foyer', 'vestibule',
            'public restroom', 'elevator', 'hallway'
        ]):
            return 'limited_public_forum'
        
        else:
            return 'traditional_public_forum'  # default to strongest protection
    
    def get_template_context(self):
        """Prepare context data for template population"""
        user_profile = getattr(self.document.user, 'profile', None)
        
        return {
            'plaintiff_name': user_profile.full_legal_name if user_profile else self.document.user.get_full_name(),
            'incident_date': self.document.incident_date.strftime('%B %d, %Y') if self.document.incident_date else '[DATE OF INCIDENT]',
            'incident_location': self.document.incident_location or '[LOCATION]',
            'defendants': self.document.defendants or '[DEFENDANTS TO BE IDENTIFIED]',
            'description': self.document.description,
        }
    
    def populate_section(self, section_type, template_text, context):
        """Create or update a document section with populated template"""
        # Use Django template system to populate placeholders
        template = Template(template_text)
        populated_content = template.render(Context(context))
        
        # Always update the section content
        section, created = DocumentSection.objects.get_or_create(
            document=self.document,
            section_type=section_type,
            defaults={
                'title': dict(DocumentSection.SECTION_TYPES)[section_type],
                'content': populated_content,
                'order': list(dict(DocumentSection.SECTION_TYPES).keys()).index(section_type)
            }
        )
        
        # Always update content, whether created or not
        section.content = populated_content
        section.save()
        
        return section
    
    def auto_populate_document(self):
        """Main method to populate document with appropriate legal templates"""
        violation_type = self.analyze_violation_type()
        location_type = self.analyze_location_type()
        context = self.get_template_context()
        
        # Get matching templates
        templates = LegalTemplate.objects.filter(
            violation_type=violation_type,
            location_type=location_type
        )
        
        sections_created = []
        for template in templates:
            section = self.populate_section(
                template.section_type, 
                template.template_text, 
                context
            )
            sections_created.append(section)
        
        return {
            'violation_type': violation_type,
            'location_type': location_type,
            'sections_created': len(sections_created),
            'sections': sections_created
        }