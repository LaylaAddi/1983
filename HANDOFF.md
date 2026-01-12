# 1983 Lawsuit Generator - Comprehensive Handoff Document

## Project Overview

**Project Name:** Section 1983 Civil Rights Lawsuit Generator
**Tech Stack:** Django 4.2 / PostgreSQL / Redis / Celery / OpenAI GPT-4o / Stripe
**Deployment:** Render (Docker) with nginx/gunicorn
**Repository:** https://github.com/LaylaAddi/1983-law

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  Django Templates + Bootstrap + JavaScript                       │
│  PWA Support (installable mobile app)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      DJANGO APPS                                 │
├──────────────┬──────────────────┬───────────────────────────────┤
│    core/     │    accounts/     │         documents/            │
│  Landing     │  Auth, Payments  │  Core Business Logic          │
│  pages       │  Subscriptions   │  AI Enhancement               │
│  PWA setup   │  Referrals       │  Video Evidence               │
└──────────────┴──────────────────┴───────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICES LAYER                               │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ AI Enhancement  │ Whisper         │ Document Orchestrator       │
│ (GPT-4o)        │ Transcription   │ Template Matching           │
│                 │ (YouTube)       │ Violation Analysis          │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  OpenAI API     │  Stripe         │  YouTube/Whisper API        │
│  (GPT-4o)       │  (Payments)     │  (Transcription)            │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

---

## Pricing Model (2-Tier + Add-On)

### Basic Plan (Free)
- **Cost:** $0
- **AI Generations:** 2 per document
- **Video Extraction:** 5 minutes per document
- **Features:** Preview only, no PDF download

### Standard Plan
- **Cost:** $197 (or $129 promotional)
- **Model:** Pay-per-document (not subscription)
- **AI Generations:** 10 per document
- **Video Extraction:** 30 minutes per document
- **Features:** Full PDF download

### Add-On Bundle
- **Cost:** $29 per bundle
- **Adds:** +20 AI generations AND +15 min video extraction
- **Stackable:** Can purchase multiple bundles per document

---

## Django Apps

### 1. Core App (`/core/`)
Landing pages, PWA installation, educational content.

**Key Views:**
- `home` - Landing page
- `know_your_rights` - Educational content
- `pwa_demo`, `install` - PWA installation

### 2. Accounts App (`/accounts/`)
User authentication, payments, subscriptions, referrals.

**Key Files:**
- `views.py` - Registration, login, profile, dashboard
- `stripe_views.py` - Checkout, webhooks, payment processing
- `referral_views.py` - Referral codes, earnings, payouts
- `models.py` - UserProfile, Subscription, Payment, DiscountCode, Payout

**Models:**
| Model | Purpose |
|-------|---------|
| `UserProfile` | Legal contact info, API cost tracking |
| `Subscription` | Plan type, Stripe customer ID, referral balance |
| `Payment` | Transaction records |
| `DiscountCode` | Referral discount codes |
| `ReferralReward` | Commission tracking |
| `Payout` | Cash withdrawal requests |
| `PromoSettings` | Promotional pricing (singleton) |
| `ReferralSettings` | Referral program config (singleton) |

### 3. Documents App (`/documents/`)
Core business logic - document creation, AI enhancement, video evidence.

**Key Files:**
- `views_main.py` - Document CRUD
- `views/evidence_views.py` - Video extraction, speaker attribution
- `views/section_views.py` - Section editing
- `views/whisper_views.py` - Transcript extraction
- `services/` - Business logic layer

**Models:**
| Model | Purpose |
|-------|---------|
| `LawsuitDocument` | Main document entity with usage tracking |
| `DocumentSection` | Sections (Introduction, Facts, Claims, etc.) |
| `LegalTemplate` | Boilerplate templates by violation type |
| `VideoEvidence` | Video segments with transcripts |
| `Person` | Speaker attribution (officers, witnesses) |
| `TranscriptQuote` | Highlighted quotes with attribution |
| `PurchasedDocument` | Pay-per-document purchase records |
| `DocumentAddon` | Add-on bundle purchases |

