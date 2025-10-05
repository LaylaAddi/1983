"""
Service to convert reviewed video evidence into Statement of Facts.
Generates numbered factual statements referencing video exhibits.
"""
from ..models import VideoEvidence


class EvidenceToFactsService:
    """Convert video evidence segments into legal Statement of Facts."""
    
    @staticmethod
    def generate_facts_section(document):
        """
        Generate Statement of Facts from video evidence marked for inclusion.
        
        Returns:
            dict with 'content' (formatted facts) and 'metadata'
        """
        # Get segments marked for inclusion, ordered by timestamp
        segments = VideoEvidence.objects.filter(
            document=document,
            include_in_complaint=True
        ).order_by('youtube_url', 'start_seconds')
        
        if not segments.exists():
            return {
                'content': '',
                'metadata': {
                    'segment_count': 0,
                    'error': 'No video segments marked for inclusion in complaint'
                }
            }
        
        # Group segments by video URL for exhibit lettering
        videos = {}
        for segment in segments:
            if segment.youtube_url not in videos:
                videos[segment.youtube_url] = []
            videos[segment.youtube_url].append(segment)
        
        # Assign exhibit letters (A, B, C, etc.)
        exhibit_map = {}
        for idx, url in enumerate(videos.keys()):
            exhibit_letter = chr(65 + idx)  # A=65 in ASCII
            exhibit_map[url] = exhibit_letter
        
        # Generate numbered facts
        facts = []
        fact_number = 1
        
        for url, url_segments in videos.items():
            exhibit_letter = exhibit_map[url]
            
            for segment in url_segments:
                # Use edited transcript if available, otherwise raw
                transcript = segment.edited_transcript or segment.raw_transcript
                
                if not transcript:
                    continue
                
                # Split transcript into sentences/statements
                statements = EvidenceToFactsService._parse_statements(transcript)
                
                for statement in statements:
                    # Format as legal fact with exhibit reference
                    fact = (
                        f"{fact_number}. {statement} "
                        f"(Video Evidence, Exhibit {exhibit_letter}, "
                        f"{segment.start_time}-{segment.end_time})."
                    )
                    facts.append(fact)
                    fact_number += 1
        
        # Combine into formatted section
        content = "\n\n".join(facts)
        
        # Generate exhibits list
        exhibits_list = EvidenceToFactsService._generate_exhibits_list(videos, exhibit_map)
        
        return {
            'content': content,
            'exhibits_list': exhibits_list,
            'metadata': {
                'segment_count': segments.count(),
                'fact_count': len(facts),
                'exhibit_count': len(videos)
            }
        }
    
    @staticmethod
    def _parse_statements(transcript):
        """
        Parse transcript into individual factual statements.
        Handles speaker attribution format: "Officer Smith: text"
        """
        statements = []
        
        # Split by speaker changes or sentence endings
        lines = transcript.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line has speaker attribution
            if ':' in line:
                # Format: "Speaker: statement"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    statement = parts[1].strip()
                    
                    # Convert to third person factual statement
                    if speaker.lower().startswith('officer') or speaker.lower().startswith('deputy'):
                        factual = f"{speaker} stated: \"{statement}\""
                    elif speaker.lower() in ['plaintiff', 'i', 'me']:
                        factual = f"Plaintiff stated: \"{statement}\""
                    else:
                        factual = f"{speaker} stated: \"{statement}\""
                    
                    statements.append(factual)
            else:
                # No speaker attribution, treat as narrative
                # Split into sentences
                sentences = line.replace('? ', '?|').replace('. ', '.|').replace('! ', '!|').split('|')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 10:  # Ignore very short fragments
                        statements.append(sentence)
        
        return statements
    
    @staticmethod
    def _generate_exhibits_list(videos, exhibit_map):
        """Generate formatted exhibits list for complaint."""
        exhibits = []
        
        for url, segments in videos.items():
            letter = exhibit_map[url]
            
            # Collect all timestamps for this video
            timestamps = [f"{s.start_time}-{s.end_time}" for s in segments]
            
            # Get violation tags from segments
            all_tags = set()
            for segment in segments:
                if segment.violation_tags:
                    tags = segment.violation_tags.split(',')
                    all_tags.update(tags)
            
            violations = ', '.join(sorted(all_tags)) if all_tags else 'Constitutional violations'
            
            exhibit_text = (
                f"EXHIBIT {letter}: Video Evidence\n"
                f"URL: {url}\n"
                f"Relevant Timestamps: {', '.join(timestamps)}\n"
                f"Description: Video documentation of {violations}"
            )
            exhibits.append(exhibit_text)
        
        return "\n\n".join(exhibits)