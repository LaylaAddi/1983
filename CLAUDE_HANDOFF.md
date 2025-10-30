# Claude Handoff Document - Section 1983 App Pricing Redesign

**Last Updated**: 2025-10-30
**Git Branch**: `claude/fix-video-transcript-retrieval-011CUW3FJkHSmajZjFq2SCkY`
**Status**: PHASE 1 Complete (Video Extraction Limits), Ready for Testing

---

## Current Session Objective

Complete redesign of pricing system from 3-tier subscription model to simplified 2-tier + add-on bundle model with usage-based limits enforced per document.

---

## Pricing Model (NEW)

### Plans

**BASIC (Free)**
- 2 AI generations per document
- 5 minutes video extraction per document
- Preview only (no PDF download)

**STANDARD ($197 regular / $129 promo)**
- 10 AI generations per document
- 30 minutes video extraction per document
- Full PDF download
- Purchased per document (not subscription)

**ADD-ON BUNDLE ($29)**
- +20 AI generations
- +15 minutes video extraction
- Can be purchased multiple times per document

### Key Business Logic

1. **Document-scoped limits**: Each document tracks its own usage (not subscription-wide)
2. **Pay-per-document**: Users pay $197 per document (Standard plan)
3. **Promo pricing**: Admin can toggle promotional pricing ($129) via Django admin
4. **Usage enforcement**: Both AI generation and video extraction have hard limits
5. **Add-on purchases**: Users can buy bundles to increase limits on specific documents

---

## Implementation Status

### ✅ COMPLETED (PHASE 1)

#### 1.1 & 1.2: Video Extraction Backend Enforcement
- **File**: `/home/user/1983/documents/views/evidence_views.py:103-160`
- **Changes**:
  - Added limit check before extraction: `document.extraction_minutes_remaining >= duration_minutes`
  - Returns JSON error if insufficient minutes
  - Tracks usage after successful extraction: `document.extraction_minutes_used += duration_minutes`
  - Shows appropriate error message based on plan (Basic vs Standard)
- **Commit**: "PHASE 1.1 & 1.2: Add video extraction limit enforcement and tracking"

#### 1.3: Video Extraction Frontend Confirmation
- **File**: `/home/user/1983/templates/documents/evidence_manager.html:749-808`
- **Changes**:
  - JavaScript confirmation dialog before extraction
  - Shows duration, remaining minutes, and minutes after extraction
  - Pre-validation blocks if insufficient minutes
  - Updated success message to show minutes used and remaining
- **Commit**: "PHASE 1.3: Add video extraction confirmation dialog and usage display"

#### AI Generation Limits (Previously Completed)
- **File**: `/home/user/1983/documents/views_main.py:244-310`
- **Changes**:
  - Backend limit check before AI generation
  - Increments `ai_generations_used` after success
  - Shows remaining count in success message
- **File**: `/home/user/1983/templates/documents/detail.html:675-686`
- **Changes**:
  - JavaScript confirmation dialog with remaining count
  - Button text shows "(X left)"

#### Core Model Changes
- **File**: `/home/user/1983/accounts/models.py`
  - Updated `Subscription.PLAN_CHOICES` from 3 tiers to 2: `('basic', 'standard')`
  - Removed fields: `api_credit_balance`, `stripe_subscription_id`, `expires_at`, `last_credit_refill`
  - Added `PromoSettings` model (singleton pattern) for promotional pricing
  - Lines 668-806: Complete promo settings implementation

- **File**: `/home/user/1983/documents/models.py`
  - Added usage tracking fields to `LawsuitDocument` (lines 78-110):
    - `ai_generations_purchased`, `ai_generations_used`
    - `extraction_minutes_purchased`, `extraction_minutes_used`
    - `stripe_payment_intent_id`, `stripe_customer_id`, `purchased_at`
  - Added properties: `ai_generations_remaining`, `extraction_minutes_remaining`, `is_purchased`
  - Created `DocumentAddon` model (lines 416-463) for tracking bundle purchases

