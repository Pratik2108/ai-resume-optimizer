"""
Resume optimization engines.
Handles role detection, JD keyword extraction, ATS-grade resume prompting, and scoring.
"""

import re
from typing import Dict, List, Any, Tuple
import logging

import config

logger = logging.getLogger(__name__)


class RoleDetector:
    """Detect the primary role type from a job description."""

    INDICATORS = {
        'Functional': [
            'functional consultant', 'business analyst', 'requirements gathering',
            'business process', 'configuration', 'workshop', 'end-user training',
            'fit-gap', 'fit/gap', 'functional design', 'uat', 'user acceptance',
            'process mapping', 'blueprint', 'business requirements document',
        ],
        'Technical': [
            'technical', 'developer', 'suitescript', 'suiteflow', 'suitebuild',
            'coding', 'api integration', 'rest api', 'soap', 'debugging',
            'scripting', 'custom development', 'integration architect',
        ],
        'Senior': [
            'senior', 'lead consultant', 'architect', 'leadership', 'mentor',
            'strategic', 'advisory', 'principal', 'director', 'head of',
            'delivery manager', 'practice lead', 'team lead', 'solution architect',
        ],
    }

    def detect(self, jd_text: str) -> str:
        jd_lower = jd_text.lower()
        scores = {role: 0 for role in config.ROLE_TYPES}
        for role, indicators in self.INDICATORS.items():
            for indicator in indicators:
                if indicator in jd_lower:
                    scores[role] += jd_lower.count(indicator)
        best = max(scores, key=scores.get)
        detected = best if scores[best] > 0 else 'Consultant'
        logger.info(f"Detected role: {detected} (scores: {scores})")
        return detected

    def get_focus_areas(self, jd_text: str) -> List[str]:
        jd_lower = jd_text.lower()
        patterns = {
            'requirements_gathering': r'gather(?:ing)?\s+(?:business\s+)?requirements',
            'technical_development':  r'(?:technical|development|coding|scripting)',
            'leadership':             r'(?:lead|manage|mentor|oversee)\s+(?:a\s+)?team',
            'client_facing':          r'(?:client|stakeholder|executive|c-level)\s+(?:management|communication|presentation)',
            'data_analytics':         r'(?:data|analytics|reporting|dashboard|bi)',
            'testing_qa':             r'(?:test|uat|quality|qa|validation|defect)',
            'project_management':     r'(?:project management|pmo|delivery|timeline|milestone)',
        }
        return [area for area, pat in patterns.items() if re.search(pat, jd_lower)]


class JDKeywordExtractor:
    """Extract ATS-critical keywords from a job description."""

    STOPWORDS = {
        'the', 'and', 'for', 'with', 'our', 'this', 'that', 'will', 'you',
        'your', 'are', 'have', 'has', 'been', 'would', 'should', 'must',
        'from', 'into', 'able', 'about', 'also', 'both', 'each', 'most',
        'such', 'their', 'they', 'them', 'then', 'than', 'when', 'where',
        'who', 'which', 'what', 'how', 'any', 'all', 'can', 'not', 'but',
    }

    def extract(self, jd_text: str, top_n: int = 30) -> List[str]:
        """Return the most-frequent meaningful words and phrases from the JD."""
        # Single important words
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.\-]{2,}\b', jd_text)
        word_freq: Dict[str, int] = {}
        for w in words:
            w_lower = w.lower()
            if w_lower not in self.STOPWORDS and len(w_lower) > 2:
                word_freq[w_lower] = word_freq.get(w_lower, 0) + 1

        # Two-word phrases (bigrams)
        bigrams = re.findall(r'\b([a-zA-Z][a-zA-Z0-9+#.\-]+ [a-zA-Z][a-zA-Z0-9+#.\-]+)\b', jd_text)
        bigram_freq: Dict[str, int] = {}
        for bg in bigrams:
            bg_lower = bg.lower()
            parts = bg_lower.split()
            if not any(p in self.STOPWORDS for p in parts):
                bigram_freq[bg_lower] = bigram_freq.get(bg_lower, 0) + 1

        # Merge, rank by frequency, deduplicate substrings
        combined = {**word_freq, **bigram_freq}
        ranked = sorted(combined, key=combined.get, reverse=True)

        final = []
        for kw in ranked:
            if not any(kw in existing for existing in final):
                final.append(kw)
            if len(final) >= top_n:
                break

        logger.info(f"Extracted {len(final)} JD keywords")
        return final


