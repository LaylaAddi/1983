# documents/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import PurchasedDocument, Person, TranscriptQuote, VideoEvidence


@admin.register(PurchasedDocument)
class PurchasedDocumentAdmin(admin.ModelAdmin):
    list_display = ['user', 'document', 'amount_paid_display', 'discount_used', 'purchased_at']
    list_filter = ['purchased_at']
    search_fields = ['user__username', 'user__email', 'document__title']
    readonly_fields = ['purchased_at', 'stripe_payment_intent_id']
    
    fieldsets = (
        ('Purchase Info', {
            'fields': ('user', 'document', 'purchased_at')
        }),
        ('Payment Details', {
            'fields': ('amount_paid', 'discount_code_used', 'discount_amount', 'stripe_payment_intent_id')
        }),
    )
    
    def amount_paid_display(self, obj):
        """Display amount paid"""
        return format_html(
            '<strong>${}</strong>',
            f'{float(obj.amount_paid):.2f}'
        )
    amount_paid_display.short_description = 'Amount Paid'
    
    def discount_used(self, obj):
        """Display if discount was used"""
        if obj.discount_code_used:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
                obj.discount_code_used
            )
        return '-'
    discount_used.short_description = 'Discount Code'


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'title', 'document', 'color_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['name', 'title', 'document__title']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('document', 'name', 'role')
        }),
        ('Details', {
            'fields': ('title', 'badge_number', 'notes')
        }),
        ('Display Settings', {
            'fields': ('color_code',)
        }),
    )

    def color_preview(self, obj):
        """Show color preview"""
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color_code
        )
    color_preview.short_description = 'Color'


@admin.register(TranscriptQuote)
class TranscriptQuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_preview', 'speaker', 'video_segment', 'significance', 'include_in_document', 'created_at']
    list_filter = ['include_in_document', 'speaker__role', 'created_at']
    search_fields = ['text', 'speaker__name', 'significance']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Quote Information', {
            'fields': ('video_evidence', 'text', 'speaker')
        }),
        ('Position & Timing', {
            'fields': ('start_position', 'end_position', 'approximate_timestamp')
        }),
        ('Categorization', {
            'fields': ('significance', 'violation_tags', 'notes')
        }),
        ('Organization', {
            'fields': ('sort_order', 'include_in_document')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def quote_preview(self, obj):
        """Show quote preview"""
        preview = obj.text[:60] + "..." if len(obj.text) > 60 else obj.text
        return format_html('<em>"{}"</em>', preview)
    quote_preview.short_description = 'Quote'

    def video_segment(self, obj):
        """Show video segment info"""
        return f"{obj.video_evidence.start_time}-{obj.video_evidence.end_time}"
    video_segment.short_description = 'Segment'


@admin.register(VideoEvidence)
class VideoEvidenceAdmin(admin.ModelAdmin):
    list_display = ['document', 'youtube_url_short', 'time_range', 'is_reviewed', 'include_in_complaint', 'quotes_count']
    list_filter = ['is_reviewed', 'include_in_complaint', 'manually_entered', 'created_at']
    search_fields = ['youtube_url', 'video_title', 'edited_transcript']
    readonly_fields = ['created_at', 'updated_at', 'extraction_cost']

    fieldsets = (
        ('Video Information', {
            'fields': ('document', 'youtube_url', 'video_title')
        }),
        ('Timestamp Segment', {
            'fields': ('start_time', 'end_time', 'start_seconds', 'end_seconds')
        }),
        ('Transcripts', {
            'fields': ('raw_transcript', 'edited_transcript', 'manually_entered')
        }),
        ('Categorization', {
            'fields': ('violation_tags', 'notes')
        }),
        ('Status', {
            'fields': ('is_reviewed', 'include_in_complaint')
        }),
        ('Metadata', {
            'fields': ('extraction_cost', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def youtube_url_short(self, obj):
        """Show shortened YouTube URL"""
        return obj.youtube_url[:50] + "..." if len(obj.youtube_url) > 50 else obj.youtube_url
    youtube_url_short.short_description = 'YouTube URL'

    def time_range(self, obj):
        """Show time range"""
        return f"{obj.start_time} - {obj.end_time}"
    time_range.short_description = 'Time Range'

    def quotes_count(self, obj):
        """Show number of quotes"""
        count = obj.quotes.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                count
            )
        return '0'
    quotes_count.short_description = 'Quotes'