#### Settings & Constants
- **File**: `/home/user/1983/config/settings.py:157-176`
  - Updated pricing constants:
    - `PRICE_STANDARD = 197.00`
    - `PRICE_STANDARD_PROMO = 129.00`
    - `PRICE_ADDON_BUNDLE = 29.00`
  - Added usage limit constants:
    - `BASIC_AI_GENERATIONS = 2`, `STANDARD_AI_GENERATIONS = 10`, `ADDON_AI_GENERATIONS = 20`
    - `BASIC_EXTRACTION_MINUTES = 5`, `STANDARD_EXTRACTION_MINUTES = 30`, `ADDON_EXTRACTION_MINUTES = 15`

#### UI/Template Updates
- **File**: `/home/user/1983/templates/accounts/pricing.html`
  - Complete redesign: 2-tier layout with promotional banner
  - Add-on bundle section showing $29 bundle
  - Feature comparison table
  - FAQ accordion
  - Dark mode support

- **File**: `/home/user/1983/templates/base.html:85-113`
  - Added dark mode CSS for cards, tables, card-headers

- **File**: `/home/user/1983/templates/documents/list.html`
  - Updated to show "Basic Plan" or "Standard Plan" instead of old 3-tier names

#### Admin Interface
- **File**: `/home/user/1983/accounts/admin.py`
  - Updated `SubscriptionAdmin`: removed old field references, added `referral_balance_display`
  - Added `PromoSettingsAdmin` with singleton pattern
  - Added `DocumentAddonAdmin` for managing bundles

#### Bug Fixes
- Fixed PDF download error: Changed `subscription.is_unlimited` to `subscription.is_standard` in `DocumentPDFView`
- Fixed document creation unpacking error in `document_create()` and `document_list()` views
- Fixed dark mode white boxes by removing `bg-light` and `thead-light` classes

---

### 🔄 IN PROGRESS (PHASE 1.4)

#### Testing Video Extraction Limits
**Status**: Code complete, awaiting user testing

**Test Steps**:
1. Pull latest changes: `git pull origin claude/fix-video-transcript-retrieval-011CUW3FJkHSmajZjFq2SCkY`
2. Test Basic plan (5 min limit):
   - Extract segments totaling < 5 minutes (should work)
   - Try to exceed 5 minutes (should block with error)
3. Test Standard plan (30 min limit):
   - Extract segments up to 30 minutes
   - Verify blocking after 30 minutes
4. Verify both JS confirmation and backend enforcement work

**What to Verify**:
- ✓ Confirmation dialog shows correct remaining minutes
- ✓ Extraction works when sufficient minutes available
- ✓ Backend blocks extraction when limit exceeded
- ✓ Error message shows appropriate upgrade/bundle link based on plan

---

### ⏳ PENDING (PHASE 2)

#### 2.1: Create Add-on Bundle Stripe Checkout
- **File to modify**: `/home/user/1983/accounts/stripe_views.py`
- **What to add**:
  - New view: `create_addon_checkout_session(request, document_id)`
  - Creates Stripe checkout for $29 bundle
  - Metadata: `{'type': 'addon_bundle', 'document_id': document_id}`

#### 2.2: Handle Bundle Purchase Success
- **File to modify**: `/home/user/1983/accounts/stripe_views.py`
- **What to add**:
  - Update `payment_success()` view to handle addon type
  - Create `DocumentAddon` record
  - Increment document limits:
    - `document.ai_generations_purchased += 20`
    - `document.extraction_minutes_purchased += 15`

#### 2.3: Add Purchase Bundle Button
- **Files to modify**:
  - `/home/user/1983/templates/documents/detail.html` - Add button near usage stats
  - `/home/user/1983/templates/documents/evidence_manager.html` - Add button in evidence section
- **What to add**:
  - "Purchase Add-on Bundle ($29)" button
  - Shows current usage and what bundle provides
  - Links to bundle checkout

#### 2.4: Test Bundle Purchase Flow
- Create document, use up limits
- Purchase bundle
- Verify limits increase by 20 AI gen + 15 min extraction
- Verify can purchase multiple bundles

