# documents/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import PurchasedDocument


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