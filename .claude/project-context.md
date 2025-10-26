# 1983 Legal Document Generator - Project Context

## Overview
**1983ls.com** is a Django web application that helps users generate Section 1983 civil rights complaints. The app uses AI (OpenAI GPT-4o and Whisper) to enhance legal documents and extract evidence from videos, with built-in budget controls and subscription tiers.

## Tech Stack

### Core Framework
- **Django 4.2.7** - Web framework
- **PostgreSQL** - Database (via psycopg)
- **Docker + Docker Compose** - Containerization
- **Gunicorn** - WSGI server
- **WhiteNoise** - Static file serving

### API Integration
- **OpenAI GPT-4o** (via `openai==1.52.0`) - Legal document AI enhancement
- **OpenAI Whisper** - Audio/video transcription
- **Stripe 7.0.0** - Payment processing

### Additional Libraries
- **Django REST Framework 3.14.0** - API endpoints
- **django-cors-headers 4.3.1** - CORS support
- **django-weasyprint 2.3.0** - PDF generation
- **youtube-transcript-api 1.2.2** - YouTube transcript extraction
- **yt-dlp 2024.10.7** - YouTube video metadata
- **Celery 5.3.4** + **Redis 5.0.1** - Background tasks

### Frontend
- Bootstrap 5 - UI framework
- Vanilla JavaScript - Client-side interactivity
- Progressive Web App (PWA) capabilities

## Project Structure

```
1983/
├── accounts/           # User authentication, subscriptions, payments
├── config/             # Django settings and main URLs
├── core/               # Landing pages, static pages
├── documents/          # Main app - document generation logic
│   ├── services/       # Business logic services
│   ├── views/          # View handlers (split into modules)
│   ├── management/     # Django management commands
│   ├── templatetags/   # Custom template filters
│   └── utils/          # Helper utilities
├── templates/          # Django HTML templates
├── static/             # CSS, JS, images
└── .claude/            # Claude Code configuration (this file)
```

## Key Models

### accounts/models.py

**UserProfile** - Extended user information
- `full_legal_name`, `street_address`, `city`, `state`, `zip_code`, `phone_number` - Legal contact info
- `total_api_cost` - Cumulative API spending (tracks across all time)
- `api_cost_limit` - Maximum allowed spending (default $0.50 for free users)
- `api_limit_reached_at` - Timestamp when limit hit
- Properties: `remaining_api_budget`, `is_over_limit`, `usage_percentage`

**Subscription** - User subscription tiers
- `plan_type` - Choices: 'free', 'pay_per_doc', 'unlimited'
- `stripe_customer_id`, `stripe_subscription_id` - Stripe integration
- `api_credit_balance` - Current API credit (unlimited plan: $10/month, free: $0.50 one-time)
- `referral_cash_balance` - Referral earnings for cash withdrawal
- Methods: `can_create_document()`, `deduct_api_cost()`, `refill_monthly_credit()`

**Payment** - Payment tracking
- `payment_type` - 'pay_per_doc', 'unlimited', 'api_credit'
- `stripe_payment_intent_id`, `amount`, `final_amount`
- `status` - 'pending', 'completed', 'failed', 'refunded'

**DiscountCode** - Referral and promo codes
- `code`, `discount_type` ('percentage'/'fixed'), `discount_value`
- `max_uses`, `times_used`, `is_active`
- `created_by` - User who generated referral code

**ReferralReward** - Referral earnings tracking
- `referrer`, `referred_user`, `reward_amount` (default $25)
- `is_paid`, `paid_at`

**ReferralSettings** - Global referral configuration (singleton)
- Percentage-based rewards for pay-per-doc/unlimited
- Promotional period settings

**Payout** - Cash withdrawal requests
- `method` - 'paypal', 'venmo', 'zelle', 'check', 'bank_transfer', 'api_credit'
- `status` - 'pending', 'approved', 'processing', 'completed', 'rejected'

### documents/models.py

**LawsuitDocument** - Main document
- `user`, `title`, `description`, `status` ('draft', 'in_progress', 'completed', 'filed')
- `incident_date`, `incident_location` - Case details
- `incident_street_address`, `incident_city`, `incident_state`, `incident_zip_code` - Structured address
- `suggested_federal_district`, `user_confirmed_district`, `district_lookup_confidence` - Court lookup
- `defendants` - Names/positions
- `youtube_url_1` through `youtube_url_4` - Video evidence with timestamps/transcripts
- `pdf_file` - Generated PDF
- Properties: `total_sections`, `completed_sections`, `completion_percentage`, `is_document_complete`