---

### 🔮 FUTURE (PHASE 3)

- Usage dashboard showing all documents with usage stats
- Email notifications when usage is low
- Admin analytics showing bundle purchase patterns

---

## Key Database Schema

### Subscription Model
```python
class Subscription(models.Model):
    user = OneToOneField(User)
    plan_type = CharField(choices=[('basic', 'Basic'), ('standard', 'Standard')])
    is_active = BooleanField(default=True)
    referral_cash_balance = DecimalField(default=0.00)
    stripe_customer_id = CharField(max_length=255, blank=True)
```

### LawsuitDocument Model (Usage Tracking)
```python
class LawsuitDocument(models.Model):
    # ... existing fields ...

    # Usage tracking (added in redesign)
    ai_generations_purchased = IntegerField(default=2)  # Basic default
    extraction_minutes_purchased = IntegerField(default=5)  # Basic default
    ai_generations_used = IntegerField(default=0)
    extraction_minutes_used = DecimalField(max_digits=6, decimal_places=2, default=0.00)

    # Payment tracking
    stripe_payment_intent_id = CharField(max_length=255, blank=True)
    stripe_customer_id = CharField(max_length=255, blank=True)
    purchased_at = DateTimeField(null=True, blank=True)

    @property
    def ai_generations_remaining(self):
        return max(0, self.ai_generations_purchased - self.ai_generations_used)

    @property
    def extraction_minutes_remaining(self):
        return max(0, float(self.extraction_minutes_purchased) - float(self.extraction_minutes_used))

    @property
    def is_purchased(self):
        return bool(self.stripe_payment_intent_id)
```

### DocumentAddon Model (Bundle Purchases)
```python
class DocumentAddon(models.Model):
    document = ForeignKey('LawsuitDocument', on_delete=CASCADE)
    addon_type = CharField(max_length=20, default='bundle')
    ai_generations_added = IntegerField(default=20)
    extraction_minutes_added = IntegerField(default=15)
    amount = DecimalField(max_digits=6, decimal_places=2, default=29.00)
    stripe_payment_intent_id = CharField(max_length=255)
    purchased_at = DateTimeField(auto_now_add=True)
```

### PromoSettings Model (Singleton)
```python
class PromoSettings(models.Model):
    is_active = BooleanField(default=False)
    regular_price = DecimalField(max_digits=6, decimal_places=2, default=197.00)
    promo_price = DecimalField(max_digits=6, decimal_places=2, default=129.00)
    promo_text = CharField(max_length=200, default='Launch Special - Limited Time!')
    promo_badge_text = CharField(max_length=50, default='34% OFF')

    @property
    def current_price(self):
        return self.promo_price if self.is_active else self.regular_price
```

---

## Migration History & Database Notes

### Migration 0012: Usage Tracking Fields
- **Status**: Applied (via manual SQL + fake)
- **Issue**: Migration was faked initially, causing columns to be missing
- **Resolution**: Ran manual SQL to add columns, then faked migration

**Manual SQL Used** (if needed again):
```sql
ALTER TABLE documents_lawsuitdocument
ADD COLUMN ai_generations_purchased integer DEFAULT 2 NOT NULL,
ADD COLUMN extraction_minutes_purchased integer DEFAULT 5 NOT NULL,
ADD COLUMN ai_generations_used integer DEFAULT 0 NOT NULL,
ADD COLUMN extraction_minutes_used numeric(6,2) DEFAULT 0.00 NOT NULL,
ADD COLUMN stripe_payment_intent_id varchar(255) DEFAULT '' NOT NULL,
ADD COLUMN stripe_customer_id varchar(255) DEFAULT '' NOT NULL,
ADD COLUMN purchased_at timestamp with time zone NULL;

CREATE TABLE documents_documentaddon (
    id bigint NOT NULL PRIMARY KEY,
    addon_type varchar(20) NOT NULL DEFAULT 'bundle',
    ai_generations_added integer NOT NULL DEFAULT 20,
    extraction_minutes_added integer NOT NULL DEFAULT 15,
    amount numeric(6,2) NOT NULL DEFAULT 29.00,
    stripe_payment_intent_id varchar(255) NOT NULL,
    purchased_at timestamp with time zone NOT NULL,
    document_id bigint NOT NULL REFERENCES documents_lawsuitdocument(id) ON DELETE CASCADE
);

CREATE SEQUENCE documents_documentaddon_id_seq OWNED BY documents_documentaddon.id;
ALTER TABLE documents_documentaddon ALTER COLUMN id SET DEFAULT nextval('documents_documentaddon_id_seq');
```