---

## Services Layer (`/documents/services/`)

### AI Enhancement Service (`ai_enhancement_service.py`)
Enhances legal sections using GPT-4o with budget controls.

**Enabled Sections:**
- `facts` - Description to legal facts (~$0.025/call)
- `introduction` - Case overview (~$0.015/call)
- `claims` - Legal claims (~$0.025/call)
- `parties` - Party identification (~$0.012/call)

**Disabled Sections (boilerplate only):**
- `jurisdiction`, `prayer`, `jury_demand`

**Key Methods:**
```python
check_user_budget(user)  # Validate budget before enhancement
enhance_section(template, document, context_data, timeout=10)  # Main enhancement
```

### Document Orchestrator Service (`document_orchestrator_service.py`)
Coordinates all services for complete document auto-population.

```python
auto_populate_document(document, use_ai=True)  # Main orchestrator
# Returns: sections created, AI stats, warnings, upgrade prompts
```

### Whisper Transcript Service (`whisper_transcript_service.py`)
Extracts audio transcripts from YouTube videos.

**Extraction Methods (priority order):**
1. YouTube captions (free)
2. Whisper API (reliable, ~$0.006-0.02 per 3 min)
3. yt-dlp (fallback)

**Key Methods:**
```python
extract_video_id(url)  # Parse YouTube URL
get_youtube_transcript(video_id, start, end)  # Try captions first
get_whisper_transcript(video_id, start, end)  # Whisper API fallback
```

### Violation Analysis Service (`violation_analysis_service.py`)
Determines violation type from incident description.

**Violation Types:**
- `interference_recording` - Blocking recording
- `forced_to_leave_public` - Removal from public space
- `retaliation_protected_speech` - First Amendment retaliation
- `threatened_arrest_public` - Unlawful arrest threats

**Forum Types:**
- `traditional_public_forum` - Parks, sidewalks, streets
- `designated_public_forum` - City hall, courthouses
- `limited_public_forum` - Lobbies, waiting areas

### Court Lookup Service (`court_lookup_service.py`)
Maps incident location to federal district court.

**Coverage:** All 50 states + DC
**Multi-District States:** NY, CA, TX, FL, PA, IL, OH, GA, MI (city-based routing)

---

## Key Workflows

### 1. Document Auto-Population

```
User clicks "Auto-Populate"
        │
        ▼
Violation Analysis Service
(Analyze description for violation type)
        │
        ▼
Location Analysis
(Determine forum type from location)
        │
        ▼
Template Matching Service
(Find templates for violation + location)
        │
        ▼
For each section:
├── Try AI Enhancement (if budget available)
│   └── GPT-4o with legal prompts
├── Fallback: Template Rendering
│   └── Django template substitution
└── Fallback: Default Content
        │
        ▼
Return results with stats
```

### 2. Video Evidence Extraction

```
User enters YouTube URL + timestamps
        │
        ▼
Check extraction_minutes_remaining
        │
        ▼
Extract transcript (YouTube captions → Whisper API)
        │
        ▼
Store in VideoEvidence model
        │
        ▼
Increment extraction_minutes_used
        │
        ▼
User edits transcript, adds speaker attribution
        │
        ▼
Generate Statement of Facts from tagged quotes
```

### 3. Payment Flow

```
User clicks "Get Started" on pricing page
        │
        ▼
Validate discount code (if provided)
        │
        ▼
Create Stripe Checkout Session
        │
        ▼
Stripe hosted checkout
        │
        ▼
Webhook: payment_intent.succeeded
        │
        ▼
Create Payment record
Update document (purchased_at, stripe_payment_intent_id)
Grant Standard plan limits
        │
        ▼
Redirect to document editor
```

---

## URL Structure

### Accounts URLs (`/accounts/`)
```
/register/              - User registration
/login/                 - Login
/logout/                - Logout
/dashboard/             - User dashboard
/profile/               - Profile editing
/pricing/               - Pricing page
/create-checkout-session/ - Stripe checkout
/payment-success/       - Payment confirmation
/stripe-webhook/        - Stripe webhook
/referrals/             - Referral dashboard
/validate-discount-code/ - AJAX discount validation
```