**DocumentSection** - Individual document sections
- `document` (FK to LawsuitDocument)
- `section_type` - Choices: 'introduction', 'jurisdiction', 'parties', 'facts', 'claims', 'prayer', 'jury_demand', 'exhibits'
- `title`, `content`, `order`
- **AI Enhancement fields** (added recently):
  - `ai_enhanced` - Boolean flag
  - `ai_cost` - Cost in USD (DecimalField)
  - `ai_model` - Model name (e.g., 'gpt-4o')
- `REQUIRED_SECTIONS` - Class attribute listing mandatory sections
- Properties: `is_complete`, `completion_percentage`

**LegalTemplate** - Boilerplate templates
- `violation_type` - 'threatened_arrest_public', 'interference_recording', etc.
- `location_type` - 'traditional_public_forum', 'designated_public_forum', etc.
- `section_type` - Matches DocumentSection types
- `template_text` - Django template with {{placeholders}}

**VideoEvidence** - Video evidence segments
- `document` (FK), `youtube_url`, `video_title`
- `start_time`, `end_time`, `start_seconds`, `end_seconds`
- `raw_transcript`, `edited_transcript`, `manually_entered`
- `violation_tags`, `notes`, `extraction_cost`
- `is_reviewed`, `include_in_complaint`

**PurchasedDocument** - Pay-per-doc purchases
- `user`, `document`, `amount_paid`
- `stripe_payment_intent_id`, `discount_code_used`

## Key Services (documents/services/)

### ai_enhancement_service.py (NEW - 445 lines)
**AIEnhancementService** - Core AI enhancement logic
- `enhance_section()` - Main method: checks budget, calls GPT-4o, tracks cost
- `check_user_budget()` - Validates user has sufficient budget before API call
- Section-specific prompts for: facts, introduction, claims, parties
- Temperature: 0.2-0.3 (low for legal accuracy)
- Token limits: 300-800 per section
- Cost tracking: Updates UserProfile.total_api_cost and Subscription.api_credit_balance
- 3-layer fallback: AI → Template → Default content

**AI_ENHANCED_SECTIONS** config:
- `facts`: $0.02, 800 tokens, temp 0.3
- `introduction`: $0.015, 500 tokens, temp 0.2
- `claims`: $0.015, 500 tokens, temp 0.2
- `parties`: $0.01, 300 tokens, temp 0.25

### document_orchestrator_service.py
**DocumentOrchestrator** - Coordinates document generation
- `generate_complete_document()` - Main workflow
- Creates all 8 sections in order
- Returns AI statistics: `ai_enhanced_count`, `total_ai_cost`, `sections_with_ai`

### section_generation_service.py
**SectionGenerationService** - Creates individual sections
- `create_section_from_template()` - Enhanced with AI integration (use_ai flag)
- Attempts AI enhancement first, falls back to template rendering
- Returns section + AI metadata (`ai_enhanced`, `ai_cost`, `method`)

### template_matching_service.py
**TemplateMatchingService** - Template selection and rendering
- `find_best_template()` - Matches violation/location to template
- `render_template_content()` - Replaces {{placeholders}} with context data
- Context: `plaintiff_name`, `incident_date`, `incident_location`, `defendants`, `description`, `youtube_urls`, `transcripts`

### whisper_transcript_service.py
**WhisperTranscriptService** - Video transcription
- `extract_transcript()` - Extracts audio and transcribes with Whisper
- Uses yt-dlp for audio download
- Costs ~$0.006 per minute of audio
- Budget checking before API call

### court_lookup_service.py
**CourtLookupService** - Federal district court lookup
- Geocodes address and matches to federal court districts
- Returns district name and confidence level
- Used for jurisdiction section

### violation_analysis_service.py
**ViolationAnalysisService** - Categorizes civil rights violations
- Analyzes description to determine violation type
- Maps to template categories

