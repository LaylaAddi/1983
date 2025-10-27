"""
Service to convert reviewed video evidence into Statement of Facts.
Generates numbered factual statements from tagged quotes with speaker attribution.
"""
from ..models import VideoEvidence, TranscriptQuote


class EvidenceToFactsService:
    """Convert tagged video quotes into legal Statement of Facts."""

    @staticmethod
    def generate_facts_section(document):
        """
        Generate Statement of Facts from tagged quotes marked for inclusion.

        Uses the new TranscriptQuote model with speaker attribution.
        Only includes quotes where include_in_document=True.

        Returns:
            dict with 'content' (formatted facts) and 'metadata'
        """
        # Get all video segments marked for inclusion
        segments = VideoEvidence.objects.filter(
            document=document,
            include_in_complaint=True
        ).prefetch_related('quotes__speaker').order_by('youtube_url', 'start_seconds')

        if not segments.exists():
            return {
                'content': '',
                'metadata': {
                    'segment_count': 0,
                    'quote_count': 0,
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

        # Generate numbered facts from tagged quotes
        facts = []
        fact_number = 1
        total_quotes = 0

        for url, url_segments in videos.items():
            exhibit_letter = exhibit_map[url]

            for segment in url_segments:
                # Get quotes for this segment that should be included
                quotes = segment.quotes.filter(include_in_document=True).order_by('sort_order', 'start_position')

                if not quotes.exists():
                    # Fallback: if no quotes tagged, mention the segment exists
                    fact = (
                        f"{fact_number}. Video evidence from {segment.start_time} to {segment.end_time} "
                        f"documents relevant events. "
                        f"(Exhibit {exhibit_letter})."
                    )
                    facts.append(fact)
                    fact_number += 1
                    continue

                # Process each tagged quote
                for quote in quotes:
                    total_quotes += 1

                    # Build the factual statement with speaker attribution
                    speaker_name = quote.speaker.display_name
                    speaker_role = quote.speaker.get_role_display()

                    # Format the statement
                    fact_parts = []

                    # Add context/significance if provided
                    if quote.significance:
                        fact_parts.append(f"{quote.significance}.")

                    # Add the quote with attribution
                    fact_parts.append(f'{speaker_name} stated: "{quote.text}"')

                    # Combine parts
                    fact_text = ' '.join(fact_parts)

                    # Add exhibit reference
                    fact = (
                        f"{fact_number}. {fact_text} "
                        f"(Exhibit {exhibit_letter}, {segment.start_time})."
                    )

                    facts.append(fact)
                    fact_number += 1

        if not facts:
            return {
                'content': '',
                'metadata': {
                    'segment_count': segments.count(),
                    'quote_count': 0,
                    'error': 'No tagged quotes found. Please tag quotes with speaker attribution before generating.'
                }
            }

        # Combine into formatted section
        content = "\n\n".join(facts)

        # Generate exhibits list
        exhibits_list = EvidenceToFactsService._generate_exhibits_list(videos, exhibit_map)

        return {
            'content': content,
            'exhibits_list': exhibits_list,
            'metadata': {
                'segment_count': segments.count(),
                'quote_count': total_quotes,
                'fact_count': len(facts),
                'exhibit_count': len(videos)
            }
        }

    @staticmethod
    def _generate_exhibits_list(videos, exhibit_map):
        """Generate formatted exhibits list for complaint."""
        exhibits = []

        for url, segments in videos.items():
            letter = exhibit_map[url]

            # Collect all timestamps for this video
            timestamps = [f"{s.start_time}-{s.end_time}" for s in segments]

            # Get violation tags from quotes
            all_tags = set()
            for segment in segments:
                # Get violation tags from the segment's quotes
                quotes = segment.quotes.filter(include_in_document=True)
                for quote in quotes:
                    if quote.violation_tags:
                        tags = quote.violation_tags.split(',')
                        all_tags.update(t.strip() for t in tags)

                # Also check segment-level tags
                if segment.violation_tags:
                    tags = segment.violation_tags.split(',')
                    all_tags.update(t.strip() for t in tags)

            # Format violation tags for display
            if all_tags:
                violations = ', '.join(sorted(tag.replace('_', ' ').title() for tag in all_tags))
            else:
                violations = 'Constitutional violations'

            exhibit_text = (
                f"EXHIBIT {letter}: Video Evidence\n"
                f"URL: {url}\n"
                f"Relevant Timestamps: {', '.join(timestamps)}\n"
                f"Description: Video documentation of {violations}"
            )
            exhibits.append(exhibit_text)

        return "\n\n".join(exhibits)