### Documents URLs (`/documents/`)
```
/create/                - Create document
/list/                  - List documents
/<pk>/                  - View document
/<pk>/edit/             - Edit document
/<pk>/sections/         - Manage sections
/<pk>/preview/          - Preview document
/<pk>/download-pdf/     - Download PDF
/<pk>/generate-defaults/ - Auto-populate sections
/<pk>/evidence/         - Evidence manager
/<pk>/evidence/extract/ - Extract video transcript
/<pk>/people/           - Manage speakers
/<pk>/evidence/<id>/quotes/ - Manage quotes
```

---

## Usage Limits Enforcement

### AI Generations
```python
# Before AI call
if document.ai_generations_remaining < 1:
    return {"error": "limit_exceeded", "upgrade_prompt": "..."}

# After successful call
document.ai_generations_used += 1
document.save()
```

### Video Extraction
```python
# Before extraction
duration_minutes = (end_seconds - start_seconds) / 60
if document.extraction_minutes_remaining < duration_minutes:
    return {"error": "insufficient_minutes", ...}

# After successful extraction
document.extraction_minutes_used += duration_minutes
document.save()
```

---

## Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Email
EMAIL_HOST_USER=info@1983ls.com
EMAIL_HOST_PASSWORD=your-email-password

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# OpenAI
OPENAI_API_KEY=sk-...

# URLs
SITE_URL=https://1983ls.com
```

---

## Recent Changes (Latest First)

1. **Video extraction confirmation dialog** - Shows usage before extraction
2. **Video extraction limit enforcement** - Per-document minute tracking
3. **AI generation limit enforcement** - Per-document usage tracking
4. **Document list view fix** - Updated for new pricing model
5. **Speaker attribution** - Quote highlighting with violation tagging
6. **Statement of Facts generation** - Auto-generate from tagged quotes
7. **Promotional pricing system** - Admin-toggleable promo prices
8. **2-Tier pricing model** - Replaced 3-tier with Basic + Standard + Add-ons
9. **Referral system** - Discount codes, earnings, payouts

---

## Database Schema (Key Tables)

```
accounts_userprofile
├── user_id (FK → auth_user)
├── total_api_cost, api_cost_limit
└── full_name, address, phone, etc.

accounts_subscription
├── user_id (FK → auth_user)
├── plan_type (basic/standard)
├── referral_cash_balance
└── stripe_customer_id

documents_lawsuitdocument
├── user_id (FK → auth_user)
├── title, description, incident_date
├── incident_city, incident_state
├── ai_generations_purchased/used
├── extraction_minutes_purchased/used
└── stripe_payment_intent_id, purchased_at

documents_documentsection
├── document_id (FK)
├── section_type, title, content
├── ai_enhanced, ai_cost, ai_model
└── order

documents_videoevidence
├── document_id (FK)
├── youtube_url, start_time, end_time
├── raw_transcript, edited_transcript
└── extraction_cost

documents_person
├── document_id (FK)
├── name, role, title, badge_number
└── color_code

documents_transcriptquote
├── video_evidence_id (FK)
├── speaker_id (FK → Person)
├── text, significance, violation_tags
└── include_in_document
```

---

## Deployment

- **Platform:** Render
- **Container:** Docker
- **WSGI:** Gunicorn
- **Static Files:** WhiteNoise
- **Database:** PostgreSQL (Render managed)
- **Cache/Queue:** Redis + Celery

---

## Known Issues / TODOs

1. The error `thinking or redacted_thinking blocks cannot be modified` occurs with Claude API extended thinking - this is an API conversation handling issue, not in this codebase
2. PDF generation requires Standard plan purchase
3. Whisper API has 3-minute max per call (cost control)
4. Multi-district court lookup may need manual confirmation for edge cases

---

## Contact & Support

- **Support Email:** info@1983ls.com
- **Repository:** https://github.com/LaylaAddi/1983-law
