# Stripe Implementation Guide - New Pricing Model

## Overview

This guide will help you implement Stripe payments for the new simplified pricing model:

**Pricing Structure:**
- **FREE (Trial)**: 2 AI generations, 5 min video, preview only
- **STANDARD ($197 or Promo $129)**: 10 AI generations, 30 min video, PDF download
- **Add-ons ($29 each)**: +10 AI generations OR +30 minutes

---

## Step 1: Create Products in Stripe Dashboard

### 1.1 Main Document Product

1. Go to **Stripe Dashboard** → **Products** → **Add Product**

2. **Product Details:**
   ```
   Name: Section 1983 Legal Document
   Description: Complete legal document generation with AI-powered sections and video transcript extraction
   ```

3. **Create TWO Prices for this product:**

   **Regular Price:**
   ```
   Amount: $197.00
   Billing: One-time
   Price ID: (copy this - e.g., price_1ABC123...)
   ```

   **Promotional Price:**
   ```
   Amount: $129.00
   Billing: One-time
   Price ID: (copy this - e.g., price_1XYZ789...)
   ```

### 1.2 AI Generations Add-On

1. **Products** → **Add Product**

2. **Product Details:**
   ```
   Name: Additional AI Generations
   Description: 10 additional AI section generations for your document
   ```

3. **Price:**
   ```
   Amount: $29.00
   Billing: One-time
   Price ID: (copy this)
   ```

### 1.3 Video Extraction Add-On

1. **Products** → **Add Product**

2. **Product Details:**
   ```
   Name: Additional Video Extraction Time
   Description: 30 additional minutes of video transcript extraction
   ```

3. **Price:**
   ```
   Amount: $29.00
   Billing: One-time
   Price ID: (copy this)
   ```

---

## Step 2: Update Django Settings

### 2.1 Environment Variables

Add to your `.env` file:

```bash
# Stripe Keys
STRIPE_SECRET_KEY=sk_live_xxxxx  # or sk_test_xxxxx for testing
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx  # or pk_test_xxxxx

# Product Price IDs
STRIPE_DOCUMENT_REGULAR_PRICE_ID=price_1ABC123...
STRIPE_DOCUMENT_PROMO_PRICE_ID=price_1XYZ789...
STRIPE_AI_ADDON_PRICE_ID=price_1DEF456...
STRIPE_VIDEO_ADDON_PRICE_ID=price_1GHI789...

# Webhook Secret (for production)
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### 2.2 Update config/settings.py

```python
# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

# Stripe Product Price IDs
STRIPE_PRICES = {
    'document_regular': os.getenv('STRIPE_DOCUMENT_REGULAR_PRICE_ID'),
    'document_promo': os.getenv('STRIPE_DOCUMENT_PROMO_PRICE_ID'),
    'ai_generations_addon': os.getenv('STRIPE_AI_ADDON_PRICE_ID'),
    'video_extraction_addon': os.getenv('STRIPE_VIDEO_ADDON_PRICE_ID'),
}
```

---

## Step 3: Database Models (Already Done)

The `PromoSettings` model already exists in `accounts/models.py`. It includes:
- `is_active` - Toggle promo on/off
- `regular_price` - $197
- `promo_price` - $129
- `stripe_promo_price_id` - For storing Stripe price ID

You also need to add fields to `LawsuitDocument`:

```python
# Add to documents/models.py - LawsuitDocument model

# Purchased add-ons
ai_generations_purchased = models.IntegerField(default=10)  # Base 10 included
extraction_minutes_purchased = models.IntegerField(default=30)  # Base 30 min

# Usage tracking
ai_generations_used = models.IntegerField(default=0)
extraction_minutes_used = models.DecimalField(max_digits=6, decimal_places=2, default=0)

# Stripe payment tracking
stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
stripe_customer_id = models.CharField(max_length=255, blank=True)
purchased_at = models.DateTimeField(null=True, blank=True)

@property
def ai_generations_remaining(self):
    return self.ai_generations_purchased - self.ai_generations_used

@property
def extraction_minutes_remaining(self):
    return self.extraction_minutes_purchased - float(self.extraction_minutes_used)
