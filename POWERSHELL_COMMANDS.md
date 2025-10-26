# 🔧 PowerShell Commands - Merge AI Enhancement to Master

## Quick Reference Commands

### ✅ **RECOMMENDED: Option 1 - Pull Request (Safest)**

```powershell
# Already done - your feature branch is pushed!
# Just create the PR on GitHub

# Visit this URL to create PR:
Start-Process "https://github.com/LaylaAddi/1983/pull/new/claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv"

# Or if you have GitHub CLI installed:
gh pr create `
  --title "AI-Enhanced Legal Document Generation" `
  --body "## Summary
Implements GPT-4 powered personalization of legal sections with budget controls and upgrade prompts.

## Features
- AI enhancement using GPT-4o for facts, introduction, claims, parties sections
- Budget controls: \`$0.50\` free tier (~8 docs), \`$10/month\` unlimited (~166 docs)
- Automatic upgrade prompts when users hit limits
- Graceful fallback to templates when AI unavailable
- Cost tracking per section and per user

## Testing
- 9 automated tests all passing (see test_ai_enhancement.py)
- Estimated cost: ~\`$0.06\` per document

## Documentation
- STEP_5_IMPLEMENTATION_COMPLETE.md - Full implementation details
- DEPLOYMENT_GUIDE.md - Production deployment instructions
- test_ai_enhancement.py - Comprehensive test suite

See commit 42855ee for full details."
```

---

### ⚡ **Option 2 - Direct Merge (Fast & Simple)**

```powershell
# Navigate to your repo
cd C:\path\to\1983

# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Merge the AI enhancement branch
git merge claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# Push to main
git push origin main

# ✅ Done! AI enhancement is now on main
```

---

### 🎯 **Option 3 - Squash Merge (Clean Git History)**

```powershell
# Navigate to your repo
cd C:\path\to\1983

# Switch to main
git checkout main

# Pull latest
git pull origin main

# Squash merge (combines all commits into one)
git merge --squash claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# Commit the squashed changes
git commit -m "Add AI-enhanced legal document generation with GPT-4

Implements AI enhancement service using GPT-4o for personalized legal sections.
Includes budget controls ($0.50 free tier), upgrade prompts, and template fallback.

New files:
- documents/services/ai_enhancement_service.py (445 lines)
- documents/migrations/0011_documentsection_ai_tracking.py
- test_ai_enhancement.py (comprehensive test suite)
- DEPLOYMENT_GUIDE.md

Enhanced files:
- documents/services/section_generation_service.py
- documents/services/document_orchestrator_service.py

Features:
- AI-enhanced sections: facts, introduction, claims, parties
- Budget tracking: UserProfile.total_api_cost, Subscription.api_credit_balance
- Upgrade prompts when users hit $0.50 free limit
- Automatic fallback to templates if AI fails or over budget
- GPT-4o with temperature 0.2-0.3 for legal accuracy

Cost: ~$0.06 per document (4 AI-enhanced sections)
Free users: ~8 documents | Unlimited: ~166/month

Tests: 9/9 passing (migration, budget, AI quality, fallback, upgrade prompts)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to main
git push origin main

# ✅ Clean single commit on main
```

---

### 🧹 **Cleanup After Merge (Optional)**

```powershell
# Delete local feature branch
git branch -d claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# Delete remote feature branch
git push origin --delete claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# Verify main is clean
git log --oneline -5
```

---

## 🧪 **Testing Commands (Before Merging)**

### Run Tests Locally

```powershell
# Activate virtual environment (adjust path as needed)
.\venv\Scripts\Activate.ps1

# Run migration
python manage.py migrate

# Run test suite
python test_ai_enhancement.py

# Expected output:
# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                   AI ENHANCEMENT TEST SUITE                                ║
# ╚════════════════════════════════════════════════════════════════════════════╝
# ...
# RESULTS: 9/9 tests passed
# 🎉 ALL TESTS PASSED!
```

### Manual Browser Testing