### evidence_to_facts_service.py
**EvidenceToFactsService** - Transforms video evidence to legal narrative
- Combines multiple VideoEvidence segments into cohesive facts section
- Uses GPT-4o with legal writing guidelines

## User Workflows

### 1. Document Creation Flow
1. **Create Document** (`/documents/create/`)
   - User enters title, description, incident details
   - Court district auto-populated via CourtLookupService

2. **Extract Video Evidence** (`/documents/<pk>/evidence/`)
   - User adds YouTube URLs with timestamps
   - WhisperTranscriptService extracts transcripts
   - User reviews/edits transcripts with speaker attribution

3. **Generate Sections** (`/documents/<pk>/generate-defaults/`)
   - DocumentOrchestrator creates all 8 sections
   - AIEnhancementService enhances 4 key sections (if budget allows)
   - TemplateMatchingService fills remaining sections
   - Fallback to defaults if templates not found

4. **Edit Sections** (`/documents/<pk>/sections/`)
   - User can manually edit any section content
   - Can insert additional template sections

5. **Download PDF** (`/documents/<pk>/download-pdf/`)
   - django-weasyprint generates final PDF
   - Includes all sections formatted for legal filing

### 2. Subscription & Payment Flow
1. **Free Tier** (default)
   - 1 document limit
   - $0.50 AI budget (one-time)
   - Budget tracked in UserProfile.total_api_cost

2. **Pay-Per-Doc Tier** ($149/document)
   - Must purchase document before creating next
   - Same $0.50 AI budget per document

3. **Unlimited Tier** ($59/month)
   - Unlimited documents
   - $10/month AI credit (refills monthly)
   - Credit tracked in Subscription.api_credit_balance

### 3. Referral Program Flow
1. User generates referral code (DiscountCode)
2. New user signs up with code (25% discount)
3. New user makes purchase
4. Referrer earns 20% of sale as ReferralReward
5. Earnings go to Subscription.referral_cash_balance
6. User can request Payout (cash or API credit)

## Budget Control System

### Free/Pay-Per-Doc Users
- **Limit**: UserProfile.api_cost_limit (default $0.50)
- **Tracking**: UserProfile.total_api_cost (cumulative)
- **Check**: Before each AI API call
- **Action when exceeded**: Show upgrade prompt, skip AI enhancement, use template fallback

### Unlimited Users
- **Credit**: Subscription.api_credit_balance ($10/month)
- **Refill**: Monthly via Celery task
- **Tracking**: Deducted per API call
- **Action when exhausted**: Notify user, continue with template fallback

### User-Facing Budget Displays (NEW)
**Dashboard** (`/dashboard/`)
- AI Enhancement Budget card
- Progress bar showing remaining budget
- Estimated AI-enhanced documents remaining
- Warning alerts when low/exhausted

**Subscription Page** (`/accounts/manage-subscription/`)
- Detailed AI usage statistics
- Per-section cost breakdown
- API credit balance (unlimited users)
- Cumulative spending (free/pay-per-doc users)

## Key URLs

### Accounts
- `/accounts/login/` - User login
- `/accounts/register/` - New user registration
- `/accounts/dashboard/` - User dashboard with AI budget display
- `/accounts/manage-subscription/` - Subscription management with AI stats
- `/accounts/referrals/` - Referral code generation

### Documents
- `/documents/create/` - Create new document
- `/documents/list/` - List user's documents
- `/documents/<pk>/` - Document detail view
- `/documents/<pk>/edit/` - Edit document metadata
- `/documents/<pk>/evidence/` - Manage video evidence
- `/documents/<pk>/sections/` - Edit document sections
- `/documents/<pk>/generate-defaults/` - Auto-generate all sections
- `/documents/<pk>/download-pdf/` - Download final PDF

## Environment Variables

**Required:**
- `SECRET_KEY` - Django secret key
- `DEBUG` - True/False
- `DATABASE_URL` - PostgreSQL connection string (production)
- `OPENAI_API_KEY` - OpenAI API key
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key

**Optional:**
- `ALLOWED_HOSTS` - Comma-separated list
- `REDIS_URL` - Redis connection for Celery

## Recent Major Features

### AI-Enhanced Document Generation (October 2024)
- Implemented GPT-4o integration for 4 sections
- Added AI tracking fields to DocumentSection model
- Budget controls with upgrade prompts
- User-facing budget displays on dashboard/subscription
- Cost: ~$0.06 per AI-enhanced document
- Migration: `0011_documentsection_ai_tracking.py`

