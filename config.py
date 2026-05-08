"""
Configuration management for AI Resume Optimizer v2.0
Handles environment variables, paths, and application settings
"""

import os
from pathlib import Path
from enum import Enum

from dotenv import load_dotenv
load_dotenv()

# ============ PATHS ============
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
BACKUP_DIR = DATA_DIR / "backups"
EXPORT_DIR = DATA_DIR / "exports"

# Create directories if they don't exist
for directory in [DATA_DIR, LOG_DIR, BACKUP_DIR, EXPORT_DIR, EXPORT_DIR / "optimized", EXPORT_DIR / "pdf"]:
    directory.mkdir(parents=True, exist_ok=True)

# ============ DATABASE ============
DATABASE_URL = str(DATA_DIR / "resume_optimizer_v2.db")
DATABASE_BACKUP_RETENTION = 30  # days

# ============ API CONFIGURATION ============
class APIProvider(str, Enum):
    OLLAMA = "ollama"
    GEMINI = "gemini"
    OPENAI = "openai"
    GROK = "grok"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_TIMEOUT = 90

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

XAI_API_KEY = os.getenv("XAI_API_KEY", "")
GROK_BASE_URL = "https://api.x.ai/v1"
GROK_MODEL = os.getenv("GROK_MODEL", "grok-3-beta")

# ============ LOGGING ============
LOG_FILE = LOG_DIR / "app.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5

# ============ EXTRACTION SETTINGS ============
METRICS_EXTRACTION = {
    "enable_percentage": True,
    "enable_counts": True,
    "enable_growth": True,
    "enable_time_qualified": True,
}

SKILL_CATEGORIES = {
    "technical": [
        # ERP / NetSuite ecosystem
        "netsuite", "suitescript", "suiteflow", "suitebuild", "suiteta",
        "suiteanaly", "suitetalk", "suitecommerce", "openair",
        # Integration & API
        "rest", "soap", "graphql", "api", "webhook", "etl", "xml", "json",
        # Languages & scripting
        "python", "javascript", "typescript", "sql", "bash", "powershell",
        # Data & BI
        "power bi", "tableau", "looker", "excel", "google sheets", "dbt",
        # Cloud & DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
        # Collaboration tools
        "git", "github", "jira", "confluence", "asana", "monday", "notion",
        # Other platforms
        "salesforce", "sap", "oracle", "workday", "hubspot", "zendesk",
    ],
    "domain": [
        "erp", "ecommerce", "crm", "order-to-cash", "procure-to-pay",
        "general ledger", "accounts payable", "accounts receivable",
        "inventory management", "supply chain", "financial reporting",
        "accounting", "revenue recognition", "fixed assets", "payroll",
        "warehouse management", "demand planning", "procurement",
        "business intelligence", "data analytics", "digital transformation",
        "system integration", "change management", "business process",
    ],
    "soft": [
        "leadership", "project management", "communication", "stakeholder management",
        "facilitation", "analytical thinking", "problem-solving", "collaboration",
        "mentoring", "strategic planning", "cross-functional", "client-facing",
        "presentations", "requirement gathering", "documentation", "training",
        "agile", "scrum", "waterfall", "pmo",
    ],
}

# ============ OPTIMIZATION SETTINGS ============
MIN_RESUME_WORD_COUNT = 200
TARGET_RESUME_WORD_COUNT = 600
MAX_RESUME_WORD_COUNT = 2000

ROLE_TYPES = ["Functional", "Technical", "Senior", "Consultant"]

# Resume scoring weights
SCORING_WEIGHTS = {
    "real_metrics": 0.40,
    "structure": 0.20,
    "word_count": 0.15,
    "skill_match": 0.15,
    "role_alignment": 0.10,
}

# ============ UI SETTINGS ============
STREAMLIT_CONFIG = {
    "page_title": "AI Resume Optimizer v2.0",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# ============ DATA RETENTION ============
OPTIMIZATION_HISTORY_RETENTION = 365  # days
KB_VERSIONS_TO_KEEP = 10

# ============ FEATURE FLAGS ============
FEATURES = {
    "knowledge_base": True,
    "smart_remixing": True,
    "role_detection": True,
    "audit_logging": True,
    "backup_automation": True,
    "export_pdf": False,  # Coming in v2.1
    "export_docx": False,  # Coming in v2.1
}

# ============ VALIDATION ============
VALIDATION_RULES = {
    "min_username_length": 2,
    "max_username_length": 50,
    "min_resume_length": 100,
    "max_resume_length": 50000,
    "min_jd_length": 100,
    "max_jd_length": 10000,
}

# ============ ERROR MESSAGES ============
ERRORS = {
    "db_connection": "Database connection failed. Check configuration.",
    "api_timeout": "API request timed out. Try again.",
    "invalid_input": "Invalid input provided. Check and try again.",
    "kb_not_found": "Knowledge Base not found. Create one first.",
    "extraction_failed": "Failed to extract data. Check resume format.",
}

# ============ ATS RESUME SETTINGS ============
ATS_RESUME_SECTIONS = [
    "PROFESSIONAL SUMMARY",
    "CORE COMPETENCIES",
    "PROFESSIONAL EXPERIENCE",
    "KEY ACHIEVEMENTS",
    "TECHNICAL SKILLS",
    "EDUCATION",
    "CERTIFICATIONS",
]

ATS_MAX_TOKENS = 2500

if __name__ == "__main__":
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"DATABASE_URL: {DATABASE_URL}")
    print(f"LOG_FILE: {LOG_FILE}")
