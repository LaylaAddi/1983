# accounts\stripe_views.py
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription, Payment, DiscountCode, ReferralReward
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
import json
from .emails import EmailService

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def pricing_page(request):
    """Public pricing page"""
    referred_by_code = ''
    
    # If user is logged in, check if they have a referral code
    if request.user.is_authenticated:
        try:
            referred_by_code = request.user.profile.referred_by_code or ''
        except:
            pass
    
    context = {
        'price_per_doc': settings.PRICE_PAY_PER_DOC,
        'price_unlimited': settings.PRICE_UNLIMITED,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'referred_by_code': referred_by_code,
    }
    return render(request, 'accounts/pricing.html', context)


def validate_discount_code(request):
    """
    AJAX endpoint to validate discount codes before checkout
    Returns discount amount and validation status
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        discount_code = data.get('code', '').strip()
        plan_type = data.get('plan_type', '')
        
        if not discount_code:
            return JsonResponse({
                'valid': False,
                'message': 'Please enter a discount code'
            })
        
        # Get base price
        if plan_type == 'pay_per_doc':
            price = settings.PRICE_PAY_PER_DOC
            plan_name = 'Pay-Per-Document'
        elif plan_type == 'unlimited':
            price = settings.PRICE_UNLIMITED
            plan_name = 'Unlimited Plan'
        else:
            return JsonResponse({
                'valid': False,
                'message': 'Invalid plan type'
            })
        
        # Check if code exists
        try:
            discount_obj = DiscountCode.objects.get(code__iexact=discount_code)
        except DiscountCode.DoesNotExist:
            return JsonResponse({
                'valid': False,
                'message': f'Code "{discount_code}" not found. Please check spelling.'
            })
        
        # Validate code
        is_valid, message = discount_obj.is_valid()
        
        if not is_valid:
            return JsonResponse({
                'valid': False,
                'message': message
            })
        
        # Calculate discount
        discount_amount = float(discount_obj.calculate_discount(price))
        final_price = price - discount_amount
        
        # Get discount type for display
        if discount_obj.discount_type == 'percentage':
            discount_display = f"{discount_obj.discount_value}% off"
        else:
            discount_display = f"${discount_obj.discount_value} off"
        
        return JsonResponse({
            'valid': True,
            'message': f'✓ Code applied! {discount_display}',
            'discount_amount': discount_amount,
            'original_price': price,
            'final_price': final_price,
            'discount_display': discount_display,
            'code': discount_obj.code
        })
        
    except Exception as e:
        return JsonResponse({
            'valid': False,
            'message': f'Error validating code: {str(e)}'
        }, status=400)
    

@login_required
def create_checkout_session(request):
    """Create Stripe checkout session"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        
        plan_type = data.get('plan_type')
        document_id = data.get('document_id')
        discount_code = data.get('discount_code', '').strip()
        
        # Get base price
        if plan_type == 'pay_per_doc':
            price = settings.PRICE_PAY_PER_DOC
        elif plan_type == 'unlimited':
            price = settings.PRICE_UNLIMITED
        else:
            return JsonResponse({'error': 'Invalid plan type'}, status=400)
        
        # Apply discount code
        discount_amount = 0
        if discount_code:
            try:
                discount_obj = DiscountCode.objects.get(code__iexact=discount_code)
                is_valid, message = discount_obj.is_valid()
                if not is_valid:
                    return JsonResponse({'error': message}, status=400)
                
                discount_amount = float(discount_obj.calculate_discount(price))
                price = price - discount_amount
            except DiscountCode.DoesNotExist:
                return JsonResponse({'error': 'Invalid discount code'}, status=400)
        
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Pay Per Document' if plan_type == 'pay_per_doc' else 'Unlimited Plan',
                    },
                    'unit_amount': int(price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/accounts/payment-success/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/accounts/pricing/'),
            client_reference_id=str(request.user.id),
            metadata={
                'plan_type': plan_type,
                'document_id': document_id if document_id else '',
                'discount_code': discount_code if discount_code else '',
                'user_id': str(request.user.id),
            }
        )
        
        return JsonResponse({'sessionId': session.id})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
