# 🚀 AI Enhancement Deployment Guide

## Step-by-Step Deployment to Production

### 📋 Prerequisites

- [x] OpenAI API key in environment variables
- [x] Code committed to feature branch
- [x] All changes pushed to remote

---

## 🔧 Local Testing (Before Merging)

### 1. Run Migration

```bash
# Activate your virtual environment first
python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying documents.0011_documentsection_ai_tracking... OK
```

### 2. Run Test Suite

```bash
python test_ai_enhancement.py
```

This will:
- ✅ Verify migration successful
- ✅ Test cost estimation
- ✅ Create test user with free tier
- ✅ Test budget checking
- ✅ Create document with AI enhancement
- ✅ Verify AI content quality
- ✅ Test budget limits and upgrade prompts
- ✅ Test fallback to templates
- ✅ Test unlimited tier behavior

Expected output:
```
╔════════════════════════════════════════════════════════════════════════════╗
║                   AI ENHANCEMENT TEST SUITE                                ║
╚════════════════════════════════════════════════════════════════════════════╝

TEST SUMMARY
================================================================================
✅ PASS - Migration Check
✅ PASS - Cost Estimation
✅ PASS - Create Test User
✅ PASS - Budget Check
✅ PASS - AI Enhancement
✅ PASS - Content Quality
✅ PASS - Budget Limits
✅ PASS - Fallback Mechanism
✅ PASS - Unlimited Tier

RESULTS: 9/9 tests passed
================================================================================

🎉 ALL TESTS PASSED! AI Enhancement is working correctly.
```

### 3. Manual Testing in Browser

```bash
# Start dev server
python manage.py runserver
```

1. **Create a test document**:
   - Go to `/documents/create/`
   - Fill in description with real incident details
   - Click "Auto-populate sections"

2. **Check results**:
   - Should see message: "Sections generated! X sections enhanced with AI (cost: $X.XX)"
   - View document to see AI-enhanced content
   - Check that facts section is professionally written

3. **Test budget limit**:
   - In Django admin, set user's `api_cost_limit` to `0.48`
   - Try auto-populating another document
   - Should see upgrade prompt instead of AI enhancement
   - Sections should still be created using templates

---

## 📤 PowerShell Commands to Merge to Master

### Option A: Merge via Pull Request (Recommended)

```powershell
# 1. View the current branch
git status

# 2. Make sure all changes are committed
git log -1

# 3. Push to remote (already done)
git push -u origin claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# 4. Create PR via GitHub CLI (if installed)
gh pr create --title "AI-Enhanced Legal Document Generation" --body "Implements GPT-4 powered personalization of legal sections with budget controls and upgrade prompts. See STEP_5_IMPLEMENTATION_COMPLETE.md for details."

# OR manually create PR:
# Visit: https://github.com/LaylaAddi/1983/pull/new/claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv
```

### Option B: Direct Merge to Main (Fast)

```powershell
# 1. Switch to main branch
git checkout main

# 2. Pull latest changes from remote
git pull origin main

# 3. Merge the feature branch
git merge claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# 4. Push to main
git push origin main

# 5. Delete the feature branch (optional)
git branch -d claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv
git push origin --delete claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv
```

### Option C: Squash Merge (Clean History)

```powershell
# 1. Switch to main
git checkout main

# 2. Pull latest
git pull origin main

# 3. Squash merge (combines all commits into one)
git merge --squash claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# 4. Commit the squashed changes
git commit -m "Add AI-enhanced legal document generation with GPT-4

Implements AI enhancement service using GPT-4o for personalized legal sections.
Includes budget controls ($0.50 free tier), upgrade prompts, and template fallback.

- New: documents/services/ai_enhancement_service.py
- Enhanced: section_generation_service.py, document_orchestrator_service.py
- Migration: AI tracking fields on DocumentSection

Cost: ~$0.06 per document (4 AI-enhanced sections)
Free users: ~8 documents | Unlimited: ~166/month"

# 5. Push to main
git push origin main

# 6. Clean up feature branch
git branch -d claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv
git push origin --delete claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv
```

---

## 🌐 Production Deployment

### 1. After Merging to Main

```powershell
# On production server (or via CI/CD)

# Pull latest main
git pull origin main

# Run migration
python manage.py migrate

# Collect static files (if needed)
python manage.py collectstatic --noinput

# Restart web server
# For Gunicorn:
sudo systemctl restart gunicorn

# For Docker:
docker-compose restart web
```