class MetricRemixer:
    """Build a production-grade ATS resume prompt from KB data."""

    def remix(self, metrics: List[Dict], skills: Dict, achievements: List[str],
              role_type: str, jd_text: str,
              contact: Dict = None, education: List[Dict] = None,
              certifications: List[str] = None) -> str:

        kw_extractor = JDKeywordExtractor()
        jd_keywords = kw_extractor.extract(jd_text, top_n=25)

        contact      = contact      or {}
        education    = education    or []
        certifications = certifications or []

        prompt = f"""You are a senior resume writer with 15 years of experience helping professionals \
land roles at top companies. Your resumes consistently pass ATS filters and impress human reviewers.

══════════════════════════════════════════════════════════════════
CANDIDATE DATA (use ONLY this — never invent facts or numbers)
══════════════════════════════════════════════════════════════════

REAL METRICS (every number you write must appear in this list):
{self._fmt_metrics(metrics)}

SKILLS & COMPETENCIES:
{self._fmt_skills(skills)}

KEY ACHIEVEMENTS:
{self._fmt_achievements(achievements)}

EDUCATION:
{self._fmt_education(education)}

CERTIFICATIONS:
{self._fmt_certs(certifications)}

CONTACT:
{self._fmt_contact(contact)}

══════════════════════════════════════════════════════════════════
TARGET JOB DESCRIPTION (first 1 000 chars):
══════════════════════════════════════════════════════════════════
{jd_text[:1000]}

TOP JD KEYWORDS TO MIRROR EXACTLY (ATS matching — weave these in naturally):
{', '.join(jd_keywords)}

══════════════════════════════════════════════════════════════════
OUTPUT: Write a complete, ATS-optimised resume for a {role_type} role.
══════════════════════════════════════════════════════════════════

STRUCTURE — output each section using the EXACT heading shown:

[CANDIDATE NAME]
[Email] | [Phone] | [LinkedIn] | [Location]
(Use contact data above; omit any field not provided)

PROFESSIONAL SUMMARY
(3-4 sentences. Open with years of experience and role title. Weave in 2-3 JD keywords.
Include AT LEAST 2 real metrics. Close with value proposition for this specific role.)

CORE COMPETENCIES
(12-16 items in a 3-column pipe-delimited layout. Pull from skills + JD keywords.
Example: NetSuite Administration | SuiteScript 2.x | Order-to-Cash)

PROFESSIONAL EXPERIENCE
(For each role, write 4-6 bullet points. Each bullet = strong action verb + specific \
outcome + real metric where one exists. Mirror JD keywords naturally.
DO NOT fabricate company names or dates — write "Present Role" or leave employer blank \
if not in the candidate data.)

KEY ACHIEVEMENTS
(3-5 standalone achievements drawn from the achievements list. Bold the metric using \
ALL-CAPS for the number, e.g. "Achieved 124.53% of productivity targets…"
These should be your most impressive, metric-backed wins.)

TECHNICAL SKILLS
(Group by category: ERP/NetSuite | Integration & APIs | Data & Reporting | \
Project & Collaboration. Only list skills from the skills data above.)

EDUCATION
(Degree | Institution | Year — from education data only; omit if empty)

CERTIFICATIONS
(From certifications data only; omit if empty)

══════════════════════════════════════════════════════════════════
NON-NEGOTIABLE RULES:
══════════════════════════════════════════════════════════════════
1. EVERY number must come from the metrics list — zero invented statistics
2. Mirror JD keywords verbatim (exact spelling = ATS match)
3. Use strong past-tense action verbs (Led, Delivered, Drove, Optimised…)
4. No tables, no columns, no special characters outside standard ASCII
5. No placeholder text like "[Company]", "[Date]" — omit the field instead
6. Target 450-600 words for the body (ATS sweet spot)
7. Output plain text only — no markdown bold/italic/headers
8. Sections with no available data should be omitted entirely
"""
        return prompt

    # ── formatting helpers ──────────────────────────────────────────────────

    def _fmt_metrics(self, metrics: List[Dict]) -> str:
        if not metrics:
            return "  (none extracted — use qualitative language only)"
        lines = [f"  • {m.get('raw_text', str(m.get('value')))}" for m in metrics[:15]]
        return '\n'.join(lines)

    def _fmt_skills(self, skills: Dict) -> str:
        if not skills:
            return "  (none extracted)"
        lines = []
        for cat, skill_list in skills.items():
            lines.append(f"  {cat.title()}: {', '.join(skill_list[:12])}")
        return '\n'.join(lines)

    def _fmt_achievements(self, achievements: List[str]) -> str:
        if not achievements:
            return "  (none extracted)"
        return '\n'.join(f"  • {a}" for a in achievements[:10])

    def _fmt_education(self, education: List[Dict]) -> str:
        if not education:
            return "  (none extracted)"
        return '\n'.join(f"  • {e.get('raw_line', e.get('degree', ''))}" for e in education)

    def _fmt_certs(self, certs: List[str]) -> str:
        if not certs:
            return "  (none extracted)"
        return '\n'.join(f"  • {c}" for c in certs[:8])

    def _fmt_contact(self, contact: Dict) -> str:
        if not contact:
            return "  (none extracted)"
        parts = []
        for field in ('name', 'email', 'phone', 'linkedin', 'github'):
            if field in contact:
                parts.append(f"  {field.title()}: {contact[field]}")
        return '\n'.join(parts) if parts else "  (none extracted)"


