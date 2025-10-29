# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Legal contact information
    full_legal_name = models.CharField(max_length=200, blank=True, 
                                      help_text="Full name as it should appear in legal documents")
    street_address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Optional additional fields
    date_of_birth = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    # Referral tracking
    referred_by_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Referral code used during signup"
    )
    
    # API Usage Tracking (ADMIN ONLY - hidden from users)
    total_api_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=0.0000,
        help_text="Total API costs incurred (USD) - admin view only"
    )
    api_cost_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.50,
        help_text="Maximum allowed API spending (USD) - default $0.50 for free users"
    )
    api_limit_reached_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp when user hit their API limit"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [self.street_address, self.city, self.state, self.zip_code]
        return ", ".join(part for part in parts if part)
    
    @property
    def is_complete(self):
        """Check if profile has all required legal information"""
        required_fields = [
            self.full_legal_name, self.street_address, 
            self.city, self.state, self.zip_code, self.phone_number
        ]
        return all(field.strip() if field else False for field in required_fields)
    
    @property
    def remaining_api_budget(self):
        """Calculate remaining budget."""
        return float(self.api_cost_limit) - float(self.total_api_cost)
    
    @property
    def is_over_limit(self):
        """Check if user has exceeded their API limit."""
        return self.total_api_cost >= self.api_cost_limit
    
    @property
    def usage_percentage(self):
        """Return percentage of limit used."""
        if self.api_cost_limit == 0:
            return 100
        return (float(self.total_api_cost) / float(self.api_cost_limit)) * 100
    
    def add_api_cost(self, cost):
        """Add cost to user's total and save."""
        if isinstance(cost, float):
            cost = Decimal(str(cost))
        
        self.total_api_cost += cost
        
        if self.is_over_limit and not self.api_limit_reached_at:
            self.api_limit_reached_at = timezone.now()
        
        self.save()
    
    def reset_api_usage(self):
        """Reset API usage back to zero (admin action)."""
        self.total_api_cost = Decimal('0.0000')
        self.api_limit_reached_at = None
        self.save()

# Signal to create profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)



class Subscription(models.Model):
    """
    User subscription - tracks which plan they're on.
    In the new system:
    - 'basic' = Free trial (2 AI gen, 5 min video, preview only)
    - 'standard' = Paid ($197 or promo) - tracks usage per document
    """
    PLAN_CHOICES = [
        ('basic', 'Basic (Free Trial)'),
        ('standard', 'Standard'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')

    # Stripe integration
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

    # Payment tracking
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)

    # Referral earnings (separate from document purchases)
    referral_cash_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Referral earnings available for cash withdrawal"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_type_display()}"

    @property
    def is_standard(self):
        """Check if user has standard plan"""
        return self.plan_type == 'standard' and self.is_active

    @property
    def is_basic(self):
        """Check if user is on basic/free plan"""
        return self.plan_type == 'basic'

    def can_create_document(self):
        """
        Check if user can create a new document.
        Basic: Unlimited documents (but limited features)
        Standard: After purchasing, unlimited documents
        """
        return True  # Both can create documents, features differ

    def can_download_pdf(self, document):
        """
        Check if user can download PDF for a specific document.
        Basic: Never
        Standard: Only if document is purchased
        """
        if self.plan_type == 'basic':
            return False

        # Check if document is purchased
        return hasattr(document, 'stripe_payment_intent_id') and document.stripe_payment_intent_id


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('standard', 'Standard Plan - Document Purchase'),
        ('addon_bundle', 'Add-on Bundle - AI + Video'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    
    # Stripe
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Document reference (for pay-per-doc)
    document = models.ForeignKey('documents.LawsuitDocument', on_delete=models.SET_NULL, 
                                 null=True, blank=True, related_name='payments')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_payment_type_display()} - ${self.final_amount}"

class DiscountCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Usage limits
    max_uses = models.IntegerField(default=1, help_text="Max times this code can be used")
    times_used = models.IntegerField(default=0)
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Referral tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='created_codes',
                                   help_text="User who generated this referral code")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else '$'}"
    
    def is_valid(self):
        """Check if code is valid"""
        now = timezone.now()
        
        if not self.is_active:
            return False, "Code is no longer active"
        
        if self.times_used >= self.max_uses:
            return False, "Code has reached maximum uses"
        
        if self.valid_until and now > self.valid_until:
            return False, "Code has expired"
        
        if now < self.valid_from:
            return False, "Code is not yet valid"
        
        return True, "Valid"
    
    def calculate_discount(self, original_amount):
        """Calculate discount amount"""
        if isinstance(original_amount, (int, float)):
            original_amount = Decimal(str(original_amount))
        
        if self.discount_type == 'percentage':
            discount = original_amount * (self.discount_value / 100)
        else:
            discount = self.discount_value
        
        return min(discount, original_amount)
    
    def use_code(self):
        """Increment usage counter"""
        self.times_used += 1
        self.save()

