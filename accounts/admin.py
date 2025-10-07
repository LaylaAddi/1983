# accounts/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'full_legal_name',
        'api_usage_display',
        'api_cost_limit',
        'usage_bar',
        'status_badge',
        'api_limit_reached_at'
    ]
    
    list_filter = ['created_at', 'api_limit_reached_at']
    search_fields = ['user__username', 'user__email', 'full_legal_name']
    
    readonly_fields = ['created_at', 'updated_at', 'usage_percentage']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Legal Information', {
            'fields': ('full_legal_name', 'street_address', 'city', 'state', 'zip_code', 'phone_number')
        }),
        ('Additional Information', {
            'fields': ('date_of_birth', 'occupation'),
            'classes': ('collapse',)
        }),
        ('API Usage Tracking', {
            'fields': ('total_api_cost', 'api_cost_limit', 'usage_percentage', 'api_limit_reached_at'),
            'description': 'Track and manage user API spending'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['reset_api_usage', 'increase_limit_to_5']
    
    def api_usage_display(self, obj):
        """Display API usage with color coding"""
        cost = float(obj.total_api_cost)
        percentage = obj.usage_percentage
        
        if percentage >= 100:
            color = 'red'
        elif percentage >= 80:
            color = 'orange'
        else:
            color = 'green'
        
        cost_formatted = f"${cost:.4f}"
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            cost_formatted
        )
    api_usage_display.short_description = 'API Usage'
    
    def usage_bar(self, obj):
        """Visual progress bar for usage"""
        percentage = min(obj.usage_percentage, 100)
        
        if percentage >= 100:
            color = '#dc3545'  # Red
        elif percentage >= 80:
            color = '#ffc107'  # Orange
        else:
            color = '#28a745'  # Green
        
        percentage_text = f"{percentage:.0f}%"
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 11px; line-height: 20px;">'
            '{}'
            '</div></div>',
            percentage,
            color,
            percentage_text
        )
    usage_bar.short_description = 'Usage'
    
    def status_badge(self, obj):
        """Display status badge"""
        if obj.is_over_limit:
            return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">BLOCKED</span>')
        elif obj.usage_percentage >= 80:
            return format_html('<span style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 3px; font-size: 11px;">WARNING</span>')
        else:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">ACTIVE</span>')
    status_badge.short_description = 'Status'
    
    def reset_api_usage(self, request, queryset):
        """Admin action to reset API usage to $0.00"""
        count = 0
        for profile in queryset:
            profile.reset_api_usage()
            count += 1
        
        self.message_user(
            request,
            f'Successfully reset API usage for {count} user(s).'
        )
    reset_api_usage.short_description = 'Reset API usage to $0.00'
    
    def increase_limit_to_5(self, request, queryset):
        """Admin action to increase limit to $5.00"""
        count = queryset.update(api_cost_limit=5.00)
        
        self.message_user(
            request,
            f'Successfully increased API limit to $5.00 for {count} user(s).'
        )
    increase_limit_to_5.short_description = 'Increase limit to $5.00'