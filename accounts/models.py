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
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pay_per_doc', 'Pay Per Document'),
        ('unlimited', 'Unlimited'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    
    # Stripe integration
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Payment tracking
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # API Credit tracking
    api_credit_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.50)
    last_credit_refill = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_plan_type_display()}"
    
    @property
    def is_unlimited(self):
        return self.plan_type == 'unlimited' and self.is_active
    
    @property
    def monthly_credit_amount(self):
        """How much credit user gets per month"""
        if self.plan_type == 'unlimited':
            return 10.00
        return 0.00
    
    def refill_monthly_credit(self):
        """Refill credit for unlimited users"""
        if self.plan_type == 'unlimited' and self.is_active:
            self.api_credit_balance += Decimal(str(self.monthly_credit_amount))
            self.last_credit_refill = timezone.now()
            self.save()
    
    def deduct_api_cost(self, cost):
        """Deduct cost from credit balance"""
        if isinstance(cost, float):
            cost = Decimal(str(cost))
        
        if self.api_credit_balance >= cost:
            self.api_credit_balance -= cost
            self.save()
            return True
        return False
    
    def has_sufficient_credit(self, estimated_cost):
        """Check if user has enough credit"""
        if isinstance(estimated_cost, float):
            estimated_cost = Decimal(str(estimated_cost))
        return self.api_credit_balance >= estimated_cost


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('pay_per_doc', 'Pay Per Document'),
        ('unlimited', 'Unlimited Plan'),
        ('api_credit', 'API Credit Top-Up'),
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