class ReferralReward(models.Model):
    """Track referral rewards earned"""
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_rewards')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_by_reward')
    
    discount_code_used = models.ForeignKey(DiscountCode, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    
    # Reward
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=25.00)
    reward_type = models.CharField(max_length=20, default='api_credit')
    
    # Status
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username} - ${self.reward_amount}"
    

# Add this at the VERY BOTTOM of accounts/models.py
# After the ReferralReward class

class ReferralSettings(models.Model):
    """
    Global settings for the referral program.
    Only ONE row should exist in the database.
    Auto-creates with defaults on first access.
    """
    
    # Percentage-based rewards (recommended)
    pay_per_doc_reward_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=20.00,
        help_text="Percentage of Pay-Per-Doc sale to give as reward (e.g., 20.00 = 20%)"
    )
    unlimited_reward_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=20.00,
        help_text="Percentage of Unlimited sale to give as reward (e.g., 20.00 = 20%)"
    )
    
    # Alternative: Flat rate (if you want fixed amounts instead)
    use_percentage_rewards = models.BooleanField(
        default=True,
        help_text="If unchecked, uses flat rate rewards below instead of percentages"
    )
    flat_pay_per_doc_reward = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=25.00,
        help_text="Flat dollar amount for Pay-Per-Doc referrals (if not using percentage)"
    )
    flat_unlimited_reward = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=25.00,
        help_text="Flat dollar amount for Unlimited referrals (if not using percentage)"
    )
    
    # Discount settings
    default_referral_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=25.00,
        help_text="Default discount % for new referral codes (e.g., 25% off)"
    )
    
    # Promotional boost (optional - for special events)
    is_promotional_period = models.BooleanField(
        default=False,
        help_text="Enable promotional rewards (Black Friday, etc.)"
    )
    promo_pay_per_doc_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        help_text="Promotional reward % for Pay-Per-Doc"
    )
    promo_unlimited_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        help_text="Promotional reward % for Unlimited"
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='referral_settings_updates',
        help_text="Admin who last updated settings"
    )
    
    class Meta:
        verbose_name = "Referral Setting"
        verbose_name_plural = "Referral Settings"
    
    def __str__(self):
        return f"Referral Settings (Updated: {self.updated_at.strftime('%Y-%m-%d')})"
    
    def save(self, *args, **kwargs):
        """Ensure only one settings object exists (singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of settings"""
        pass
    
    @classmethod
    def get_settings(cls):
        """
        Get or create the single settings instance with defaults.
        This ensures settings always exist after database drops.
        """
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'pay_per_doc_reward_percentage': Decimal('20.00'),
                'unlimited_reward_percentage': Decimal('20.00'),
                'use_percentage_rewards': True,
                'flat_pay_per_doc_reward': Decimal('25.00'),
                'flat_unlimited_reward': Decimal('25.00'),
                'default_referral_discount_percentage': Decimal('25.00'),
                'is_promotional_period': False,
                'promo_pay_per_doc_percentage': Decimal('30.00'),
                'promo_unlimited_percentage': Decimal('30.00'),
            }
        )
        return obj
    
    def calculate_reward(self, payment_type, payment_amount):
        """
        Calculate reward amount based on current settings.
        
        Args:
            payment_type: 'pay_per_doc' or 'unlimited'
            payment_amount: Decimal amount of the sale
        
        Returns:
            Decimal reward amount
        """
        if isinstance(payment_amount, (int, float)):
            payment_amount = Decimal(str(payment_amount))
        
        # Check if using flat rates
        if not self.use_percentage_rewards:
            if payment_type == 'pay_per_doc':
                return self.flat_pay_per_doc_reward
            elif payment_type == 'unlimited':
                return self.flat_unlimited_reward
            return Decimal('25.00')
        
        # Get percentage (check promo first)
        if self.is_promotional_period:
            if payment_type == 'pay_per_doc':
                percentage = self.promo_pay_per_doc_percentage
            elif payment_type == 'unlimited':
                percentage = self.promo_unlimited_percentage
            else:
                percentage = Decimal('20.00')
        else:
            if payment_type == 'pay_per_doc':
                percentage = self.pay_per_doc_reward_percentage
            elif payment_type == 'unlimited':
                percentage = self.unlimited_reward_percentage
            else:
                percentage = Decimal('20.00')
        
        # Calculate percentage-based reward
        reward = (payment_amount * percentage) / Decimal('100')
        return reward.quantize(Decimal('0.01'))


# Signal to create Subscription when User is created (if not exists)
@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    """Ensure every user has a subscription"""
    if created:
        Subscription.objects.get_or_create(
            user=instance,
            defaults={
                'plan_type': 'free',
                'api_credit_balance': Decimal('0.50'),
            }
        )


# Add this at the very bottom of accounts/models.py
# After the ReferralSettings model