```

---

## Step 4: Create Payment Views

### 4.1 Document Purchase View

Create `accounts/views/payment_views.py`:

```python
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from accounts.models import PromoSettings
from documents.models import LawsuitDocument

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
@require_POST
def create_document_checkout(request, document_id):
    """Create Stripe checkout session for document purchase"""

    document = get_object_or_404(LawsuitDocument, id=document_id, user=request.user)

    # Check if already purchased
    if document.stripe_payment_intent_id:
        return JsonResponse({'error': 'Document already purchased'}, status=400)

    # Get current pricing
    promo = PromoSettings.get_settings()

    # Determine which price to use
    if promo.is_active:
        price_id = settings.STRIPE_PRICES['document_promo']
        amount = int(promo.promo_price * 100)  # Convert to cents
    else:
        price_id = settings.STRIPE_PRICES['document_regular']
        amount = int(promo.regular_price * 100)

    try:
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/documents/{document.id}/?payment=success'),
            cancel_url=request.build_absolute_uri(f'/documents/{document.id}/?payment=cancelled'),
            client_reference_id=str(document.id),
            customer_email=request.user.email,
            metadata={
                'document_id': document.id,
                'user_id': request.user.id,
                'purchase_type': 'document',
            }
        )

        return JsonResponse({'checkout_url': checkout_session.url})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
```

### 4.2 Add-On Purchase View

```python
@login_required
@require_POST
def create_addon_checkout(request, document_id):
    """Create checkout for add-on purchase (AI or video extraction)"""

    document = get_object_or_404(LawsuitDocument, id=document_id, user=request.user)

    # Check document is already purchased
    if not document.stripe_payment_intent_id:
        return JsonResponse({'error': 'Must purchase document first'}, status=400)

    addon_type = request.POST.get('addon_type')  # 'ai_generations' or 'video_extraction'

    if addon_type == 'ai_generations':
        price_id = settings.STRIPE_PRICES['ai_generations_addon']
    elif addon_type == 'video_extraction':
        price_id = settings.STRIPE_PRICES['video_extraction_addon']
    else:
        return JsonResponse({'error': 'Invalid addon type'}, status=400)

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/documents/{document.id}/?addon=success'),
            cancel_url=request.build_absolute_uri(f'/documents/{document.id}/?addon=cancelled'),
            client_reference_id=str(document.id),
            customer_email=request.user.email,
            metadata={
                'document_id': document.id,
                'user_id': request.user.id,
                'purchase_type': 'addon',
                'addon_type': addon_type,
            }
        )

        return JsonResponse({'checkout_url': checkout_session.url})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
