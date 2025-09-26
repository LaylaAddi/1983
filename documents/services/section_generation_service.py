# documents/services/section_generation_service.py
from django.db import models
from ..models import DocumentSection

class SectionGenerationService:
    """Service to create and manage document sections"""

    @staticmethod
    def create_or_update_section(document, section_type, title, content, order=None):
        """Create a new section or update existing one"""
        if order is None:
            order = SectionGenerationService._get_next_order(document)
        
        section, created = DocumentSection.objects.get_or_create(
            document=document,
            section_type=section_type,
            defaults={
                'title': title,
                'content': content,
                'order': order
            }
        )
        
        # Always update content and title for existing sections
        if not created:
            section.title = title
            section.content = content
            section.save()
        
        return section, created

    @staticmethod
    def create_section_from_template(document, template, context_data):
        """Create a section from a legal template with context data"""
        from .template_matching_service import TemplateMatchingService
        
        # Render the template content
        rendered_content = TemplateMatchingService.render_template_content(
            template.template_text, 
            context_data
        )
        
        # Get the display title for the section type
        title = SectionGenerationService._get_section_title(template.section_type)
        
        # Get the standard order for this section type
        order = SectionGenerationService._get_standard_order(template.section_type)
        
        return SectionGenerationService.create_or_update_section(
            document=document,
            section_type=template.section_type,
            title=title,
            content=rendered_content,
            order=order
        )

    @staticmethod
    def bulk_generate_sections(document, templates, context_data):
        """Generate multiple sections from templates"""
        results = []
        
        for template in templates:
            section, created = SectionGenerationService.create_section_from_template(
                document, template, context_data
            )
            results.append({
                'section': section,
                'created': created,
                'template': template
            })
        
        return results

    @staticmethod
    def reorder_sections(document):
        """Reorder all sections according to standard legal document order"""
        sections = DocumentSection.objects.filter(document=document)
        
        for section in sections:
            standard_order = SectionGenerationService._get_standard_order(section.section_type)
            if section.order != standard_order:
                section.order = standard_order
                section.save()

    @staticmethod
    def delete_section(document, section_type):
        """Delete a specific section type from document"""
        try:
            section = DocumentSection.objects.get(
                document=document,
                section_type=section_type
            )
            section.delete()
            return True
        except DocumentSection.DoesNotExist:
            return False

    @staticmethod
    def get_document_sections(document, ordered=True):
        """Get all sections for a document"""
        sections = DocumentSection.objects.filter(document=document)
        if ordered:
            sections = sections.order_by('order')
        return sections

    @staticmethod
    def get_missing_sections(document):
        """Get list of standard sections not yet created for this document"""
        existing_types = set(
            DocumentSection.objects.filter(document=document).values_list(
                'section_type', flat=True
            )
        )
        
        all_section_types = set(dict(DocumentSection.SECTION_TYPES).keys())
        missing_types = all_section_types - existing_types
        
        return [
            {
                'section_type': section_type,
                'title': SectionGenerationService._get_section_title(section_type),
                'order': SectionGenerationService._get_standard_order(section_type)
            }
            for section_type in missing_types
        ]

    @staticmethod
    def get_section_statistics(document):
        """Get statistics about document sections"""
        sections = DocumentSection.objects.filter(document=document)
        total_sections = sections.count()
        total_possible = len(DocumentSection.SECTION_TYPES)
        
        return {
            'total_sections': total_sections,
            'total_possible': total_possible,
            'completion_percentage': (total_sections / total_possible * 100) if total_possible > 0 else 0,
            'missing_count': total_possible - total_sections,
            'sections_by_type': list(sections.values('section_type', 'title', 'order')),
            'missing_sections': SectionGenerationService.get_missing_sections(document)
        }

    @staticmethod
    def create_all_default_sections(document):
        """Create all 7 standard legal sections with default content"""
        
        # Get user's full state name from profile
        user_profile = getattr(document.user, 'profile', None)
        user_state = '[STATE]'  # default fallback

        print(f"DEBUG: user_profile = {user_profile}")
        print(f"DEBUG: user_profile.state = {user_profile.state if user_profile else 'None'}")
        
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
        
        # Default content templates for each section type
        default_content = {
            'introduction': 'Plaintiff brings this civil rights action seeking damages and injunctive relief for violations of constitutional rights under 42 U.S.C. § 1983.',
            'jurisdiction': 'This Court has jurisdiction over this action pursuant to 28 U.S.C. §§ 1331 and 1343, as this action arises under the Constitution and laws of the United States. Venue is proper in this district under 28 U.S.C. § 1391(b).',
            'parties': f'Plaintiff is a citizen and resident of {user_state}. {document.defendants or "[DEFENDANTS TO BE IDENTIFIED]"} are individuals acting under color of state law.',
            'facts': f'On {document.incident_date.strftime("%B %d, %Y") if document.incident_date else "[DATE]"}, at {document.incident_location or "[LOCATION]"}, the following events occurred: {document.description or "[DESCRIPTION TO BE ADDED]"}',
            'claims': 'COUNT I - VIOLATION OF CIVIL RIGHTS (42 U.S.C. § 1983)\n\nDefendants violated Plaintiff\'s constitutional rights by [SPECIFIC VIOLATIONS TO BE DETAILED].',
            'prayer': 'WHEREFORE, Plaintiff respectfully requests that this Court:\na) Award compensatory and punitive damages;\nb) Enter injunctive relief;\nc) Award attorney\'s fees and costs pursuant to 42 U.S.C. § 1988;\nd) Grant such other relief as this Court deems just and proper.',
            'jury_demand': 'Plaintiff hereby demands a trial by jury on all issues so triable as a matter of right pursuant to Federal Rule of Civil Procedure 38.'
        }
        
        results = []
        sections_created = 0
        sections_updated = 0
        
        for section_type, content in default_content.items():
            title = SectionGenerationService._get_section_title(section_type)
            order = SectionGenerationService._get_standard_order(section_type)
            
            section, created = SectionGenerationService.create_or_update_section(
                document=document,
                section_type=section_type,
                title=title,
                content=content,
                order=order
            )
            
            results.append({
                'section': section,
                'created': created,
                'section_type': section_type
            })
            
            if created:
                sections_created += 1
            else:
                sections_updated += 1
        
        return {
            'sections_created': sections_created,
            'sections_updated': sections_updated,
            'total_sections': len(results),
            'results': results,
            'document': document
        }

    @staticmethod
    def _get_next_order(document):
        """Get the next available order number for a document"""
        max_order = DocumentSection.objects.filter(document=document).aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0
        return max_order + 1

    @staticmethod
    def _get_section_title(section_type):
        """Get the display title for a section type"""
        return dict(DocumentSection.SECTION_TYPES).get(
            section_type, 
            section_type.replace('_', ' ').title()
        )

    @staticmethod
    def _get_standard_order(section_type):
        """Get the standard legal order for a section type"""
        # Standard legal document order
        standard_order = {
            'introduction': 1,
            'jurisdiction': 2,
            'parties': 3,
            'facts': 4,
            'claims': 5,
            'prayer': 6,
            'jury_demand': 7
        }
        return standard_order.get(section_type, 999)  # Unknown types go to end