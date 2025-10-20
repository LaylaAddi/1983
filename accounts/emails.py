# accounts/emails.py
"""
Email notification service for the Section 1983 Lawsuit Generator.
Centralizes all email sending logic with HTML and plain text templates.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails to users."""
    
    @staticmethod
    def _get_base_context():
        """Get base context variables for all emails."""
        return {
            'site_url': settings.SITE_URL,
            'site_name': settings.SITE_NAME,
            'support_email': settings.SUPPORT_EMAIL,
        }
    
    @staticmethod
    def send_email(subject, to_email, template_name, context):
        """
        Generic email sender with HTML and plain text versions.
        
        Args:
            subject: Email subject line
            to_email: Recipient email address
            template_name: Base template name (without extension)
            context: Dictionary of template variables
        """
        try:
            # Merge with base context
            full_context = {**EmailService._get_base_context(), **context}
            
            # Render HTML version
            html_content = render_to_string(
                f'accounts/emails/{template_name}.html',
                full_context
            )
            
            # Render plain text version
            text_content = render_to_string(
                f'accounts/emails/{template_name}.txt',
                full_context
            )
            
            # Create email with both versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Email sent successfully: {subject} to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @classmethod
    def send_welcome_email(cls, user):
        """Send welcome email to newly registered user."""
        context = {
            'user': user,
        }
        
        return cls.send_email(
            subject=f'Welcome to {settings.SITE_NAME}',
            to_email=user.email,
            template_name='welcome',
            context=context
        )
    
    @classmethod
    def send_payment_confirmation(cls, user, payment, subscription):
        """
        Send payment confirmation email after successful purchase.
        
        Args:
            user: User who made the payment
            payment: Payment object with transaction details
            subscription: Updated subscription object
        """
        # Determine what was purchased
        if payment.payment_type == 'pay_per_doc':
            plan_name = 'Pay-Per-Document'
            features = [
                'Download PDF for your purchased document',
                f'${payment.final_amount} one-time payment',
                '$5 API credit added to your account',
                'Unlimited edits to your document'
            ]
        elif payment.payment_type == 'unlimited':
            plan_name = 'Unlimited'
            features = [
                'Download unlimited documents as PDFs',
                f'${payment.final_amount} one-time payment',
                '$10 API credit every month (forever)',
                'Priority support'
            ]
        else:
            plan_name = 'API Credit'
            features = [
                f'${payment.final_amount} API credit added',
                'Use for video evidence extraction'
            ]
        
        context = {
            'user': user,
            'payment': payment,
            'subscription': subscription,
            'plan_name': plan_name,
            'features': features,
        }
        
        return cls.send_email(
            subject=f'Payment Confirmed - {plan_name} Plan',
            to_email=user.email,
            template_name='payment_confirmation',
            context=context
        )
    
    @classmethod
    def send_low_credit_warning(cls, user, subscription, threshold=0.50):
        """
        Send warning email when API credit balance is low.
        
        Args:
            user: User to notify
            subscription: Subscription with low balance
            threshold: Balance threshold that triggered the warning
        """
        context = {
            'user': user,
            'subscription': subscription,
            'balance': subscription.api_credit_balance,
            'threshold': Decimal(str(threshold)),
        }
        
        return cls.send_email(
            subject='Low API Credit Balance - Action Needed',
            to_email=user.email,
            template_name='low_credit_warning',
            context=context
        )
    
    @classmethod
    def send_payout_approved(cls, user, payout):
        """Send notification when payout request is approved."""
        context = {
            'user': user,
            'payout': payout,
        }
        
        return cls.send_email(
            subject='Payout Request Approved',
            to_email=user.email,
            template_name='payout_approved',
            context=context
        )
    
    @classmethod
    def send_payout_completed(cls, user, payout):
        """Send notification when payout is completed and money sent."""
        context = {
            'user': user,
            'payout': payout,
        }
        
        return cls.send_email(
            subject='Payout Completed - Money Sent',
            to_email=user.email,
            template_name='payout_completed',
            context=context
        )