"""
Database layer for AI Resume Optimizer v2.0
Comprehensive schema with full history and audit trail
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages all database operations with transaction support"""
    
    def __init__(self, db_path: str = config.DATABASE_URL):
        self.db_path = db_path
        self.init_schema()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_schema(self):
        """Initialize database schema on first run"""
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            # ============ USERS TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # ============ KNOWLEDGE BASE TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    kb_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    master_resume TEXT NOT NULL,
                    resume_hash TEXT,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                    UNIQUE(user_id, version)
                )
            ''')
            
            # ============ EXTRACTED METRICS TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS kb_metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kb_id INTEGER NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value TEXT NOT NULL,
                    metric_context TEXT,
                    raw_text TEXT,
                    confidence REAL DEFAULT 0.95,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(kb_id) REFERENCES knowledge_base(kb_id)
                )
            ''')
            
            # ============ EXTRACTED SKILLS TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS kb_skills (
                    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kb_id INTEGER NOT NULL,
                    skill_name TEXT NOT NULL,
                    skill_category TEXT NOT NULL,
                    proficiency_level TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(kb_id) REFERENCES knowledge_base(kb_id),
                    UNIQUE(kb_id, skill_name)
                )
            ''')
            
            # ============ EXTRACTED ACHIEVEMENTS TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS kb_achievements (
                    achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kb_id INTEGER NOT NULL,
                    achievement_text TEXT NOT NULL,
                    achievement_type TEXT,
                    associated_metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(kb_id) REFERENCES knowledge_base(kb_id)
                )
            ''')
            
            # ============ JOB DESCRIPTIONS TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    jd_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    jd_text TEXT NOT NULL,
                    jd_hash TEXT,
                    role_title TEXT,
                    company_name TEXT,
                    detected_role_type TEXT,
                    key_skills TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            ''')
            
            # ============ OPTIMIZED RESUMES TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS optimizations (
                    opt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    jd_id INTEGER,
                    kb_id INTEGER NOT NULL,
                    original_resume TEXT NOT NULL,
                    optimized_resume TEXT NOT NULL,
                    resume_hash TEXT,
                    original_score REAL,
                    optimized_score REAL,
                    structure_score REAL,
                    metric_count INTEGER,
                    role_type TEXT,
                    api_provider TEXT,
                    api_model TEXT,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_tokens INTEGER,
                    processing_time_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                    FOREIGN KEY(jd_id) REFERENCES job_descriptions(jd_id),
                    FOREIGN KEY(kb_id) REFERENCES knowledge_base(kb_id)
                )
            ''')
            
            # ============ OPTIMIZATION METRICS USED TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS optimization_metrics_used (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opt_id INTEGER NOT NULL,
                    metric_id INTEGER NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(opt_id) REFERENCES optimizations(opt_id),
                    FOREIGN KEY(metric_id) REFERENCES kb_metrics(metric_id)
                )
            ''')
            
            # ============ API CALLS LOG TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS api_calls_log (
                    call_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    api_provider TEXT NOT NULL,
                    api_model TEXT NOT NULL,
                    request_type TEXT,
                    request_tokens INTEGER,
                    response_tokens INTEGER,
                    total_tokens INTEGER,
                    response_time_ms INTEGER,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            ''')
            
            # ============ AUDIT LOG TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    entity_type TEXT,
                    entity_id INTEGER,
                    old_value TEXT,
                    new_value TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            ''')
            
            # ============ SYSTEM SETTINGS TABLE ============
            c.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing schema: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # ============ USER OPERATIONS ============
    def create_user(self, username: str, email: Optional[str] = None) -> int:
        """Create new user"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO users (username, email) VALUES (?, ?)
            ''', (username, email))
            conn.commit()
            user_id = c.lastrowid
            self.log_audit(user_id, "user_created", "users", user_id)
            logger.info(f"User created: {username} (ID: {user_id})")
            return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"Username already exists: {username}")
            raise ValueError(f"Username '{username}' already taken")
        finally:
            conn.close()
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
        result = c.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ? AND is_active = 1', (user_id,))
        result = c.fetchone()
        conn.close()
        return dict(result) if result else None
    
    # ============ KNOWLEDGE BASE OPERATIONS ============
    def save_knowledge_base(self, user_id: int, master_resume: str,
                            metrics: List[Dict], skills: Dict[str, List],
                            achievements: List[str],
                            contact: Dict = None, education: List = None,
                            certifications: List[str] = None) -> int:
        """Save knowledge base with extracted data"""
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            resume_hash = hashlib.sha256(master_resume.encode()).hexdigest()

            # Deactivate any existing KB for this user
            c.execute('''
                UPDATE knowledge_base SET is_active = 0 WHERE user_id = ?
            ''', (user_id,))

            # Get next version number for this user
            c.execute('''
                SELECT COALESCE(MAX(version), 0) + 1 FROM knowledge_base WHERE user_id = ?
            ''', (user_id,))
            next_version = c.fetchone()[0]

            c.execute('''
                INSERT INTO knowledge_base (user_id, master_resume, resume_hash, version)
                VALUES (?, ?, ?, ?)
            ''', (user_id, master_resume, resume_hash, next_version))
            
            kb_id = c.lastrowid
            
            # Insert metrics
            for metric in metrics:
                c.execute('''
                    INSERT INTO kb_metrics (kb_id, metric_type, metric_value, raw_text)
                    VALUES (?, ?, ?, ?)
                ''', (kb_id, metric.get('type', 'unknown'), 
                     str(metric.get('value')), metric.get('raw_text', '')))
            
            # Insert skills
            for category, skill_list in skills.items():
                for skill in skill_list:
                    c.execute('''
                        INSERT OR IGNORE INTO kb_skills (kb_id, skill_name, skill_category)
                        VALUES (?, ?, ?)
                    ''', (kb_id, skill, category))
            
            # Insert achievements
            for achievement in achievements:
                c.execute('''
                    INSERT INTO kb_achievements (kb_id, achievement_text)
                    VALUES (?, ?)
                ''', (kb_id, achievement))

            # Store contact, education, certifications as JSON in system_settings
            # keyed by kb_id so they travel with the KB record
            if contact:
                c.execute('''
                    INSERT OR REPLACE INTO system_settings (setting_key, setting_value, description)
                    VALUES (?, ?, ?)
                ''', (f'kb_{kb_id}_contact', json.dumps(contact), 'Extracted contact info'))
            if education:
                c.execute('''
                    INSERT OR REPLACE INTO system_settings (setting_key, setting_value, description)
                    VALUES (?, ?, ?)
                ''', (f'kb_{kb_id}_education', json.dumps(education), 'Extracted education'))
            if certifications:
                c.execute('''
                    INSERT OR REPLACE INTO system_settings (setting_key, setting_value, description)
                    VALUES (?, ?, ?)
                ''', (f'kb_{kb_id}_certs', json.dumps(certifications), 'Extracted certifications'))

            conn.commit()
            self.log_audit(user_id, "kb_created", "knowledge_base", kb_id)
            logger.info(f"Knowledge base saved for user {user_id} (KB ID: {kb_id})")
            return kb_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving KB: {e}")
            raise
        finally:
            conn.close()
    
    def get_knowledge_base(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get active knowledge base for user"""
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                SELECT kb_id, master_resume FROM knowledge_base 
                WHERE user_id = ? AND is_active = 1 
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id,))
            
            kb_result = c.fetchone()
            if not kb_result:
                return None
            
            kb_id = kb_result['kb_id']
            
            # Get metrics
            c.execute('''
                SELECT * FROM kb_metrics WHERE kb_id = ? 
                ORDER BY created_at DESC
            ''', (kb_id,))
            metrics = [dict(row) for row in c.fetchall()]
            
            # Get skills
            c.execute('''
                SELECT skill_category, GROUP_CONCAT(skill_name, ', ') as skills 
                FROM kb_skills WHERE kb_id = ? 
                GROUP BY skill_category
            ''', (kb_id,))
            skills = {row['skill_category']: row['skills'].split(', ') 
                     for row in c.fetchall()}
            
            # Get achievements
            c.execute('''
                SELECT achievement_text FROM kb_achievements WHERE kb_id = ? 
                ORDER BY created_at DESC
            ''', (kb_id,))
            achievements = [row['achievement_text'] for row in c.fetchall()]
            
            # Retrieve contact / education / certs stored in system_settings
            def _get_setting(key):
                c.execute('SELECT setting_value FROM system_settings WHERE setting_key = ?', (key,))
                row = c.fetchone()
                return json.loads(row['setting_value']) if row else None

            contact      = _get_setting(f'kb_{kb_id}_contact') or {}
            education    = _get_setting(f'kb_{kb_id}_education') or []
            certifications = _get_setting(f'kb_{kb_id}_certs') or []

            return {
                'kb_id': kb_id,
                'master_resume': kb_result['master_resume'],
                'metrics': metrics,
                'skills': skills,
                'achievements': achievements,
                'contact': contact,
                'education': education,
                'certifications': certifications,
            }
        finally:
            conn.close()
    
    # ============ OPTIMIZATION OPERATIONS ============
    def save_optimization(self, user_id: int, jd_id: int, kb_id: int,
                         original_resume: str, optimized_resume: str,
                         original_score: float, optimized_score: float,
                         role_type: str, api_provider: str, api_model: str,
                         metrics_used: List[int], processing_time_ms: int = 0) -> int:
        """Save optimization result"""
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            resume_hash = hashlib.sha256(optimized_resume.encode()).hexdigest()
            
            c.execute('''
                INSERT INTO optimizations 
                (user_id, jd_id, kb_id, original_resume, optimized_resume, 
                 resume_hash, original_score, optimized_score, 
                 metric_count, role_type, api_provider, api_model, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, jd_id, kb_id, original_resume, optimized_resume,
                 str(resume_hash), original_score, optimized_score,
                 len(metrics_used), role_type, api_provider, api_model, processing_time_ms))
            
            opt_id = c.lastrowid
            
            # Record which metrics were used
            for metric_id in metrics_used:
                c.execute('''
                    INSERT INTO optimization_metrics_used (opt_id, metric_id)
                    VALUES (?, ?)
                ''', (opt_id, metric_id))
            
            conn.commit()
            self.log_audit(user_id, "optimization_created", "optimizations", opt_id)
            logger.info(f"Optimization saved (ID: {opt_id}) for user {user_id}")
            return opt_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving optimization: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_optimizations(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get optimization history for user"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''
            SELECT opt_id, original_score, optimized_score, role_type, 
                   api_provider, metric_count, created_at 
            FROM optimizations 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        results = [dict(row) for row in c.fetchall()]
        conn.close()
        return results
    
    # ============ API LOGGING ============
    def log_api_call(self, user_id: int, api_provider: str, api_model: str,
                    request_tokens: int, response_tokens: int, 
                    response_time_ms: int, success: bool = True,
                    error_message: str = None):
        """Log API call for analytics"""
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO api_calls_log 
                (user_id, api_provider, api_model, request_tokens, response_tokens,
                 total_tokens, response_time_ms, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, api_provider, api_model, request_tokens, response_tokens,
                 request_tokens + response_tokens, response_time_ms, success, error_message))
            
            conn.commit()
        finally:
            conn.close()
    
    # ============ AUDIT LOGGING ============
    def log_audit(self, user_id: int, action: str, entity_type: str = None,
                 entity_id: int = None, old_value: str = None, new_value: str = None):
        """Log action to audit trail"""
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO audit_log 
                (user_id, action, entity_type, entity_id, old_value, new_value)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, action, entity_type, entity_id, old_value, new_value))
            
            conn.commit()
            logger.info(f"Audit log: {action} by user {user_id}")
        finally:
            conn.close()
    
    # ============ ANALYTICS ============
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        conn = self.get_connection()
        c = conn.cursor()
        
        stats = {}
        
        # Total optimizations
        c.execute('SELECT COUNT(*) as count FROM optimizations WHERE user_id = ?', (user_id,))
        stats['total_optimizations'] = c.fetchone()['count']
        
        # Average score improvement
        c.execute('''
            SELECT AVG(optimized_score - original_score) as avg_gain 
            FROM optimizations WHERE user_id = ?
        ''', (user_id,))
        result = c.fetchone()['avg_gain']
        stats['avg_score_gain'] = round(result, 1) if result else 0
        
        # Best score
        c.execute('''
            SELECT MAX(optimized_score) as best_score 
            FROM optimizations WHERE user_id = ?
        ''', (user_id,))
        stats['best_score'] = c.fetchone()['best_score'] or 0
        
        # KB versions
        c.execute('SELECT COUNT(*) as count FROM knowledge_base WHERE user_id = ?', (user_id,))
        stats['kb_versions'] = c.fetchone()['count']
        
        conn.close()
        return stats

# Create global database instance
db = DatabaseManager()

if __name__ == "__main__":
    # Test database initialization
    test_db = DatabaseManager()
    print("✓ Database initialized successfully")
