# 🪟 Windows Commands - Git & Docker Compose Deployment

## Complete command reference for Windows (PowerShell & CMD)

---

## 📁 **PART 1: Git Commands (Merge to Main/Master)**

### **Option A: Direct Merge to Main (FASTEST)**

#### PowerShell:
```powershell
# Navigate to your repo
cd C:\path\to\1983

# Check current branch
git status

# Switch to main branch (or master if that's your default)
git checkout main

# Pull latest changes from remote
git pull origin main

# Merge the AI enhancement branch
git merge claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# If merge conflicts occur, resolve them, then:
# git add .
# git commit -m "Resolve merge conflicts"

# Push to main
git push origin main

# Clean up - delete local feature branch (optional)
git branch -d claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# Delete remote feature branch (optional)
git push origin --delete claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# ✅ Done!
```

#### CMD (Command Prompt):
```cmd
REM Navigate to your repo
cd C:\path\to\1983

REM Check current branch
git status

REM Switch to main
git checkout main

REM Pull latest
git pull origin main

REM Merge
git merge claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

REM Push
git push origin main

REM ✅ Done!
```

---

### **Option B: Squash Merge (Clean History)**

#### PowerShell:
```powershell
# Navigate to repo
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
Includes budget controls (`$0.50 free tier), upgrade prompts, and template fallback.

Features:
- AI-enhanced sections: facts, introduction, claims, parties
- Budget tracking and limits
- Automatic upgrade prompts
- Graceful fallback to templates

Cost: ~`$0.06 per document (4 AI-enhanced sections)
Free users: ~8 documents | Unlimited: ~166/month

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to main
git push origin main

# Clean up
git branch -d claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv
git push origin --delete claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv

# ✅ Done!
```

---

### **Option C: Create Pull Request**

#### PowerShell:
```powershell
# If you have GitHub CLI installed:
gh pr create `
  --title "AI-Enhanced Legal Document Generation" `
  --body "See FINAL_SUMMARY.md for complete details"

# Or open in browser:
Start-Process "https://github.com/LaylaAddi/1983/pull/new/claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv"
```

---

## 🐳 **PART 2: Docker Compose Commands (Windows)**

### **Check if Docker is Running**

#### PowerShell:
```powershell
# Check Docker status
docker --version
docker-compose --version

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a
```

#### CMD:
```cmd
REM Check Docker version
docker --version
docker-compose --version

REM List containers
docker ps
```

---

### **Start Docker Compose Services**

#### PowerShell:
```powershell
# Navigate to project directory
cd C:\path\to\1983

# Start all services in background
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web

# Check service status
docker-compose ps
```

#### CMD:
```cmd
REM Navigate to project
cd C:\path\to\1983

REM Start services
docker-compose up -d

REM View logs
docker-compose logs -f web
```

---

### **Run Migration in Docker**

#### PowerShell:
```powershell
# Navigate to project
cd C:\path\to\1983

# Run migrations
docker-compose exec web python manage.py migrate

# Expected output:
# Running migrations:
#   Applying documents.0011_documentsection_ai_tracking... OK
```

#### CMD:
```cmd
REM Navigate to project
cd C:\path\to\1983

REM Run migrations
docker-compose exec web python manage.py migrate
```

---

### **Run Tests in Docker**

#### PowerShell:
```powershell
# Run the AI enhancement test suite
docker-compose exec web python test_ai_enhancement.py

# Or run Django tests
docker-compose exec web python manage.py test

# Run specific test
docker-compose exec web python manage.py test documents.tests.test_ai_enhancement
```

#### CMD:
```cmd
REM Run test suite
docker-compose exec web python test_ai_enhancement.py

REM Run Django tests
docker-compose exec web python manage.py test
```

---

### **Access Django Shell in Docker**

#### PowerShell:
```powershell
# Open Django shell
docker-compose exec web python manage.py shell

# Then inside shell:
# >>> from accounts.models import UserProfile
# >>> from decimal import Decimal
# >>> profile = UserProfile.objects.first()
# >>> print(f"Budget: ${profile.remaining_api_budget}")
# >>> exit()
```

---

### **View Environment Variables in Docker**

#### PowerShell:
```powershell
# Check if OPENAI_API_KEY is set
docker-compose exec web printenv OPENAI_API_KEY

# View all environment variables
docker-compose exec web printenv
```

