"""
Data extraction engines for resume analysis.
Extracts metrics, skills, achievements, contact info, education, and certifications.
"""

import re
from typing import List, Dict, Any, Optional
from collections import defaultdict
import logging

import config

logger = logging.getLogger(__name__)


class MetricsExtractor:
    """Extract quantified metrics from resume text."""

    def __init__(self):
        self.patterns = self._build_patterns()

    def _build_patterns(self) -> Dict[str, str]:
        return {
            'percentage_range':    r'(\d+\.?\d*)\s*%\s*to\s*(\d+\.?\d*)\s*%',
            'percentage_achieved': r'(\d+\.?\d*)\s*%\s*(?:increase|improvement|growth|completion|resolution|achievement|accuracy|retention|adoption|reduction|savings|efficiency)',
            'percentage_value':    r'(?:from|reach|achieve|hit|exceed)\s+(\d+\.?\d*)\s*%',
            'growth_metrics':      r'(?:grew|growth|improved|increased|rose|jumped)\s+(?:from\s+)?(\d+\.?\d*)\s*%?\s+to\s+(\d+\.?\d*)\s*%?',
            'count_metrics':       r'(\d{1,4}(?:,\d{3})*|\d+)\s+(?:cases?|issues?|comments?|answers?|badges?|projects?|clients?|implementations?|users?|employees?|team members?|stakeholders?|modules?|integrations?|endpoints?|tickets?)',
            'time_qualified':      r'(\d+\.?\d*)\s*%\s+(?:in|during|for|over)\s+(FY\d+\s*Q\d|Q\d\s+\d{4}|[A-Za-z]+\s+\d{4}|[Hh]\d\s+\d{4}|\d{4})',
            'currency':            r'(\$[\d,.]+\s*[MKBmkb]?\s*(?:million|billion|thousand)?)',
            'time_savings':        r'(\d+\.?\d*)\s*(?:hours?|days?|weeks?|months?)\s+(?:saved|reduced|cut|faster)',
            'ratio':               r'(\d+\.?\d*)\s*:\s*(\d+\.?\d*)',
            'multiplier':          r'(\d+\.?\d*)x\s+(?:faster|more|better|improvement|increase)',
        }

    def extract(self, text: str) -> List[Dict[str, Any]]:
        metrics = []
        for pattern_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                metrics.append({
                    'type': pattern_type,
                    'value': match.groups() if len(match.groups()) > 1 else match.group(1),
                    'raw_text': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                })
        logger.info(f"Extracted {len(metrics)} raw metrics")
        return self._deduplicate(metrics)

    def _deduplicate(self, metrics: List[Dict]) -> List[Dict]:
        seen, unique = set(), []
        for m in sorted(metrics, key=lambda x: x['start']):
            key = (m['type'], str(m['value']))
            if key not in seen:
                seen.add(key)
                unique.append(m)
        return unique


