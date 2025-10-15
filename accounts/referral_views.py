"""
Referral tracking and dashboard views
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from decimal import Decimal
from accounts.models import DiscountCode, ReferralReward, Subscription, Payment


@login_required
def referral_dashboard(request):
    """
    Dashboard showing user's referral code performance and earnings
    """
    user = request.user
    
    # Get user's referral code (if they have one)
    referral_code = DiscountCode.objects.filter(
        created_by=user,
        is_active=True
    ).first()
    
    # Get all referral rewards for this user
    rewards = ReferralReward.objects.filter(
        referrer=user
    ).select_related('referred_user', 'payment', 'discount_code_used').order_by('-created_at')
    
    # Calculate totals
    total_earned = rewards.aggregate(
        total=Sum('reward_amount')
    )['total'] or Decimal('0.00')
    
    paid_rewards = rewards.filter(is_paid=True).aggregate(
        total=Sum('reward_amount')
    )['total'] or Decimal('0.00')
    
    pending_rewards = total_earned - paid_rewards
    
    # Count referrals by type
    referral_stats = rewards.values('payment__payment_type').annotate(
        count=Count('id'),
        total_earned=Sum('reward_amount')
    )
    
    # Get recent referrals (last 10)
    recent_referrals = rewards[:10]
    
    # Code usage stats
    code_stats = None
    if referral_code:
        code_stats = {
            'code': referral_code.code,
            'times_used': referral_code.times_used,
            'max_uses': referral_code.max_uses or 'Unlimited',
            'total_discount_given': Payment.objects.filter(
                discount_code=referral_code.code
            ).aggregate(total=Sum('discount_amount'))['total'] or Decimal('0.00')
        }
    
    context = {
        'referral_code': referral_code,
        'code_stats': code_stats,
        'total_earned': total_earned,
        'paid_rewards': paid_rewards,
        'pending_rewards': pending_rewards,
        'recent_referrals': recent_referrals,
        'referral_count': rewards.count(),
        'referral_stats': referral_stats,
    }
    
    return render(request, 'accounts/referral_dashboard.html', context)


@login_required
def create_referral_code(request):
    """
    Create a personalized referral code for the user
    """
    user = request.user
    
    # Check if user already has a code
    existing_code = DiscountCode.objects.filter(
        created_by=user,
        is_active=True
    ).first()
    
    if existing_code:
        messages.info(request, f'You already have an active referral code: {existing_code.code}')
        return redirect('referral_dashboard')
    
    if request.method == 'POST':
        custom_code = request.POST.get('custom_code', '').upper().strip()
        
        # Validate custom code
        if not custom_code:
            messages.error(request, 'Please enter a referral code.')
            return render(request, 'accounts/create_referral_code.html')
        
        if len(custom_code) < 4 or len(custom_code) > 20:
            messages.error(request, 'Code must be between 4 and 20 characters.')
            return render(request, 'accounts/create_referral_code.html')
        
        if not custom_code.replace('_', '').replace('-', '').isalnum():
            messages.error(request, 'Code can only contain letters, numbers, dashes, and underscores.')
            return render(request, 'accounts/create_referral_code.html')
        
        # Check if code already exists
        if DiscountCode.objects.filter(code__iexact=custom_code).exists():
            messages.error(request, f'The code "{custom_code}" is already taken. Please choose another.')
            return render(request, 'accounts/create_referral_code.html')
        
        # Get default discount percentage from settings
        from accounts.models import ReferralSettings
        settings = ReferralSettings.get_settings()
        
        # Create the code
        discount_code = DiscountCode.objects.create(
            code=custom_code,
            discount_type='percentage',
            discount_value=settings.default_referral_discount_percentage,
            created_by=user,
            is_active=True,
            max_uses=999999  
        )
        
        messages.success(request, f'Your referral code "{custom_code}" has been created!')
        return redirect('referral_dashboard')
    
    # GET request - show form with suggested codes
    suggested_codes = []
    if user.username:
        username_code = f"{user.username.upper()}25"[:18]
        suggested_codes.append(username_code)
    
    if user.first_name and user.last_name:
        name_code = f"{user.first_name.upper()}{user.last_name.upper()}"[:18]
        suggested_codes.append(name_code)
    
    if user.email:
        email_code = f"{user.email.split('@')[0].upper()}"[:18]
        suggested_codes.append(email_code)
    
    context = {
        'suggested_codes': suggested_codes[:3]
    }
    
    return render(request, 'accounts/create_referral_code.html', context)


@login_required
def toggle_referral_code(request, code_id):
    """
    Activate or deactivate a referral code
    """
    code = DiscountCode.objects.filter(id=code_id, created_by=request.user).first()
    
    if not code:
        messages.error(request, 'Referral code not found.')
        return redirect('referral_dashboard')
    
    code.is_active = not code.is_active
    code.save()
    
    status = "activated" if code.is_active else "deactivated"
    messages.success(request, f'Your referral code has been {status}.')
    
    return redirect('referral_dashboard')