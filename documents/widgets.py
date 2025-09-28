# documents/widgets.py
"""
Custom form widgets for court lookup functionality
"""

from django import forms
from django.forms.widgets import Widget
from django.template import Context, Template
from django.utils.safestring import mark_safe
import json


class CourtLookupWidget(Widget):
    """
    Custom widget that displays court lookup results and allows manual override
    """
    template_name = 'documents/widgets/court_lookup_widget.html'
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'court-lookup-widget',
            'data-widget': 'court-lookup'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        """Format the value for display"""
        if value is None:
            return ''
        return value

    def render(self, name, value, attrs=None, renderer=None):
        """Render the court lookup widget"""
        context = {
            'widget': {
                'name': name,
                'value': self.format_value(value),
                'attrs': self.build_attrs(self.attrs, attrs),
            }
        }
        
        # Create the HTML template
        template_str = '''
        <div class="court-lookup-container" data-widget="court-lookup">
            <!-- Hidden field to store the actual court value -->
            <input type="hidden" name="{{ widget.name }}" value="{{ widget.value }}" id="id_{{ widget.name }}">
            
            <!-- Court suggestion display -->
            <div class="court-suggestion-display" id="court-suggestion-{{ widget.name }}">
                <div class="alert alert-info" id="court-info-box" style="display: none;">
                    <h6><i class="fas fa-gavel"></i> Suggested Federal Court:</h6>
                    <div id="suggested-court-text"></div>
                    <small class="text-muted">
                        <span id="confidence-text"></span>
                        <span id="confidence-description"></span>
                    </small>
                </div>
                
                <div class="alert alert-warning" id="court-warning-box" style="display: none;">
                    <h6><i class="fas fa-exclamation-triangle"></i> Court Lookup Issue:</h6>
                    <div id="court-warning-text"></div>
                </div>
            </div>
            
            <!-- Manual override section -->
            <div class="court-manual-override mt-3">
                <div class="form-check">
                    <input type="checkbox" class="form-check-input" id="use-manual-court-{{ widget.name }}">
                    <label class="form-check-label" for="use-manual-court-{{ widget.name }}">
                        Use custom court information instead
                    </label>
                </div>
                
                <div class="manual-court-input mt-2" id="manual-court-section-{{ widget.name }}" style="display: none;">
                    <label for="manual-court-{{ widget.name }}" class="form-label">Custom Court Information:</label>
                    <textarea 
                        class="form-control" 
                        id="manual-court-{{ widget.name }}"
                        rows="3"
                        placeholder="Enter the correct federal district court information. Example:&#10;UNITED STATES DISTRICT COURT&#10;WESTERN DISTRICT OF PENNSYLVANIA&#10;PITTSBURGH DIVISION"
                    ></textarea>
                    <small class="form-text text-muted">
                        Format: "UNITED STATES DISTRICT COURT" followed by district name and division
                    </small>
                </div>
            </div>
            
            <!-- Action buttons -->
            <div class="court-actions mt-3">
                <button type="button" class="btn btn-outline-primary btn-sm" id="lookup-court-btn-{{ widget.name }}">
                    <i class="fas fa-search"></i> Look Up Court
                </button>
                <button type="button" class="btn btn-outline-success btn-sm" id="confirm-court-btn-{{ widget.name }}" style="display: none;">
                    <i class="fas fa-check"></i> Confirm This Court
                </button>
            </div>
        </div>
        '''
        
        template = Template(template_str)
        return mark_safe(template.render(Context(context)))

    class Media:
        css = {
            'all': ('css/court_lookup_widget.css',)
        }
        js = ('js/court_lookup_widget.js',)


class StateSelectWidget(forms.Select):
    """Enhanced state selection widget with court lookup integration"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-select',
            'data-trigger': 'court-lookup'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class CityInputWidget(forms.TextInput):
    """Enhanced city input widget with court lookup integration"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'data-trigger': 'court-lookup',
            'placeholder': 'City where incident occurred'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)