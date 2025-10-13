# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import stripe_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Password Change (for logged-in users)
    path('password-change/', views.password_change_view, name='password_change'),
    path('password-change/done/', views.password_change_done_view, name='password_change_done'),
    
    # Keep your existing AJAX endpoint if needed
    path('change-password/', views.change_password_ajax, name='change_password_ajax'),
    
    # Password Reset (forgot password flow)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/reset/complete/'
         ), 
         name='password_reset_confirm'),
    
    path('reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),

    # Stripe Payment URLs
    path('pricing/', stripe_views.pricing_page, name='pricing_page'),
    path('create-checkout-session/', stripe_views.create_checkout_session, name='create_checkout_session'),
    path('payment-success/', stripe_views.payment_success, name='payment_success'),
    path('stripe-webhook/', stripe_views.stripe_webhook, name='stripe_webhook'),
]