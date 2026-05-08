# AI Resume Optimizer v2.0 - Installation Guide

## 📦 Quick Setup (5 Minutes)

### 1. Extract ZIP
```bash
unzip ai-resume-optimizer-v2.zip
cd ai-resume-optimizer-v2
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Start Ollama (in separate terminal)
```bash
ollama serve
```

In another terminal:
```bash
ollama pull mistral
```

### 4. Run Application
```bash
python3 -m streamlit run app.py
```

Visit: http://localhost:8501

---

## 📚 Documentation

- **QUICK_START.md** — 5-minute quick start guide
- **README.md** — Complete setup and reference  
- **ARCHITECTURE.md** — System design and features
- **STRUCTURE.txt** — Folder organization

---

## 🗂️ Folder Structure

```
ai-resume-optimizer-v2/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration (edit as needed)
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
│
├── src/                  # Python modules
│   ├── __init__.py
│   ├── database_operations.py      # Database layer
│   ├── extraction_engines.py       # Metrics/skills extraction
│   ├── optimization_engines.py     # Role detection, scoring
│   └── api_clients.py              # LLM integrations
│
├── data/                 # Data folder (auto-created on first run)
│   ├── resume_optimizer_v2.db      # SQLite database
│   ├── backups/                    # Database backups
│   └── exports/                    # Generated resumes
│
├── logs/                 # Logs folder (auto-created on first run)
│   └── app.log                     # Application logs
│
└── Documentation/
    ├── QUICK_START.md              # Quick start guide
    ├── README.md                   # Full documentation
    ├── ARCHITECTURE.md             # System architecture
    └── STRUCTURE.txt               # File organization
```

---

## ✅ Verification

After setup, verify everything works:

```bash
# 1. Test database initialization
python3 -c "from src.database_operations import db; print('✓ Database OK')"

# 2. Test extraction
python3 -c "from src.extraction_engines import analyze_resume; print('✓ Extraction OK')"

# 3. Test API client
python3 -c "from src.api_clients import OllamaClient; print('✓ API Client OK')"

# 4. Run app
python3 -m streamlit run app.py
```

---

## 🐛 Troubleshooting

**"Ollama not running"**
```bash
ollama serve  # Start in separate terminal
```

**"Module not found"**
```bash
# Ensure you're in the right directory:
cd ai-resume-optimizer-v2
python3 -m streamlit run app.py  # Note: use python3 -m
```

**"Database error"**
```bash
# Remove old database and restart:
rm -f data/resume_optimizer_v2.db
python3 -m streamlit run app.py
```

**"Port already in use"**
```bash
python3 -m streamlit run app.py --server.port 8502
```

---

## 🚀 First Use

1. **Sign In** (sidebar) → Create account
2. **Build KB** (📚 tab) → Paste your best resume
3. **Optimize** (✏️ tab) → Paste any JD, click Generate
4. **Review** (📊 tab) → See history and scores

---

## 📞 Support

Check logs for any errors:
```bash
cat logs/app.log
```

Most issues are solved by:
1. Restarting Ollama (`ollama serve`)
2. Reinstalling dependencies (`pip3 install -r requirements.txt`)
3. Clearing database (`rm data/resume_optimizer_v2.db`)

---

**Ready to optimize!** 🎉
