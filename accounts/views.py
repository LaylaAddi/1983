# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            
            # Log the user in after registration
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next page or dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """User logout view"""
    if request.user.is_authenticated:
        messages.success(request, f'Goodbye, {request.user.username}!')
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
    """User profile management"""
    if request.method == 'POST':
        # Handle profile updates
        user = request.user
        
        # Update basic info
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
            
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'accounts/profile.html')

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