---

## Critical Files Reference

### Backend Logic
- `/home/user/1983/accounts/models.py` - Subscription, PromoSettings models
- `/home/user/1983/documents/models.py` - LawsuitDocument usage tracking, DocumentAddon
- `/home/user/1983/documents/views_main.py:244-310` - AI generation limits
- `/home/user/1983/documents/views/evidence_views.py:100-160` - Video extraction limits
- `/home/user/1983/accounts/stripe_views.py` - Payment processing (needs addon support)

### Templates
- `/home/user/1983/templates/accounts/pricing.html` - Public pricing page
- `/home/user/1983/templates/documents/detail.html` - Document page with AI generation
- `/home/user/1983/templates/documents/evidence_manager.html` - Video extraction page
- `/home/user/1983/templates/documents/list.html` - Document list with plan display
- `/home/user/1983/templates/base.html:85-113` - Dark mode CSS

### Admin & Settings
- `/home/user/1983/accounts/admin.py` - Admin interfaces
- `/home/user/1983/config/settings.py:157-176` - Pricing constants

---

## Important Implementation Details

### Dual Enforcement (Security + UX)
All usage limits are enforced in TWO layers:

1. **Backend/Database (PRIMARY SECURITY)**
   - Python code checks limits before processing
   - Returns error if limit exceeded
   - Cannot be bypassed by user
   - Example: `if document.extraction_minutes_remaining < duration_minutes: return JsonResponse({'success': False, ...})`

2. **Frontend/JavaScript (USER EXPERIENCE)**
   - Confirmation dialogs warn before action
   - Shows remaining usage
   - Can be bypassed BUT backend still enforces
   - Example: `confirm('This will use X minutes. You have Y remaining. Continue?')`

### Document vs Subscription Scope
- **OLD SYSTEM**: Credits were subscription-wide (user.subscription.api_credit_balance)
- **NEW SYSTEM**: Limits are per-document (document.ai_generations_remaining)
- **Rationale**: Users pay $197 per document, so each document gets its own usage bucket
- **Add-ons**: Apply to specific documents, not subscription

### Promo Pricing Mechanism
- `PromoSettings` singleton model in Django admin
- `is_active` toggle controls whether promo price shows
- `current_price` property returns correct price based on toggle
- Stripe checkout uses `promo.current_price` dynamically
- Promotional banner shows/hides on pricing page based on `promo.is_active`

---

## Git Workflow

### Current Branch
```bash
claude/fix-video-transcript-retrieval-011CUW3FJkHSmajZjFq2SCkY
```

### Recent Commits
1. `beb318b` - Fix document list view for new pricing model
2. `14bfd4c` - Fix document creation error and complete dark mode support
3. `536afed` - Fix dark mode white boxes on pricing page
4. `f8a54fa` - Fix admin classes for new pricing model
5. `dcfa3d7` - Complete pricing system redesign to 2-tier + add-on bundle model
6. `266af8a` - PHASE 1.1 & 1.2: Add video extraction limit enforcement and tracking
7. `2067900` - PHASE 1.3: Add video extraction confirmation dialog and usage display (LATEST)

### Pushing Changes
```bash
# Always use -u flag for branch
git push -u origin claude/fix-video-transcript-retrieval-011CUW3FJkHSmajZjFq2SCkY

# If push fails due to network, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)
```