---

### **Restart Services After Code Changes**

#### PowerShell:
```powershell
# After pulling new code from git:
cd C:\path\to\1983

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Or just restart without rebuild (faster):
docker-compose restart web

# View logs to ensure it started
docker-compose logs -f web
```

#### CMD:
```cmd
REM Rebuild and restart
cd C:\path\to\1983
docker-compose down
docker-compose up -d --build

REM Or just restart
docker-compose restart web
```

---

### **Run Collectstatic in Docker**

#### PowerShell:
```powershell
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

---

### **Create Superuser in Docker**

#### PowerShell:
```powershell
# Create admin user
docker-compose exec web python manage.py createsuperuser

# Follow prompts to enter username, email, password
```

---

### **Stop Docker Services**

#### PowerShell:
```powershell
# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop web

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (WARNING: deletes database!)
docker-compose down -v
```

---

## 🚀 **COMPLETE DEPLOYMENT WORKFLOW (Windows + Docker)**

### **Step-by-Step: Merge Code & Deploy**

#### PowerShell (Complete Workflow):
```powershell
# ===== 1. MERGE TO MAIN =====
cd C:\path\to\1983
git checkout main
git pull origin main
git merge claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv
git push origin main

# ===== 2. STOP DOCKER SERVICES =====
docker-compose down

# ===== 3. REBUILD CONTAINERS =====
docker-compose build

# ===== 4. START SERVICES =====
docker-compose up -d

# ===== 5. RUN MIGRATION =====
docker-compose exec web python manage.py migrate

# ===== 6. COLLECT STATIC FILES =====
docker-compose exec web python manage.py collectstatic --noinput

# ===== 7. RUN TESTS =====
docker-compose exec web python test_ai_enhancement.py

# ===== 8. CHECK LOGS =====
docker-compose logs -f web

# ===== 9. VERIFY IN BROWSER =====
# Open: http://localhost:8000

# ✅ DEPLOYMENT COMPLETE!
```

---

## 🧪 **TESTING COMMANDS**

### **Run All Tests**

#### PowerShell:
```powershell
# With Docker:
docker-compose exec web python test_ai_enhancement.py

# Without Docker (if you have Python locally):
# First activate virtual environment:
.\venv\Scripts\Activate.ps1
python test_ai_enhancement.py
```

#### Expected Output:
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

---

## 🔍 **TROUBLESHOOTING**

### **Problem: "docker-compose: command not found"**

#### PowerShell:
```powershell
# Try with dash instead of hyphen:
docker compose up -d

# Or install Docker Desktop for Windows:
# https://www.docker.com/products/docker-desktop
```

---

### **Problem: "Port 8000 already in use"**

#### PowerShell:
```powershell
# Find process using port 8000:
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID):
taskkill /PID <PID> /F

# Or change port in docker-compose.yml:
# ports:
#   - "8001:8000"  # Use port 8001 instead
```

---

### **Problem: "Permission denied" errors**

#### PowerShell (Run as Administrator):
```powershell
# Right-click PowerShell → "Run as Administrator"
# Then run commands again
```

---

### **Problem: "OPENAI_API_KEY not found"**

#### PowerShell:
```powershell
# Create .env file in project root:
cd C:\path\to\1983
New-Item -Path .env -ItemType File

# Add to .env file:
Add-Content -Path .env -Value "OPENAI_API_KEY=sk-your-key-here"

# Or set in docker-compose.yml:
# Edit docker-compose.yml and add under environment:
#   - OPENAI_API_KEY=sk-your-key-here

# Restart services:
docker-compose restart web
```

---

### **Problem: "Database migration error"**

#### PowerShell:
```powershell
# Check migration status:
docker-compose exec web python manage.py showmigrations

# If stuck, try fake migration (careful!):
docker-compose exec web python manage.py migrate --fake documents 0011

# Or reset database (WARNING: deletes all data!):
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## 📊 **MONITORING COMMANDS**

### **View Logs**

#### PowerShell:
```powershell
# All services:
docker-compose logs -f

# Just web service:
docker-compose logs -f web

# Last 100 lines:
docker-compose logs --tail=100 web

# Since 10 minutes ago:
docker-compose logs --since 10m web
```

---

### **Check Container Resource Usage**

