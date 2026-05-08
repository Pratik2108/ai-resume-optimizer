# AI Resume Optimizer v2.0 - Enterprise Edition

**Production-Grade Resume Optimization System with Knowledge Base, Smart Remixing, and Full History Tracking**

---

## 🎯 Features

✅ **Knowledge Base Mode** — Extract and store all real metrics from your resume  
✅ **Smart Remixing** — AI remixes metrics for role-specific resumes  
✅ **Rich Architecture** — Clean, modular, production-grade code  
✅ **Comprehensive Database** — Full schema with versioning and audit trail  
✅ **Complete History** — Track all optimizations, metrics, API calls, and actions  
✅ **Multi-API Support** — Ollama (local), Gemini, OpenAI  
✅ **Professional Logging** — Full audit trail and error tracking  
✅ **File Organization** — Clean folder structure with data, logs, and exports  

---

## 📁 Project Structure

```
ai-resume-optimizer/
├── app.py                          # Main entry point
├── config.py                       # Configuration management
├── requirements.txt                # Dependencies
│
├── src/
│   ├── database_operations.py      # Database layer (CRUD, schemas, migrations)
│   ├── extraction_engines.py       # Metrics/skills/achievements extraction
│   ├── optimization_engines.py     # Role detection, remixing, scoring
│   └── api_clients.py              # LLM client wrappers (Ollama, Gemini, OpenAI)
│
├── data/
│   ├── resume_optimizer_v2.db      # SQLite database
│   ├── backups/                    # Automatic backups
│   └── exports/                    # Generated resumes
│
└── logs/
    └── app.log                     # Application logs
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
cd ~/Desktop
git clone https://github.com/Pratik2108/ai-resume-optimizer
cd ai-resume-optimizer
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Setup Ollama (Local Free LLM)

**Terminal 1:**
```bash
ollama serve
```

**Terminal 2:**
```bash
ollama pull mistral
# Or: ollama pull llama2, ollama pull neural-chat
```

### 4. Run Application

**Terminal 3:**
```bash
python3 -m streamlit run app.py
```

Opens at: `http://localhost:8501`

---

## 📊 Database Schema

### Tables

| Table | Purpose |
|-------|---------|
| `users` | User profiles and authentication |
| `knowledge_base` | Master resumes with versioning |
| `kb_metrics` | Extracted metrics with confidence scores |
| `kb_skills` | Extracted skills by category |
| `kb_achievements` | Extracted achievements and accomplishments |
| `job_descriptions` | Stored JDs with role detection |
| `optimizations` | Generated resumes with scores |
| `optimization_metrics_used` | Tracking which metrics were used in each resume |
| `api_calls_log` | API usage analytics |
| `audit_log` | Complete audit trail of all actions |

### Key Features

- **Versioning** — Track KB changes over time
- **Audit Trail** — Every action logged with user, timestamp, entity
- **API Analytics** — Track token usage, response times, success rates
- **Metric Tracking** — Know exactly which metrics were used in each resume
- **Transaction Support** — Database rollback on errors

---

## 💻 How to Use

### Step 1: Create Knowledge Base (One Time)

1. Go to "📚 Knowledge Base" tab
2. Paste your **best resume** (copy from one of your PDFs)
3. Click "💾 Save Knowledge Base"
4. System extracts:
   - Real metrics (124.53%, 4.62 → 4.72, etc.)
   - Skills (technical, domain, soft)
   - Achievements (with real context)

### Step 2: Optimize for Any JD (1 Minute Each)

1. Go to "✏️ Optimize" tab
2. Paste any job description
3. Click "🚀 Generate Optimized Resume"
4. System:
   - Detects role type (Functional/Technical/Senior)
   - Remixes YOUR real metrics
   - Creates narrative using verified facts
   - Scores resume across 5 dimensions
5. Download as text

### Step 3: Review History

- Go to "📊 History" tab
- See all optimizations with scores
- Track which JDs you've applied for
- View API usage statistics

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Database location
DATABASE_URL = "path/to/database.db"

# API settings
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_DEFAULT_MODEL = "mistral"

# Resume settings
MIN_RESUME_WORD_COUNT = 200
TARGET_RESUME_WORD_COUNT = 600