class ResumeScoringEngine:
    """Multi-dimensional ATS resume scoring (0-100)."""

    def __init__(self):
        self.weights = config.SCORING_WEIGHTS

    def score(self, resume_text: str, metrics_used: int,
              role_match: float = 0.7, jd_text: str = "") -> Tuple[float, Dict]:

        scores = {
            'real_metrics':  self._score_metrics(resume_text, metrics_used),
            'structure':     self._score_structure(resume_text),
            'word_count':    self._score_word_count(resume_text),
            'skill_match':   self._score_skill_match(resume_text, jd_text),
            'role_alignment': role_match,
        }

        overall = sum(scores[dim] * self.weights[dim] for dim in scores)
        logger.info(f"Resume score: {overall:.1f}/100 | breakdown: {scores}")
        return round(overall, 1), scores

    def _score_metrics(self, text: str, metrics_count: int) -> float:
        word_count = len(text.split())
        if word_count == 0:
            return 0
        target = max(1, word_count // 50)
        return round(min(100, (metrics_count / target) * 100), 1)

    def _score_structure(self, text: str) -> float:
        score = 30.0
        required = {
            'summary':      ['professional summary', 'summary'],
            'experience':   ['professional experience', 'experience', 'work history'],
            'skills':       ['technical skills', 'core competencies', 'skills'],
            'achievements': ['key achievements', 'achievements', 'accomplishments'],
        }
        text_lower = text.lower()
        for section, variants in required.items():
            if any(v in text_lower for v in variants):
                score += 17.5
        return min(100, round(score, 1))

    def _score_word_count(self, text: str) -> float:
        wc = len(text.split())
        lo, target, hi = (config.MIN_RESUME_WORD_COUNT,
                          config.TARGET_RESUME_WORD_COUNT,
                          config.MAX_RESUME_WORD_COUNT)
        if wc < lo:
            return (wc / lo) * 50
        elif wc <= target:
            return 50 + (wc - lo) / (target - lo) * 50
        elif wc <= hi:
            return 100 - ((wc - target) / (hi - target)) * 20
        return 50

    def _score_skill_match(self, resume_text: str, jd_text: str) -> float:
        if not jd_text:
            return 70
        jd_kws = set(re.findall(
            r'\b[a-zA-Z][a-zA-Z0-9+#.\-]{2,}\b', jd_text.lower()))
        res_kws = set(re.findall(
            r'\b[a-zA-Z][a-zA-Z0-9+#.\-]{2,}\b', resume_text.lower()))
        if not jd_kws:
            return 70
        overlap = len(jd_kws & res_kws) / len(jd_kws)
        return round(min(100, overlap * 120), 1)   # 120 so ~83% JD overlap = 100


def score_resume(resume_text: str, metrics_used: int = 0,
                 jd_text: str = "") -> Tuple[float, Dict]:
    return ResumeScoringEngine().score(resume_text, metrics_used, jd_text=jd_text)


if __name__ == "__main__":
    detector = RoleDetector()
    jd = "We need a NetSuite Functional Consultant to lead requirements gathering and workshop facilitation."
    print(f"Role: {detector.detect(jd)}")
    print(f"Focus: {detector.get_focus_areas(jd)}")

    kw = JDKeywordExtractor()
    print(f"JD Keywords: {kw.extract(jd, top_n=10)}")
