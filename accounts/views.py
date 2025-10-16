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
    """User registration view with email and referral code"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Check if there's a referral code in URL (e.g., ?code=ABC123)
    url_code = request.GET.get('code', '').strip()
    
    if request.method == 'POST':
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Check if they used a referral code
            referral_code = form.cleaned_data.get('referral_code', '').strip()
            if referral_code:
                messages.success(
                    request, 
                    f'Account created successfully! Referral code "{referral_code}" will be applied to your first purchase.'
                )
            else:
                messages.success(request, f'Account created successfully! Welcome, {user.first_name or user.email}!')
            
            # Log the user in after registration
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill referral code from URL if provided
        initial_data = {}
        if url_code:
            initial_data['referral_code'] = url_code.upper()
        
        form = EmailUserCreationForm(initial=initial_data)
    
    context = {
        'form': form,
        'url_code': url_code  # Pass to template for display
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