# Scoring weights
SCORING_WEIGHTS = {
    'real_metrics': 0.40,
    'structure': 0.20,
    'word_count': 0.15,
    'skill_match': 0.15,
    'role_alignment': 0.10,
}
```

---

## 📝 Logging

Application logs stored in `logs/app.log`

Log levels: INFO, DEBUG, WARNING, ERROR

Check logs for:
- Knowledge base extraction results
- Optimization history
- API call metrics
- Error diagnostics
- Audit trail

```bash
tail -f logs/app.log        # Watch real-time logs
cat logs/app.log | grep ERROR  # View errors
```

---

## 🔌 API Providers

### Ollama (Recommended for Development)

- **Cost**: Free
- **Speed**: Slow (local CPU)
- **Quality**: Good (Mistral model)
- **Setup**: `ollama serve` + `ollama pull mistral`
- **Pros**: No quotas, offline, free
- **Cons**: Slower than cloud APIs

### Gemini (Free Tier)

- **Cost**: Free tier + quota limits
- **Speed**: Fast
- **Quality**: Excellent
- **Setup**: Get API key from https://aistudio.google.com/app/apikeys
- **Pros**: High quality, fast
- **Cons**: Has quota limits

### OpenAI (Paid)

- **Cost**: $0.001-0.01 per request
- **Speed**: Very fast
- **Quality**: Highest
- **Setup**: Get API key from https://platform.openai.com/api-keys
- **Pros**: Fastest, highest quality
- **Cons**: Requires payment

---

## 📊 Database Backup

Backups stored in `data/backups/`

Automatic backup created on each KB save.

Manual backup:
```bash
cp data/resume_optimizer_v2.db data/backups/backup_$(date +%Y-%m-%d).db
```

---

## 🧪 Testing

Check database initialization:
```bash
python3 src/database_operations.py
# Should output: ✓ Database initialized successfully
```

Check metric extraction:
```bash
python3 src/extraction_engines.py
# Should show extracted metrics, skills, achievements
```

Check LLM clients:
```python
from src.api_clients import OllamaClient
ollama = OllamaClient()
print(ollama.is_available())  # True if Ollama is running
```

---

## 🚀 Deployment to Streamlit Cloud

1. Push to GitHub:
```bash
git add .
git commit -m "v2.0: Enterprise edition with full database"
git push
```

2. Visit https://share.streamlit.io
3. Click "Deploy an app"
4. Select `Pratik2108/ai-resume-optimizer` repo
5. Set main file: `app.py`
6. Click Deploy
7. Add secrets in Advanced Settings:
   ```
   GEMINI_API_KEY = "your-key"
   OPENAI_API_KEY = "your-key"
   ```

**Note**: Ollama won't work on Streamlit Cloud (no local GPU). Use Gemini or OpenAI.

---

## 📈 Key Metrics

The system tracks:

- **Optimization Quality**: Multi-dimensional scoring (real metrics, structure, word count, skill match, role alignment)
- **API Performance**: Response time, token usage, success rate
- **User Activity**: Optimizations count, KB versions, best scores
- **Metric Usage**: Which metrics are used most frequently
- **Role Distribution**: What roles you're targeting

Access via "📊 History" tab.

---

## 🛠️ Development

### Adding a New Skill Category

Edit `config.py`:
```python
SKILL_CATEGORIES = {
    'new_category': ['skill1', 'skill2', ...],
    ...
}
```

### Adding a New Metric Pattern

Edit `src/extraction_engines.py`:
```python
def _build_patterns(self):
    return {
        'new_pattern': r'your-regex-here',
        ...
    }
```

### Adding a New API Provider

Create client in `src/api_clients.py`:
```python
class NewProviderClient(BaseLLMClient):
    def generate(self, prompt, max_tokens=1500):
        # Implementation
        pass
    
    def get_model_info(self):
        # Implementation
        pass
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama not running" | `ollama serve` in terminal |
| "Database locked" | Restart app (only one Streamlit instance) |
| "API timeout" | Increase timeout in config.py |
| "No metrics extracted" | Check resume format; ensure metrics are visible |
| "Empty optimized resume" | Check API provider is working; check logs |

---

## 📚 Documentation

- **DATABASE_SCHEMA.md** — Detailed schema documentation
- **API_REFERENCE.md** — API client documentation
- **DEVELOPMENT.md** — Developer guide

---

## 📞 Support

Check logs: `logs/app.log`

Common issues resolved in logs.

---

## 📄 License

Open source. Free to use and modify.

---

## 🎯 Roadmap

**v2.1** — PDF/DOCX export
**v2.2** — LinkedIn parser integration
**v2.3** — Multi-language support
**v3.0** — Advanced AI recommendations

---

## 📧 Feedback

Built for Pratik Teredesai's job search strategy.

Designed for production-grade resume optimization.

Clean code. Full history. Real metrics.