def payment_success(request):
    """Handle successful payment"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        messages.error(request, 'Invalid payment session')
        return redirect('pricing_page')
    
    try:
        # Retrieve session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            from decimal import Decimal
            from accounts.models import ReferralSettings
            
            plan_type = session.metadata.get('plan_type')
            document_id = session.metadata.get('document_id')
            discount_code = session.metadata.get('discount_code')
            
            # Get or create subscription
            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                defaults={'plan_type': 'free'}
            )
            
            # Track what was purchased for display
            plan_name = ''
            credit_added = 0
            next_url = 'document_list'
            
            # Update subscription based on plan type
            if plan_type == 'pay_per_doc':
                subscription.api_credit_balance += Decimal('5.00')
                subscription.save()
                credit_added = 5.00
                plan_name = 'Pay Per Document'
                
                # Create PurchasedDocument record
                if document_id:
                    from documents.models import LawsuitDocument, PurchasedDocument
                    document = LawsuitDocument.objects.get(pk=document_id)
                    PurchasedDocument.objects.get_or_create(
                        user=request.user,
                        document=document,
                        defaults={
                            'amount_paid': session.amount_total / 100,
                            'stripe_payment_intent_id': session.payment_intent,
                            'discount_code_used': discount_code if discount_code else None
                        }
                    )
                    next_url = f'/documents/{document_id}/'
                
            elif plan_type == 'unlimited':
                subscription.plan_type = 'unlimited'
                subscription.api_credit_balance += Decimal('10.00')
                subscription.stripe_customer_id = session.customer
                subscription.save()
                credit_added = 10.00
                plan_name = 'Unlimited Plan'
            
            # Calculate payment amount (Stripe gives cents, convert to dollars)
            payment_amount = Decimal(str(session.amount_total)) / Decimal('100')
            
            # Create Payment record for tracking (always create, not just for referrals)
            payment_record = Payment.objects.create(
                user=request.user,
                payment_type=plan_type,
                stripe_payment_intent_id=session.payment_intent,
                amount=payment_amount,
                discount_code=discount_code if discount_code else None,
                discount_amount=Decimal('0.00'),  # Calculate if needed
                final_amount=payment_amount,
                status='completed',
                completed_at=timezone.now()
            )
            
            # Process referral reward if discount code used
            if discount_code:
                try:
                    code_obj = DiscountCode.objects.get(code__iexact=discount_code)
                    code_obj.use_code()
                    
                    if code_obj.created_by:
                        # Get referral settings
                        settings = ReferralSettings.get_settings()
                        
                        # Calculate reward based on plan type and amount
                        reward_amount = settings.calculate_reward(plan_type, payment_amount)
                        
                        # Add reward to referrer's balance
                        referrer_sub = Subscription.objects.get(user=code_obj.created_by)
                        referrer_sub.referral_cash_balance += reward_amount
                        referrer_sub.save()
                        
                        # Create reward record (linked to payment)
                        ReferralReward.objects.create(
                            referrer=code_obj.created_by,
                            referred_user=request.user,
                            discount_code_used=code_obj,
                            payment=payment_record,  # Now links to payment created above
                            reward_amount=reward_amount,
                            reward_type='api_credit',
                            is_paid=True,
                            paid_at=timezone.now()
                        )
                        
                        # Optional: Log for debugging
                        print(f"Referral reward: {code_obj.created_by.username} earned ${reward_amount} from {request.user.username}'s ${payment_amount} {plan_type} purchase")
                        
                except DiscountCode.DoesNotExist:
                    pass
            
            # Send payment confirmation email
            EmailService.send_payment_confirmation(
                user=request.user,
                payment=payment_record,
                subscription=subscription
            )
            
            # Render success page with context
            context = {
                'plan_name': plan_name,
                'credit_added': credit_added,
                'total_credit': float(subscription.api_credit_balance),
                'is_unlimited': subscription.is_unlimited,
                'next_url': next_url,
            }
            return render(request, 'accounts/payment-success.html', context)
        
        messages.error(request, 'Payment was not completed')
        return redirect('pricing_page')
        
    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')
        return redirect('pricing_page')

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle different event types
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Payment was successful - already handled in payment_success view
        pass
    
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Log successful payment
        pass
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # Handle failed payment
        pass
    
    return JsonResponse({'status': 'success'})