### Court Lookup System
- Auto-populates federal district court from incident address
- Confidence scoring (high/medium/low)
- Manual override option

### Video Evidence Management
- YouTube video integration with timestamp segments
- Whisper transcription with cost tracking
- Speaker attribution in transcripts
- Evidence-to-facts transformation

### Referral Program
- Percentage-based rewards (20% default)
- Cash withdrawal or API credit conversion
- Admin-configurable via ReferralSettings

## Database Migrations

**Key migrations:**
- `accounts/migrations/` - User profiles, subscriptions, payments
- `documents/migrations/0011_documentsection_ai_tracking.py` - AI enhancement fields
- Signals auto-create UserProfile and Subscription on User creation

## Testing

**Test suite:** `test_ai_enhancement.py` (658 lines, 9 tests)
- Migration verification
- Budget checking (free/unlimited tiers)
- AI enhancement for all 4 sections
- Template fallback when budget exceeded
- Cost tracking accuracy
- User budget displays

**Run tests:**
```bash
docker-compose exec web python test_ai_enhancement.py
```

## Deployment

**Development:**
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

**Production:**
- Hosted on Render.com (or similar)
- PostgreSQL database
- WhiteNoise for static files
- Gunicorn WSGI server
- Environment variables in .env file

## Common Commands

**Django:**
```bash
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
python manage.py shell
python manage.py runserver
```

**Docker:**
```bash
docker-compose up -d              # Start containers
docker-compose down               # Stop containers
docker-compose restart web        # Restart web container
docker-compose exec web bash      # Access container shell
docker-compose logs -f web        # View web logs
```

**Git:**
- Main branch: `master` (not `main`)
- Feature branches: `claude/<feature-name>-<session-id>`
- Merge via Pull Requests

## Tips for Future Development

1. **Adding New Section Types:**
   - Update `DocumentSection.SECTION_TYPES`
   - Add to `REQUIRED_SECTIONS` if mandatory
   - Create template in `create_templates.py` management command
   - Add AI prompt in `AIEnhancementService.AI_ENHANCED_SECTIONS` if needed

2. **Modifying AI Behavior:**
   - Adjust prompts in `ai_enhancement_service.py`
   - Temperature: lower = more conservative (0.2-0.3 for legal)
   - Token limits: balance quality vs. cost
   - Always test budget controls

3. **Adding Payment Tiers:**
   - Update `Subscription.PLAN_CHOICES`
   - Add pricing logic in `can_create_document()`
   - Update Stripe integration in payment views
   - Add tier-specific features

4. **Performance Optimization:**
   - Use `select_related()` for ForeignKey queries
   - Use `prefetch_related()` for Many-to-Many queries
   - Cache template lookups
   - Offload heavy AI calls to Celery tasks

5. **Security Notes:**
   - Never commit API keys (use .env)
   - Validate all user inputs (especially video URLs)
   - Use Django's CSRF protection
   - Sanitize content before PDF generation

## Common Issues & Solutions

**Issue:** "AttributeError: 'DocumentSection' has no attribute 'REQUIRED_SECTIONS'"
- **Solution:** Missing class attribute, check model definition

**Issue:** AI budget not displaying on dashboard
- **Solution:** Verify context variables in `accounts/views.py` dashboard_view

**Issue:** Docker not loading latest code changes
- **Solution:** Use `docker-compose down && docker-compose up -d --build` (not just restart)

**Issue:** Date format errors in tests
- **Solution:** Use `date(2025, 3, 15)` objects, not strings like `"2025-03-15"`

## Documentation Files
- `BUDGET_CONTROLS_USER_GUIDE.md` - User-facing AI budget documentation
- `DEPLOYMENT_GUIDE.md` - Production deployment steps
- `WINDOWS_COMMANDS.md` - Windows-specific PowerShell commands
- `POWERSHELL_COMMANDS.md` - Git and Docker commands for Windows
- `FINAL_SUMMARY.md` - AI enhancement implementation summary

---

**Last Updated:** October 26, 2024
**Django Version:** 4.2.7
**Python Version:** 3.11+
**Database:** PostgreSQL 15+