class Payout(models.Model):
    """
    Track cash payouts to users for referral earnings
    """
    PAYOUT_METHOD_CHOICES = [
        ('paypal', 'PayPal'),
        ('venmo', 'Venmo'),
        ('zelle', 'Zelle'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('api_credit', 'Convert to API Credit'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payout details
    method = models.CharField(max_length=20, choices=PAYOUT_METHOD_CHOICES, default='paypal')
    payment_email = models.EmailField(blank=True, help_text="PayPal/Venmo email")
    payment_phone = models.CharField(max_length=20, blank=True, help_text="Zelle/phone number")
    payment_address = models.TextField(blank=True, help_text="Mailing address for checks")
    notes = models.TextField(blank=True, help_text="Additional notes or instructions")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Admin tracking
    processed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='processed_payouts',
        help_text="Admin who processed this payout"
    )
    transaction_id = models.CharField(
        max_length=255, 
        blank=True,
        help_text="PayPal transaction ID, check number, etc."
    )
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes")
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.get_status_display()})"
    
    def approve(self, admin_user=None):
        """Approve the payout request"""
        self.status = 'approved'
        self.approved_at = timezone.now()
        if admin_user:
            self.processed_by = admin_user
        self.save()
    
    def complete(self, transaction_id='', admin_user=None):
        """Mark payout as completed and deduct from user balance"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.transaction_id = transaction_id
        if admin_user:
            self.processed_by = admin_user
        
        # Deduct from user's cash balance
        subscription = Subscription.objects.get(user=self.user)
        subscription.referral_cash_balance -= self.amount
        subscription.save()
        
        self.save()
    
    def reject(self, reason='', admin_user=None):
        """Reject the payout request"""
        self.status = 'rejected'
        self.admin_notes = reason
        if admin_user:
            self.processed_by = admin_user
        self.save()


class PromoSettings(models.Model):
    """
    Global settings for promotional pricing (launch discounts, sales, etc.)
    Only ONE row should exist in the database (singleton pattern).
    Auto-creates with defaults on first access.
    """

    # Enable/disable promotional pricing
    is_active = models.BooleanField(
        default=False,
        help_text="Enable promotional pricing across the site"
    )

    # Pricing
    regular_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=197.00,
        help_text="Regular price for document ($197)"
    )
    promo_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=129.00,
        help_text="Promotional price for document ($129)"
    )

    # Promotion text/messaging (editable in admin)
    promo_badge_text = models.CharField(
        max_length=50,
        default="LAUNCH SPECIAL",
        help_text="Badge text shown on pricing (e.g., 'LAUNCH SPECIAL', 'LIMITED TIME', 'BLACK FRIDAY')"
    )
    promo_headline = models.CharField(
        max_length=200,
        default="Launch Discount - Save $68!",
        help_text="Main headline for promotion"
    )
    promo_description = models.TextField(
        default="Get our complete Section 1983 document generator at our special launch price. Limited time offer for early adopters.",
        help_text="Description text for promotion"
    )
    promo_urgency_text = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Optional urgency text (e.g., 'Offer ends December 31st', 'Only 50 spots left')"
    )

    # Display settings
    show_countdown = models.BooleanField(
        default=False,
        help_text="Show countdown timer (requires end date)"
    )
    promo_end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When promotion ends (optional - for countdown)"
    )

    # Stripe product IDs for promotional pricing
    stripe_promo_price_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="Stripe Price ID for promotional price (e.g., price_xxxxx)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promo_settings_updates',
        help_text="Admin who last updated settings"
    )

    class Meta:
        verbose_name = "Promotional Pricing Setting"
        verbose_name_plural = "Promotional Pricing Settings"

    def __str__(self):
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"Promo Settings ({status}) - ${self.promo_price}"

    def save(self, *args, **kwargs):
        """Ensure only one settings object exists (singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of settings"""
        pass

    @classmethod
    def get_settings(cls):
        """
        Get or create the single settings instance with defaults.
        This ensures settings always exist.
        """
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'is_active': False,
                'regular_price': Decimal('197.00'),
                'promo_price': Decimal('129.00'),
                'promo_badge_text': 'LAUNCH SPECIAL',
                'promo_headline': 'Launch Discount - Save $68!',
                'promo_description': 'Get our complete Section 1983 document generator at our special launch price. Limited time offer for early adopters.',
            }
        )
        return obj

    @property
    def current_price(self):
        """Return current price based on promo status"""
        return self.promo_price if self.is_active else self.regular_price

    @property
    def savings_amount(self):
        """Calculate savings if promo is active"""
        return self.regular_price - self.promo_price if self.is_active else Decimal('0.00')

    @property
    def savings_percentage(self):
        """Calculate savings percentage"""
        if self.regular_price == 0:
            return 0
        return int((self.savings_amount / self.regular_price) * 100)

    @property
    def is_ending_soon(self):
        """Check if promo ends within 24 hours"""
        if not self.promo_end_date or not self.is_active:
            return False
        time_left = self.promo_end_date - timezone.now()
        return time_left.total_seconds() <= 86400  # 24 hours

