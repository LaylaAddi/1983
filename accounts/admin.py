# accounts/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import reverse
from .models import UserProfile, Subscription, Payment, DiscountCode, ReferralReward, ReferralSettings, Payout
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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_type', 'api_credit_display', 'is_active', 'started_at']
    list_filter = ['plan_type', 'is_active', 'started_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['stripe_customer_id', 'stripe_subscription_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User & Plan', {
            'fields': ('user', 'plan_type', 'is_active')
        }),
        ('Stripe Information', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id'),
            'classes': ('collapse',)
        }),
        ('API Credits', {
            'fields': ('api_credit_balance', 'last_credit_refill')
        }),
        ('Dates', {
            'fields': ('started_at', 'expires_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['refill_credits', 'upgrade_to_unlimited', 'downgrade_to_free']
    
    def api_credit_display(self, obj):
        """Display credit balance with color coding"""
        balance = float(obj.api_credit_balance)
        
        if balance <= 0:
            color = 'red'
        elif balance < 1:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">${}</span>',
            color,
            f'{balance:.2f}'
)
    api_credit_display.short_description = 'API Credit'
    
    def refill_credits(self, request, queryset):
        """Refill monthly credits for unlimited users"""
        count = 0
        for sub in queryset:
            if sub.plan_type == 'unlimited':
                sub.refill_monthly_credit()
                count += 1
        self.message_user(request, f'Refilled credits for {count} unlimited subscription(s)')
    refill_credits.short_description = 'Refill monthly credits (Unlimited only)'
    
    def upgrade_to_unlimited(self, request, queryset):
        """Upgrade users to unlimited plan"""
        from decimal import Decimal
        count = 0
        for sub in queryset:
            sub.plan_type = 'unlimited'
            sub.api_credit_balance += Decimal('10.00')
            sub.save()
            count += 1
        self.message_user(request, f'Upgraded {count} user(s) to Unlimited')
    upgrade_to_unlimited.short_description = 'Upgrade to Unlimited plan'
    
    def downgrade_to_free(self, request, queryset):
        """Downgrade users to free plan"""
        count = queryset.update(plan_type='free')
        self.message_user(request, f'Downgraded {count} user(s) to Free plan')
    downgrade_to_free.short_description = 'Downgrade to Free plan'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_type', 'final_amount_display', 'status', 'created_at']
    list_filter = ['payment_type', 'status', 'created_at']
    search_fields = ['user__username', 'user__email', 'stripe_payment_intent_id']
    readonly_fields = ['created_at', 'completed_at']
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('user', 'payment_type', 'status')
        }),
        ('Stripe', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id')
        }),
        ('Amounts', {
            'fields': ('amount', 'discount_code', 'discount_amount', 'final_amount')
        }),
        ('Document', {
            'fields': ('document',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    def final_amount_display(self, obj):
        """Display final amount"""
        return format_html(
            '<strong>${:.2f}</strong>',
            float(obj.final_amount)
        )
    final_amount_display.short_description = 'Final Amount'


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_display', 'times_used', 'max_uses', 'is_active_badge', 'created_by']
    list_filter = ['discount_type', 'is_active', 'created_at']
    search_fields = ['code', 'created_by__username']
    readonly_fields = ['times_used', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Code Details', {
            'fields': ('code', 'discount_type', 'discount_value', 'is_active')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'times_used')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Referral Tracking', {
            'fields': ('created_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def discount_display(self, obj):
        """Display discount value"""
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}%"
        else:
            return f"${obj.discount_value}"
    discount_display.short_description = 'Discount'
    
    def is_active_badge(self, obj):
        """Display active status badge"""
        is_valid, message = obj.is_valid()
        if is_valid:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">ACTIVE</span>')
        else:
            return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>', message.upper())
    is_active_badge.short_description = 'Status'


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred_user', 'reward_amount', 'is_paid_badge', 'created_at']
    list_filter = ['is_paid', 'reward_type', 'created_at']
    search_fields = ['referrer__username', 'referred_user__username']
    readonly_fields = ['created_at', 'paid_at']
    
    fieldsets = (
        ('Referral Info', {
            'fields': ('referrer', 'referred_user')
        }),
        ('Discount & Payment', {
            'fields': ('discount_code_used', 'payment')
        }),
        ('Reward', {
            'fields': ('reward_amount', 'reward_type', 'is_paid', 'paid_at')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def is_paid_badge(self, obj):
        """Display paid status badge"""
        if obj.is_paid:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">PAID</span>')
        else:
            return format_html('<span style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 3px;">PENDING</span>')
    is_paid_badge.short_description = 'Status'


# Add this at the BOTTOM of accounts/admin.py

@admin.register(ReferralSettings)
class ReferralSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for referral program settings.
    Only allows editing the single settings record.
    """
    
    fieldsets = (
        ('💰 Percentage-Based Rewards (Recommended)', {
            'fields': (
                'use_percentage_rewards',
                'pay_per_doc_reward_percentage',
                'unlimited_reward_percentage',
            ),
            'description': (
                '<strong>Current rewards at 20%:</strong><br>'
                '• Pay-Per-Doc ($149): Referrer earns ~$30<br>'
                '• Unlimited ($499): Referrer earns ~$100<br><br>'
                'Rewards scale with the sale amount (fair for everyone!)'
            )
        }),
        ('💵 Flat Rate Rewards (Alternative)', {
            'fields': (
                'flat_pay_per_doc_reward',
                'flat_unlimited_reward',
            ),
            'description': (
                'Fixed dollar amounts regardless of sale price. '
                'Only used if "Use percentage rewards" is unchecked above.'
            ),
            'classes': ('collapse',)
        }),
        ('🎟️ Discount Settings', {
            'fields': (
                'default_referral_discount_percentage',
            ),
            'description': 'Default discount % for new referral codes created by users'
        }),
        ('🎁 Promotional Period (Optional)', {
            'fields': (
                'is_promotional_period',
                'promo_pay_per_doc_percentage',
                'promo_unlimited_percentage',
            ),
            'description': (
                '<strong style="color: red;">⚠️ WARNING:</strong> '
                'Checking "is promotional period" will IMMEDIATELY increase rewards '
                'for ALL new referrals. Use for Black Friday, holidays, etc.'
            ),
            'classes': ('collapse',)
        }),
        ('📝 Metadata', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('updated_at', 'updated_by')
    
    def has_add_permission(self, request):
        """Only allow one settings object"""
        return not ReferralSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Don't allow deleting the settings"""
        return False
    
    def save_model(self, request, obj, form, change):
        """Track who updated the settings"""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def changelist_view(self, request, extra_context=None):
        """Redirect directly to the settings edit page"""
        if ReferralSettings.objects.exists():
            obj = ReferralSettings.objects.first()
            return redirect(reverse('admin:accounts_referralsettings_change', args=[obj.pk]))
        return super().changelist_view(request, extra_context)
    
    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }

# Add to the imports at the top
from accounts.models import Payout

# Add this at the bottom of the file

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    """Admin interface for managing payout requests"""
    
    list_display = [
        'id',
        'user_email',
        'amount_display',
        'method',
        'status_badge',
        'requested_at',
        'completed_at',
    ]
    
    list_filter = ['status', 'method', 'requested_at']
    search_fields = ['user__email', 'user__username', 'transaction_id']
    readonly_fields = ['requested_at', 'approved_at', 'completed_at']
    
    fieldsets = (
        ('Payout Request', {
            'fields': (
                'user',
                'amount',
                'status',
                'requested_at',
            )
        }),
        ('Payment Details', {
            'fields': (
                'method',
                'payment_email',
                'payment_phone',
                'payment_address',
                'notes',
            )
        }),
        ('Processing', {
            'fields': (
                'transaction_id',
                'processed_by',
                'approved_at',
                'completed_at',
                'admin_notes',
            )
        }),
    )
    
    actions = ['approve_payouts', 'mark_as_completed', 'reject_payouts']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def amount_display(self, obj):
        return format_html('<strong>${}</strong>', obj.amount)
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'approved': 'info',
            'processing': 'primary',
            'completed': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            f'var(--bs-{color})' if color in ['primary', 'success', 'danger', 'warning', 'info'] else '#6c757d',
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_payouts(self, request, queryset):
        """Approve selected payout requests"""
        count = 0
        for payout in queryset.filter(status='pending'):
            payout.approve(admin_user=request.user)
            count += 1
        
        self.message_user(request, f'{count} payout(s) approved.')
    approve_payouts.short_description = 'Approve selected payouts'
    
    def mark_as_completed(self, request, queryset):
        """Mark payouts as completed (deducts from user balance)"""
        count = 0
        for payout in queryset.filter(status__in=['pending', 'approved', 'processing']):
            try:
                payout.complete(admin_user=request.user)
                count += 1
            except Exception as e:
                self.message_user(request, f'Error completing payout {payout.id}: {str(e)}', level='error')
        
        self.message_user(request, f'{count} payout(s) marked as completed and deducted from user balances.')
    mark_as_completed.short_description = 'Mark as completed (deduct balance)'
    
    def reject_payouts(self, request, queryset):
        """Reject selected payout requests"""
        count = 0
        for payout in queryset.filter(status='pending'):
            payout.reject(reason='Rejected by admin', admin_user=request.user)
            count += 1
        
        self.message_user(request, f'{count} payout(s) rejected.')
    reject_payouts.short_description = 'Reject selected payouts'
    
    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'processed_by')