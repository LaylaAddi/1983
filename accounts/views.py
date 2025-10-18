# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import UserProfile
from .forms import UserProfileForm, EmailUserCreationForm
from .forms import CustomPasswordChangeForm
import json
from accounts.models import Subscription  
from decimal import Decimal 
from accounts.models import Payment


@login_required
def password_change_view(request):
    """Allow logged-in users to change their password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Update session to prevent logout after password change
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password_change_done')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
def password_change_done_view(request):
    """Success page after password change"""
    return render(request, 'accounts/password_change_done.html')



def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create free subscription with starting credit
            Subscription.objects.get_or_create(
                user=user,
                defaults={
                    'plan_type': 'free',
                    'api_credit_balance': Decimal('0.50'),
                    'is_active': True
                }
            )
            
            messages.success(request, f'Account created successfully! Welcome, {user.first_name or user.email}!')
            
            # Log the user in after registration
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmailUserCreationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/register.html', context)

def login_view(request):
    """User login view with email"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            # Django uses username for authentication, but we store email as username
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back!')
                
                # Redirect to next page or dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please provide both email and password.')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout view"""
    if request.user.is_authenticated:
        messages.success(request, f'Goodbye!')
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    """User dashboard - shows user's documents and profile"""
    from documents.models import LawsuitDocument
    
    # Get user's recent documents
    recent_documents = LawsuitDocument.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Get document counts
    total_documents = LawsuitDocument.objects.filter(user=request.user).count()
    draft_documents = LawsuitDocument.objects.filter(
        user=request.user, 
        status='draft'
    ).count()
    completed_documents = LawsuitDocument.objects.filter(
        user=request.user, 
        status='completed'
    ).count()
    
    context = {
        'recent_documents': recent_documents,
        'total_documents': total_documents,
        'draft_documents': draft_documents,
        'completed_documents': completed_documents,
    }
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    """User profile management with legal information"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'accounts/profile.html', context)


@require_http_methods(["POST"])
@login_required
def change_password_ajax(request):
    """AJAX endpoint for password changes"""
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        # Validate current password
        if not request.user.check_password(current_password):
            return JsonResponse({'success': False, 'error': 'Current password is incorrect.'})
        
        # Validate new password
        if new_password != confirm_password:
            return JsonResponse({'success': False, 'error': 'New passwords do not match.'})
        
        if len(new_password) < 8:
            return JsonResponse({'success': False, 'error': 'Password must be at least 8 characters long.'})
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        return JsonResponse({'success': True, 'message': 'Password updated successfully!'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred. Please try again.'})




@login_required
def manage_subscription(request):
    """Page where users can view and manage their subscription"""
    subscription = request.user.subscription
    
    # Get payment history
    payments = Payment.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-completed_at')
    
    # Handle cancellation
    if request.method == 'POST' and 'cancel_subscription' in request.POST:
        if subscription.plan_type in ['pay_per_doc', 'unlimited']:
            # Downgrade to free
            subscription.plan_type = 'free'
            subscription.save()
            messages.success(request, 'Your subscription has been cancelled. You now have a free account.')
            return redirect('manage_subscription')
        else:
            messages.info(request, 'You are already on the free plan.')
    
    context = {
        'subscription': subscription,
        'payments': payments,
    }
    
    return render(request, 'accounts/manage_subscription.html', context)