```

---

## Step 5: Webhook Handler

### 5.1 Create Webhook Endpoint

Create `accounts/views/webhook_views.py`:

```python
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from documents.models import LawsuitDocument, DocumentAddon
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks for payment confirmation"""

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Handle successful payment
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_payment(session)

    return HttpResponse(status=200)


def handle_successful_payment(session):
    """Process successful payment and grant access"""

    metadata = session.get('metadata', {})
    document_id = metadata.get('document_id')
    purchase_type = metadata.get('purchase_type')

    if not document_id:
        return

    try:
        document = LawsuitDocument.objects.get(id=document_id)
    except LawsuitDocument.DoesNotExist:
        return

    if purchase_type == 'document':
        # Main document purchase
        document.stripe_payment_intent_id = session.get('payment_intent')
        document.stripe_customer_id = session.get('customer')
        document.purchased_at = timezone.now()
        document.save()

    elif purchase_type == 'addon':
        # Add-on purchase
        addon_type = metadata.get('addon_type')

        if addon_type == 'ai_generations':
            document.ai_generations_purchased += 10
        elif addon_type == 'video_extraction':
            document.extraction_minutes_purchased += 30

        document.save()

        # Record add-on purchase
        DocumentAddon.objects.create(
            document=document,
            addon_type=addon_type,
            amount=session.get('amount_total', 0) / 100,  # Convert from cents
            stripe_payment_intent_id=session.get('payment_intent')
        )
```

### 5.2 Add Webhook URL Pattern

Add to `accounts/urls.py`:

```python
from accounts.views import webhook_views, payment_views

urlpatterns = [
    # ... existing patterns ...

    # Payment endpoints
    path('checkout/document/<int:document_id>/', payment_views.create_document_checkout, name='checkout_document'),
    path('checkout/addon/<int:document_id>/', payment_views.create_addon_checkout, name='checkout_addon'),

    # Stripe webhook
    path('webhooks/stripe/', webhook_views.stripe_webhook, name='stripe_webhook'),
]
```

### 5.3 Configure Webhook in Stripe Dashboard

1. Go to **Stripe Dashboard** → **Developers** → **Webhooks**
2. Click **Add endpoint**
3. **Endpoint URL**: `https://www.1983ls.com/accounts/webhooks/stripe/`
4. **Events to send**:
   - `checkout.session.completed`
5. Copy the **Signing secret** → add to `.env` as `STRIPE_WEBHOOK_SECRET`

---

## Step 6: Frontend Integration

### 6.1 Purchase Button (Document Detail Page)

Add to `templates/documents/detail.html`:

```html
{% if not document.stripe_payment_intent_id %}
<!-- Document not purchased - show purchase button -->
<div class="alert alert-warning">
    <h5>Purchase Required</h5>
    <p>Complete your purchase to download your legal document.</p>

    {% if promo.is_active %}
    <div class="badge bg-danger mb-2">{{ promo.promo_badge_text }}</div>
    <h4>
        <span class="text-decoration-line-through text-muted">${{ promo.regular_price }}</span>
        <strong class="text-success">${{ promo.promo_price }}</strong>
        <small>Save ${{ promo.savings_amount }}!</small>
    </h4>
    <p>{{ promo.promo_description }}</p>
    {% else %}
    <h4>${{ promo.regular_price }}</h4>
    {% endif %}

    <button onclick="purchaseDocument({{ document.id }})" class="btn btn-success btn-lg">
        <i class="fas fa-shopping-cart"></i> Purchase Document - ${{ promo.current_price }}
    </button>
</div>

<script>
function purchaseDocument(documentId) {
    fetch(`/accounts/checkout/document/${documentId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    });
}
</script>
{% endif %}
```

### 6.2 Add-On Purchase Buttons

```html
{% if document.stripe_payment_intent_id %}
<!-- Show usage and add-on options -->
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <h6>AI Generations</h6>
                <div class="progress mb-2">
                    <div class="progress-bar" style="width: {{ ai_percentage }}%">
                        {{ document.ai_generations_used }}/{{ document.ai_generations_purchased }}
                    </div>
                </div>
                {% if document.ai_generations_remaining < 3 %}
                <button onclick="purchaseAddon({{ document.id }}, 'ai_generations')" class="btn btn-sm btn-primary">
                    <i class="fas fa-plus"></i> Buy +10 Generations ($29)
                </button>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <h6>Video Extraction</h6>
                <div class="progress mb-2">
                    <div class="progress-bar" style="width: {{ video_percentage }}%">
                        {{ document.extraction_minutes_used }}/{{ document.extraction_minutes_purchased }} min
                    </div>
                </div>
                {% if document.extraction_minutes_remaining < 5 %}
                <button onclick="purchaseAddon({{ document.id }}, 'video_extraction')" class="btn btn-sm btn-primary">
                    <i class="fas fa-plus"></i> Buy +30 Minutes ($29)
                </button>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<script>
function purchaseAddon(documentId, addonType) {
    const formData = new FormData();
    formData.append('addon_type', addonType);

    fetch(`/accounts/checkout/addon/${documentId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    });
}
</script>
{% endif %}
```

---

## Step 7: Admin Interface

The `PromoSettings` admin interface is already created. Access it at:

**`/admin/accounts/promosettings/`**

You can:
- ✅ Toggle promotion ON/OFF
- ✅ Change prices ($197 regular, $129 promo)
- ✅ Edit promotion text
- ✅ Set countdown timer
- ✅ Add Stripe Price ID

---

## Step 8: Testing

### 8.1 Use Stripe Test Mode

1. Use test keys: `sk_test_...` and `pk_test_...`
2. Use test card: `4242 4242 4242 4242`
3. Any future date, any CVC

### 8.2 Test Flow

1. Create document (as free user)
2. Try to download PDF → should prompt for purchase
3. Click purchase → redirect to Stripe checkout
4. Complete payment with test card
5. Webhook fires → document.stripe_payment_intent_id set
6. User redirected back → can now download PDF

---

## Step 9: Go Live

1. Switch to live Stripe keys in production `.env`
2. Update webhook URL to production domain
3. Test one real transaction
4. Monitor Stripe Dashboard for errors

---

## Summary Checklist

- [ ] Create 3 products in Stripe (Document + 2 Add-ons)
- [ ] Create 2 prices for Document (Regular + Promo)
- [ ] Copy all Price IDs to `.env` file
- [ ] Update `config/settings.py` with Stripe config
- [ ] Run migrations for `PromoSettings` model
- [ ] Create payment views (`payment_views.py`)
- [ ] Create webhook handler (`webhook_views.py`)
- [ ] Add URL patterns for payments
- [ ] Configure webhook in Stripe Dashboard
- [ ] Update templates with purchase buttons
- [ ] Test with Stripe test mode
- [ ] Go live with production keys

---

**When you're ready to implement, let me know and I'll help you with each step!**