class SkillsExtractor:
    """Extract and categorise skills from resume text."""

    def __init__(self):
        self.skill_db = config.SKILL_CATEGORIES

    def extract(self, text: str) -> Dict[str, List[str]]:
        skills: Dict[str, List[str]] = defaultdict(list)
        text_lower = text.lower()
        for category, skill_list in self.skill_db.items():
            for skill in skill_list:
                if re.search(rf'\b{re.escape(skill.lower())}\b', text_lower):
                    skills[category].append(skill)
        logger.info(f"Extracted skills: { {k: len(v) for k,v in skills.items()} }")
        return dict(skills)

    def get_missing_skills(self, resume_skills: Dict[str, List[str]],
                           jd_skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
        missing: Dict[str, List[str]] = defaultdict(list)
        for cat, jd_list in jd_skills.items():
            resume_list = [s.lower() for s in resume_skills.get(cat, [])]
            missing[cat] = [s for s in jd_list if s.lower() not in resume_list]
        return {k: v for k, v in missing.items() if v}


class AchievementsExtractor:
    """Extract achievement statements from resume text."""

    VERBS = [
        'led', 'owned', 'drove', 'managed', 'developed', 'built', 'launched',
        'delivered', 'spearheaded', 'achieved', 'completed', 'resulted in',
        'increased', 'improved', 'reduced', 'optimized', 'streamlined',
        'coordinated', 'directed', 'oversaw', 'orchestrated', 'designed',
        'implemented', 'deployed', 'migrated', 'transformed', 'automated',
        'established', 'created', 'trained', 'mentored', 'negotiated',
        'saved', 'generated', 'secured', 'expanded', 'grew', 'scaled',
    ]

    def extract(self, text: str) -> List[str]:
        achievements = []
        for line in text.split('\n'):
            line = line.strip()
            if not line or len(line) < 20:
                continue
            line_lower = line.lower()
            if any(verb in line_lower for verb in self.VERBS):
                cleaned = re.sub(r'^[•\-\*•‣◦]\s+', '', line).strip()
                if 20 < len(cleaned) < 500:
                    achievements.append(cleaned)
        logger.info(f"Extracted {len(achievements)} achievements")
        return achievements[:20]


class ContactExtractor:
    """Extract contact information from resume header."""

    EMAIL_RE    = re.compile(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}')
    PHONE_RE    = re.compile(r'(?:\+?\d[\d\s\-().]{7,}\d)')
    LINKEDIN_RE = re.compile(r'linkedin\.com/in/[\w\-]+', re.IGNORECASE)
    GITHUB_RE   = re.compile(r'github\.com/[\w\-]+', re.IGNORECASE)

    def extract(self, text: str) -> Dict[str, str]:
        first_300 = text[:300]
        contact: Dict[str, str] = {}

        email = self.EMAIL_RE.search(first_300)
        if email:
            contact['email'] = email.group()

        phone = self.PHONE_RE.search(first_300)
        if phone:
            contact['phone'] = phone.group().strip()

        linkedin = self.LINKEDIN_RE.search(text)
        if linkedin:
            contact['linkedin'] = linkedin.group()

        github = self.GITHUB_RE.search(text)
        if github:
            contact['github'] = github.group()

        # Attempt name: first non-empty line that looks like a name
        for line in text.split('\n')[:5]:
            line = line.strip()
            if line and not self.EMAIL_RE.search(line) and not self.PHONE_RE.search(line):
                if len(line.split()) <= 5 and re.match(r'^[A-Z][a-zA-Z\s.]+$', line):
                    contact['name'] = line
                    break

        return contact


class EducationExtractor:
    """Extract education entries from resume text."""

    DEGREE_PATTERNS = [
        r'\b(Bachelor(?:\'s)?(?:\s+of\s+[\w\s]+)?|B\.?[SA]\.?\s*(?:in\s+[\w\s]+)?)',
        r'\b(Master(?:\'s)?(?:\s+of\s+[\w\s]+)?|M\.?[SA]\.?\s*(?:in\s+[\w\s]+)?|MBA)',
        r'\b(Ph\.?D\.?(?:\s+in\s+[\w\s]+)?|Doctorate)',
        r'\b(Associate(?:\'s)?(?:\s+of\s+[\w\s]+)?)',
        r'\b(Diploma(?:\s+in\s+[\w\s]+)?)',
    ]

    YEAR_RE = re.compile(r'\b((?:19|20)\d{2})\b')

    def extract(self, text: str) -> List[Dict[str, str]]:
        entries = []
        lines = text.split('\n')
        for i, line in enumerate(lines):
            for pat in self.DEGREE_PATTERNS:
                match = re.search(pat, line, re.IGNORECASE)
                if match:
                    context = ' '.join(lines[max(0, i-1):i+3])
                    year_m = self.YEAR_RE.search(context)
                    entries.append({
                        'degree': match.group(1).strip(),
                        'raw_line': line.strip(),
                        'year': year_m.group(1) if year_m else '',
                    })
                    break
        return entries


class CertificationExtractor:
    """Extract professional certifications from resume text."""

    CERT_KEYWORDS = [
        'certified', 'certification', 'certificate', 'professional',
        'associate', 'specialist', 'accredited',
    ]

    KNOWN_CERTS = [
        'pmp', 'capm', 'aws certified', 'azure', 'google cloud', 'gcp',
        'cpa', 'cfa', 'cissp', 'ceh', 'comptia', 'oracle certified',
        'netsuite certified', 'salesforce certified', 'scrum master',
        'csm', 'safe', 'itil', 'togaf', 'six sigma', 'lean',
        'prince2', 'cobit', 'cism', 'cisa',
    ]

    def extract(self, text: str) -> List[str]:
        certs = []
        text_lower = text.lower()

        # Match known cert names
        for cert in self.KNOWN_CERTS:
            if cert in text_lower:
                start = text_lower.index(cert)
                snippet = text[max(0, start-10):start+80].strip()
                snippet = re.sub(r'^[•\-\*]\s*', '', snippet)
                if snippet not in certs:
                    certs.append(snippet)

        # Match lines containing certification keywords
        for line in text.split('\n'):
            line_strip = line.strip()
            if not line_strip or len(line_strip) < 10:
                continue
            line_lower = line_strip.lower()
            if any(kw in line_lower for kw in self.CERT_KEYWORDS):
                cleaned = re.sub(r'^[•\-\*]\s*', '', line_strip)
                if cleaned not in certs and len(cleaned) < 200:
                    certs.append(cleaned)

        return list(dict.fromkeys(certs))[:10]  # dedup, max 10


class ResumeAnalyzer:
    """Unified resume analysis — single call returns everything."""

    def __init__(self):
        self.metrics_ex      = MetricsExtractor()
        self.skills_ex       = SkillsExtractor()
        self.achievements_ex = AchievementsExtractor()
        self.contact_ex      = ContactExtractor()
        self.education_ex    = EducationExtractor()
        self.certs_ex        = CertificationExtractor()

    def analyze(self, resume_text: str) -> Dict[str, Any]:
        return {
            'metrics':       self.metrics_ex.extract(resume_text),
            'skills':        self.skills_ex.extract(resume_text),
            'achievements':  self.achievements_ex.extract(resume_text),
            'contact':       self.contact_ex.extract(resume_text),
            'education':     self.education_ex.extract(resume_text),
            'certifications': self.certs_ex.extract(resume_text),
            'word_count':    len(resume_text.split()),
            'char_count':    len(resume_text),
        }

    def get_summary(self, resume_text: str) -> Dict[str, Any]:
        a = self.analyze(resume_text)
        return {
            'total_metrics':    len(a['metrics']),
            'total_skills':     sum(len(v) for v in a['skills'].values()),
            'total_achievements': len(a['achievements']),
            'has_contact':      bool(a['contact']),
            'education_count':  len(a['education']),
            'cert_count':       len(a['certifications']),
            'word_count':       a['word_count'],
        }


def analyze_resume(resume_text: str) -> Dict[str, Any]:
    return ResumeAnalyzer().analyze(resume_text)


if __name__ == "__main__":
    sample = """
    John Smith  john.smith@email.com  +1-555-0100  linkedin.com/in/johnsmith

    Led end-to-end NetSuite implementation achieving 124.53% of productivity targets in FY25 Q2.
    Improved CSAT from 4.62 to 4.72 through knowledge article ownership — 567 comments resolved.
    Reduced ticket backlog by 38% increase in first-contact resolution rate.

    Bachelor of Science in Computer Science, MIT, 2018
    PMP Certified | NetSuite Certified Administrator
    Skills: Python, SQL, NetSuite, SuiteScript, Power BI, Project Management
    """
    result = analyze_resume(sample)
    print("Metrics:",       len(result['metrics']))
    print("Skills:",        {k: len(v) for k, v in result['skills'].items()})
    print("Achievements:",  len(result['achievements']))
    print("Contact:",       result['contact'])
    print("Education:",     result['education'])
    print("Certs:",         result['certifications'])
