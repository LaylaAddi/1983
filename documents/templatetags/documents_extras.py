from django import template
from django.template import Template, Context

register = template.Library()

@register.filter
def render_template(content, document):
    """Render Django template variables within section content"""
    
    # Prepare context data for template rendering
    user_profile = getattr(document.user, 'userprofile', None)
    
    # Generate video exhibit references
    video_exhibits = []
    exhibit_letters = ['A', 'B', 'C', 'D']
    exhibit_counter = 0
    
    if document.youtube_url_1:
        video_exhibits.append(f"Exhibit {exhibit_letters[exhibit_counter]} (video evidence)")
        exhibit_counter += 1
    if document.youtube_url_2:
        video_exhibits.append(f"Exhibit {exhibit_letters[exhibit_counter]} (additional video)")
        exhibit_counter += 1
    if document.youtube_url_3:
        video_exhibits.append(f"Exhibit {exhibit_letters[exhibit_counter]} (additional video)")
        exhibit_counter += 1
    if document.youtube_url_4:
        video_exhibits.append(f"Exhibit {exhibit_letters[exhibit_counter]} (additional video)")
        exhibit_counter += 1
    
    # Create exhibit reference text
    if len(video_exhibits) == 1:
        video_reference = video_exhibits[0]
    elif len(video_exhibits) == 2:
        video_reference = f"{video_exhibits[0]} and {video_exhibits[1]}"
    elif len(video_exhibits) > 2:
        video_reference = ", ".join(video_exhibits[:-1]) + f", and {video_exhibits[-1]}"
    else:
        video_reference = ""
    
    context_data = {
        'plaintiff_name': user_profile.full_legal_name if user_profile else document.user.get_full_name(),
        'incident_date': document.incident_date.strftime('%B %d, %Y') if document.incident_date else '[DATE OF INCIDENT]',
        'incident_location': document.incident_location or '[LOCATION]',
        'defendants': document.defendants or '[DEFENDANTS TO BE IDENTIFIED]',
        'description': document.description,
        'video_exhibits': video_reference,
        'has_video_evidence': bool(video_exhibits),
    }
    
    # Render the content as a Django template
    try:
        template_obj = Template(content)
        context = Context(context_data)
        return template_obj.render(context)
    except Exception:
        # If template rendering fails, return original content
        return content