### Creating PR (After Testing Complete)
```bash
# Push latest changes
git push -u origin claude/fix-video-transcript-retrieval-011CUW3FJkHSmajZjFq2SCkY

# Create PR using gh CLI
gh pr create --title "Complete pricing system redesign to 2-tier + add-on bundle model" --body "$(cat <<'EOF'
## Summary
- Redesigned from 3-tier to simplified 2-tier + add-on bundle model
- Implemented document-scoped usage limits for AI generation and video extraction
- Added promotional pricing toggle in admin
- Full dark mode support

## Changes
- PHASE 1: Video extraction limit enforcement (COMPLETE)
- PHASE 2: Add-on bundle purchase flow (PENDING)

## Test Plan
- [x] AI generation limits work (Basic: 2, Standard: 10)
- [x] Video extraction limits work (Basic: 5 min, Standard: 30 min)
- [x] Confirmation dialogs show before usage
- [x] Backend enforces limits (cannot bypass)
- [ ] Bundle purchase flow (pending implementation)

Generated with Claude Code
EOF
)"
```

---

## Testing Checklist

### ✅ Already Tested & Working
- [x] AI generation limits (Basic: 2, Standard: 10)
- [x] AI generation confirmation dialog
- [x] Document creation with new model
- [x] Pricing page displays correctly
- [x] Promo pricing toggle in admin
- [x] Dark mode styling
- [x] PDF download (Standard only)

### 🔄 Ready for Testing (PHASE 1.4)
- [ ] Video extraction limits enforcement (Basic: 5 min, Standard: 30 min)
- [ ] Video extraction confirmation dialog
- [ ] Backend blocking when limits exceeded
- [ ] Error messages show appropriate upgrade/bundle links

### ⏳ Not Yet Testable (PHASE 2)
- [ ] Add-on bundle purchase flow
- [ ] Bundle adds 20 AI gen + 15 min extraction
- [ ] Multiple bundle purchases on same document
- [ ] Usage dashboard

---

## Known Issues & Gotchas

1. **Migration conflicts**: If migrations get out of sync with database, may need manual SQL + fake migration
2. **Admin user plan**: Admin accounts may have different plan behavior - test with non-admin users too
3. **Decimal precision**: `extraction_minutes_used` uses Decimal type to avoid floating point errors
4. **Stripe webhook**: Payment success flow needs testing with real Stripe webhooks (currently using redirect success)

---

## Next Session Priorities

1. **Immediate**: Get PHASE 1.4 testing results from user
2. **If tests pass**: Start PHASE 2.1 (Add-on bundle Stripe checkout)
3. **If tests fail**: Debug and fix issues with video extraction limits

---

## Questions for User (if needed)

- None currently - waiting for PHASE 1.4 test results

---

## Environment Info

- **Platform**: linux
- **Django**: 4.2.7
- **Database**: PostgreSQL (via Docker)
- **Payment**: Stripe API
- **Deployment**: Render (based on error logs)
- **Working Directory**: `/home/user/1983`
- **Git Status**: Feature branch, clean working tree (last check)

---

## Useful Commands

```bash
# Pull latest changes
git pull origin claude/fix-video-transcript-retrieval-011CUW3FJkHSmajZjFq2SCkY

# Run migrations
docker-compose exec web python manage.py migrate

# Check migration status
docker-compose exec web python manage.py showmigrations documents

# Access Django shell
docker-compose exec web python manage.py shell

# Check current plan for user
from accounts.models import Subscription
sub = Subscription.objects.get(user__id=1)
print(sub.plan_type, sub.is_active)

# Check document usage
from documents.models import LawsuitDocument
doc = LawsuitDocument.objects.get(id=34)
print(f"AI: {doc.ai_generations_remaining}/{doc.ai_generations_purchased}")
print(f"Video: {doc.extraction_minutes_remaining}/{doc.extraction_minutes_purchased}")

# Check promo settings
from accounts.models import PromoSettings
promo = PromoSettings.get_or_create_settings()
print(f"Active: {promo.is_active}, Price: ${promo.current_price}")
```

---

**END OF HANDOFF DOCUMENT**
