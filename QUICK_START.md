# 🚀 AI Resume Optimizer v2.0 - Quick Start (5 Minutes)

## What You're Getting

✅ **Production-Grade System** — Clean code, modular architecture, professional logging
✅ **Complete Database** — 10 tables, full history, audit trail, versioning
✅ **Knowledge Base** — Extract real metrics once, reuse infinitely
✅ **Smart Remixing** — AI creates role-specific resumes using YOUR real achievements
✅ **Rich Features** — Scoring, analytics, user management, API tracking

---

## Step 1: Prepare Files (1 min)

Copy these files to your project:

```
app_v2_0_enterprise.py  → rename to app.py
config.py              → stays as is
requirements.txt       → stays as is
src/
  ├── database_operations.py
  ├── extraction_engines.py
  ├── optimization_engines.py
  └── api_clients.py
.gitignore
```

File locations:
```
~/Desktop/ai-resume-optimizer/
├── app.py
├── config.py
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── database_operations.py
│   ├── extraction_engines.py
│   ├── optimization_engines.py
│   └── api_clients.py
├── data/
│   └── (auto-created)
└── logs/
    └── (auto-created)
```

---

## Step 2: Install Dependencies (1 min)

```bash
cd ~/Desktop/ai-resume-optimizer
pip3 install -r requirements.txt
```

---

## Step 3: Start Ollama (1 min)

**Terminal 1:**
```bash
ollama serve
# Output: Listening on 127.0.0.1:11434
```

**Terminal 2:**
```bash
ollama pull mistral
# Wait for download... ~4GB
```

---

## Step 4: Run Application (1 min)

**Terminal 3:**
```bash
cd ~/Desktop/ai-resume-optimizer
python3 -m streamlit run app.py
```

Opens at: http://localhost:8501

---

## Step 5: Use It (1 min)

### First Time:

1. **Sign in** (sidebar) → Create account with any username
2. **Go to "📚 Knowledge Base"** → Paste your BEST resume → Click "💾 Save"
3. **App extracts**:
   - Real metrics (124.53%, 4.62 → 4.72, etc.)
   - Skills (Python, SuiteScript, etc.)
   - Achievements (with context)

### For Any JD:

1. **Go to "✏️ Optimize"**
2. **Paste job description**
3. **Click "🚀 Generate"**
4. **App**:
   - Detects role (Functional/Technical/Senior)
   - Remixes YOUR real metrics
   - Creates tailored resume
   - Scores it (0-100)
5. **Download**

### View Everything:

1. **"📊 History"** → See all optimizations, scores, dates
2. **"⚙️ Settings"** → Database location, log location, API status

---

## Database Features

Everything is stored:

| What | Where |
|------|-------|
| Your master resume | `knowledge_base` table |
| Extracted metrics | `kb_metrics` table (10+ usually) |
| Skills by category | `kb_skills` table |
| All optimizations | `optimizations` table |
| Metrics used per resume | `optimization_metrics_used` table |
| API calls made | `api_calls_log` table |
| Everything you did | `audit_log` table |

**Location**: `data/resume_optimizer_v2.db`

**Backup**: Auto-created in `data/backups/`

---

## Key Differences from V1.0

| Feature | V1.0 | V2.0 |
|---------|------|------|
| **Metrics** | Invented (fake) | Real (from KB) |
| **Code** | Monolithic | Modular 5-file system |
| **Database** | Basic schema | 10 tables, full tracking |
| **History** | Limited | Complete audit trail |
| **Reusability** | One JD at a time | Unlimited (KB mode) |
| **Logging** | None | Professional (logs/) |
| **File Organization** | Flat | Clean folders (src/, data/, logs/) |
| **Error Handling** | Basic | Transaction-safe |
| **User Management** | None | Multi-user support |

---

## Example Workflow

**Scenario**: Apply to 50 NetSuite roles

**V1.0 Approach (Bad)**:
1. Paste resume 50 times
2. Get fake metrics each time ❌

**V2.0 Approach (Better)**:
1. Build KB once (5 min) → Extract 20+ real metrics
2. For each JD (1 min):
   - Paste JD
   - Click Generate
   - Get role-specific resume with YOUR real metrics
3. Repeat 50 times in 50 minutes total

**Real metrics used**:
- "124.53% productivity (FY25 Q2)"
- "4.62 → 4.72 CSAT improvement"
- "567 comments, 77 answers, 22 badges"
- "315 cases closed"
- "98 product issues filed"

---

## Troubleshooting

**Ollama not running?**
```bash
ollama serve  # Start it
```

**Need to reset database?**
```bash
rm data/resume_optimizer_v2.db
# Restart app (recreates)
```

**Check logs for errors**
```bash
tail -f logs/app.log
```

**API not available?**
- Ollama: Make sure `ollama serve` is running
- Gemini: Add API key in config.py
- OpenAI: Add API key in config.py

---

## Deployment to Cloud

Want to share the app or use online?

**Option A: Streamlit Cloud (Recommended)**
```bash
git push  # To GitHub
# Visit https://share.streamlit.io
# Deploy from GitHub
# Add secrets in dashboard
```

**Option B: Local Network**
```bash
streamlit run app.py --server.address 0.0.0.0
# Access from: http://your-ip:8501
```

**Note**: Ollama only works locally. Cloud deployments use Gemini/OpenAI.

---

## What Gets Tracked

✅ Users created  
✅ Knowledge bases (with versions)  
✅ Extracted metrics, skills, achievements  
✅ Job descriptions analyzed  
✅ Resumes generated  
✅ Which metrics used in each resume  
✅ API calls made (provider, tokens, time)  
✅ Every user action (audit trail)  

All in database. All queryable. All timestamped.

---

## Next Steps

1. **Use it** for your job search
2. **Customize** if needed (edit config.py)
3. **Deploy** to cloud when ready
4. **Build portfolio** — this IS a portfolio project
   - Clean architecture ✅
   - Production database ✅
   - Full history tracking ✅
   - Multi-user support ✅
   - Professional logging ✅

---

## Files Summary

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI (main entry) |
| `config.py` | All settings & configurations |
| `src/database_operations.py` | Database (10 tables, CRUD) |
| `src/extraction_engines.py` | Extract metrics, skills, achievements |
| `src/optimization_engines.py` | Role detection, remixing, scoring |
| `src/api_clients.py` | LLM wrappers (Ollama, Gemini, OpenAI) |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Git ignore rules |

---

## Time Breakdown

**Initial Setup**: 5 minutes total
- Install: 1 min
- Start Ollama: 1 min
- Run app: 1 min
- Create KB: 2 min

**Per JD**: 1-2 minutes
- Paste JD: 30 sec
- Generate: 30 sec
- Review/download: 30 sec

**Reuse**: Infinite
- Same KB for 100+ JDs
- No re-extraction needed
- Fast iterations

---

## Support

**Check logs**:
```bash
cat logs/app.log | grep ERROR
```

**Test extraction**:
```python
from src.extraction_engines import analyze_resume
result = analyze_resume("your resume text")
print(result)
```

**Test database**:
```python
from src.database_operations import db
print(db.init_schema())  # ✓ if working
```

---

## You're Ready! 🎉

```bash
cd ~/Desktop/ai-resume-optimizer
ollama serve  # Terminal 1
ollama pull mistral  # Terminal 2
python3 -m streamlit run app.py  # Terminal 3
```

Visit: http://localhost:8501

Sign in → Build KB → Generate resumes → Track everything

---

**v2.0 Enterprise Edition**
Built for production. Ready to scale.