#### PowerShell:
```powershell
# View CPU/Memory usage:
docker stats

# View disk usage:
docker system df
```

---

### **Access Database**

#### PowerShell:
```powershell
# PostgreSQL:
docker-compose exec db psql -U postgres -d lawsuit_app

# Then in PostgreSQL shell:
# \dt - list tables
# SELECT * FROM accounts_userprofile LIMIT 5;
# \q - quit
```

---

## 🎯 **QUICK REFERENCE CHEAT SHEET**

```powershell
# ===== GIT COMMANDS =====
git checkout main                                          # Switch to main
git pull origin main                                       # Pull latest
git merge claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv  # Merge
git push origin main                                       # Push to main

# ===== DOCKER COMPOSE COMMANDS =====
docker-compose up -d                                       # Start services
docker-compose down                                        # Stop services
docker-compose restart web                                 # Restart web
docker-compose logs -f web                                 # View logs
docker-compose exec web python manage.py migrate          # Run migration
docker-compose exec web python test_ai_enhancement.py     # Run tests
docker-compose exec web python manage.py shell            # Django shell
docker-compose ps                                          # Check status

# ===== VERIFY DEPLOYMENT =====
docker-compose exec web python manage.py showmigrations   # Check migrations
docker-compose exec web printenv OPENAI_API_KEY            # Check API key
docker ps                                                  # Running containers

# ===== CLEANUP =====
docker-compose down -v                                     # Remove everything
docker system prune -a                                     # Clean Docker cache
```

---

## 🎉 **COMPLETE DEPLOYMENT (Copy-Paste Ready)**

### **PowerShell - One Complete Script**

```powershell
# ================================
# COMPLETE DEPLOYMENT SCRIPT
# ================================

# 1. Navigate to project
cd C:\path\to\1983

# 2. Merge to main
Write-Host "Step 1: Merging to main..." -ForegroundColor Green
git checkout main
git pull origin main
git merge claude/enhance-legal-doc-ai-011CUUnQmnitt8PS6HgJuKyv
git push origin main

# 3. Rebuild Docker services
Write-Host "Step 2: Rebuilding Docker services..." -ForegroundColor Green
docker-compose down
docker-compose up -d --build

# 4. Wait for services to start
Write-Host "Step 3: Waiting for services to start..." -ForegroundColor Green
Start-Sleep -Seconds 10

# 5. Run migration
Write-Host "Step 4: Running migration..." -ForegroundColor Green
docker-compose exec web python manage.py migrate

# 6. Collect static files
Write-Host "Step 5: Collecting static files..." -ForegroundColor Green
docker-compose exec web python manage.py collectstatic --noinput

# 7. Run tests
Write-Host "Step 6: Running tests..." -ForegroundColor Green
docker-compose exec web python test_ai_enhancement.py

# 8. Show final status
Write-Host "Step 7: Deployment complete!" -ForegroundColor Green
docker-compose ps

Write-Host "`n✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "Open browser: http://localhost:8000" -ForegroundColor Cyan
```

---

## 📱 **Access Application**

```powershell
# Open in default browser:
Start-Process "http://localhost:8000"

# Or manually visit:
# http://localhost:8000              - Main site
# http://localhost:8000/admin        - Django admin
# http://localhost:8000/documents/   - Documents list
```

---

## 🆘 **Emergency Rollback**

#### PowerShell:
```powershell
# If deployment goes wrong:

# 1. Revert Git merge
git checkout main
git reset --hard HEAD~1
git push origin main --force

# 2. Rebuild with old code
docker-compose down
docker-compose up -d --build

# 3. Revert migration
docker-compose exec web python manage.py migrate documents 0010_purchaseddocument

# ✅ Rolled back to previous version
```

---

## ✅ **Success Checklist**

After running commands, verify:

- [ ] Git merged to main successfully
- [ ] Docker containers running (`docker-compose ps`)
- [ ] Migration applied (`showmigrations` shows [X] for 0011)
- [ ] Tests pass (9/9)
- [ ] Web app accessible at http://localhost:8000
- [ ] Can create new document
- [ ] Can auto-populate sections
- [ ] AI enhancement working (check section content)
- [ ] Budget tracking working (check Django admin)

---

🎉 **You're ready to deploy! Copy-paste the commands above and go!** 🚀