```powershell
# Start dev server
python manage.py runserver

# Then visit:
# http://localhost:8000/documents/create/
# Create a document and click "Auto-populate sections"
# Should see: "Sections generated! X sections enhanced with AI (cost: $X.XX)"
```

---

## 🚀 **Production Deployment (After Merge)**

### If Deploying to Render/Heroku/Cloud

```powershell
# Render auto-deploys from main - just merge!
# Heroku:
git push heroku main

# Manual server:
ssh user@your-server.com
cd /path/to/1983
git pull origin main
python manage.py migrate
sudo systemctl restart gunicorn
```

### If Using Docker

```powershell
# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Run migration
docker-compose exec web python manage.py migrate

# Run tests
docker-compose exec web python test_ai_enhancement.py
```

---

## 📊 **Verify Deployment**

### Check Git Status

```powershell
# View current branch and commits
git status
git log --oneline -5

# Check what's on main
git log origin/main --oneline -5

# Compare branches
git log main..claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv --oneline
```

### View Changes Before Merging

```powershell
# See what will be merged
git diff main..claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# Just file names
git diff --name-only main..claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# Summary stats
git diff --stat main..claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv
```

---

## 🔄 **Rollback (If Needed)**

### Undo Merge (Before Pushing)

```powershell
# If you merged but haven't pushed yet
git reset --hard HEAD~1
```

### Undo Merge (After Pushing)

```powershell
# Revert the merge commit
git revert -m 1 HEAD

# Push the revert
git push origin main

# Revert the migration (on production)
python manage.py migrate documents 0010_purchaseddocument
```

---

## 📝 **Complete Deployment Checklist**

```powershell
# ✅ Step 1: Test locally
python test_ai_enhancement.py

# ✅ Step 2: Merge to main (choose one option above)
git merge claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# ✅ Step 3: Push to main
git push origin main

# ✅ Step 4: Deploy to production
# (Automatic for Render, or manual commands above)

# ✅ Step 5: Run migration in production
python manage.py migrate

# ✅ Step 6: Verify in production
python test_ai_enhancement.py

# ✅ Step 7: Test with real user
# Create document → Auto-populate → Verify AI enhancement

# ✅ Step 8: Monitor costs
# Check Django admin → User Profiles → total_api_cost

# ✅ Step 9: Clean up (optional)
git branch -d claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv
git push origin --delete claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# 🎉 DONE!
```

---

## 🎯 **My Recommendation**

**Use Option 1 (Pull Request)** for:
- ✅ Code review before merging
- ✅ CI/CD checks (if configured)
- ✅ Team visibility
- ✅ Documentation trail

**Use Option 2 (Direct Merge)** for:
- ✅ Solo projects
- ✅ Quick deployment
- ✅ Already tested locally

**Use Option 3 (Squash Merge)** for:
- ✅ Clean git history
- ✅ Single atomic commit
- ✅ Easier to revert if needed

---

## ⚡ **Fastest Path to Production**

```powershell
# Copy-paste ready - THE FASTEST WAY:

# 1. Switch to main
git checkout main

# 2. Merge
git merge claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# 3. Push
git push origin main

# 4. Deploy (if manual)
# ssh to server, git pull, migrate, restart

# DONE! ✅
```

---

## 📞 **Need Help?**

If something goes wrong:

```powershell
# Check current state
git status
git log --oneline -5

# See what's different
git diff main

# Abort merge if in progress
git merge --abort

# Reset to previous state
git reset --hard origin/main
```

---

## 🎉 **What Happens After Merge**

1. ✅ AI enhancement is live on main branch
2. ✅ Users can create AI-enhanced documents
3. ✅ Free users get ~8 AI docs ($0.50 limit)
4. ✅ Unlimited users get ~166 AI docs/month ($10 credit)
5. ✅ Upgrade prompts appear when limits reached
6. ✅ System falls back to templates gracefully
7. ✅ All costs tracked in UserProfile and Subscription

**Cost per document**: ~$0.06 (4 AI-enhanced sections)
**Models**: GPT-4o (temperature 0.2-0.3)
**Sections enhanced**: facts, introduction, claims, parties

---

Ready to merge? Pick an option above and go! 🚀