### 2. Verify Production Deployment

```bash
# SSH into production server
ssh user@your-server.com

# Check migration status
python manage.py showmigrations documents

# Should show:
# [X] 0011_documentsection_ai_tracking

# Test AI enhancement
python test_ai_enhancement.py
```

### 3. Monitor First AI Calls

```python
# In Django shell on production
python manage.py shell

from accounts.models import UserProfile

# Check API costs
profiles = UserProfile.objects.filter(total_api_cost__gt=0)
for p in profiles:
    print(f"{p.user.username}: ${p.total_api_cost} / ${p.api_cost_limit}")
```

---

## 🔍 Troubleshooting

### Issue: "No module named 'openai'"

```bash
# Install OpenAI package
pip install openai==1.52.0
```

### Issue: "OPENAI_API_KEY not configured"

```bash
# Add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Or export in shell
export OPENAI_API_KEY=sk-your-key-here

# For Docker, add to docker-compose.yml:
# environment:
#   - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Issue: AI enhancement not working

```python
# Check budget
from accounts.models import UserProfile
profile = UserProfile.objects.get(user__username='your-username')
print(f"Budget: ${profile.remaining_api_budget}")

# If over limit:
profile.total_api_cost = Decimal('0.00')
profile.save()
```

### Issue: All sections using templates (not AI)

Possible causes:
1. User over budget → Check `UserProfile.total_api_cost`
2. OpenAI API key missing → Check environment variable
3. AI disabled → Check `use_ai=False` parameter
4. OpenAI API error → Check logs for error messages

Solution:
```python
# Force AI enhancement
from documents.services.document_orchestrator_service import DocumentOrchestratorService
orchestrator = DocumentOrchestratorService(document)
result = orchestrator.auto_populate_document(use_ai=True)
print(result)  # Check for errors in response
```

---

## 📊 Monitoring AI Usage

### Check Total AI Spending

```python
from accounts.models import UserProfile
from django.db.models import Sum

total_spent = UserProfile.objects.aggregate(Sum('total_api_cost'))
print(f"Total AI spending: ${total_spent['total_api_cost__sum']}")
```

### Check AI-Enhanced Documents

```python
from documents.models import DocumentSection

ai_sections = DocumentSection.objects.filter(ai_enhanced=True)
total_cost = sum(s.ai_cost for s in ai_sections)
print(f"AI-enhanced sections: {ai_sections.count()}")
print(f"Total cost: ${total_cost}")
```

### Users Approaching Limit

```python
from accounts.models import UserProfile

approaching_limit = UserProfile.objects.filter(
    total_api_cost__gte=0.40,  # >= 80% of $0.50
    total_api_cost__lt=0.50
)

for profile in approaching_limit:
    print(f"{profile.user.username}: ${profile.total_api_cost} / $0.50")
    print(f"  {profile.usage_percentage}% used")
```

---

## 🎯 Success Criteria

Before marking deployment complete, verify:

- [x] Migration ran successfully
- [x] Test suite passes (9/9 tests)
- [x] AI enhancement creates professional content
- [x] Budget tracking works correctly
- [x] Upgrade prompts appear when limit reached
- [x] Fallback to templates works when AI fails
- [x] No errors in production logs
- [x] First real user document generated successfully
- [x] Costs are being tracked accurately

---

## 🔄 Rollback Plan (If Needed)

If issues occur in production:

```powershell
# 1. Revert the migration
python manage.py migrate documents 0010_purchaseddocument

# 2. Revert the code
git revert HEAD

# 3. Push the revert
git push origin main

# 4. Restart server
sudo systemctl restart gunicorn
```

---

## 📞 Support

If you encounter issues:

1. Check logs: `/var/log/gunicorn/error.log`
2. Review test output: `python test_ai_enhancement.py`
3. Check OpenAI dashboard for API errors
4. Verify environment variables are set

---

## 🎉 Deployment Complete!

Once verified in production:
- ✅ Users can create AI-enhanced documents
- ✅ Free users get 8 AI-enhanced documents ($0.50 limit)
- ✅ Unlimited users get ~166 documents/month ($10 credit)
- ✅ Upgrade prompts guide users to higher tiers
- ✅ System gracefully falls back to templates when needed
