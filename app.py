"""
AI Resume Optimizer v2.0 - Enterprise Edition
Streamlit app: Knowledge Base + ATS Resume Generation + Full History
Providers: Ollama (local) | Gemini | ChatGPT (OpenAI) | Grok (xAI)
"""

import streamlit as st
import logging
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'src'))

import config
from database_operations import db
from extraction_engines import analyze_resume
from optimization_engines import RoleDetector, ResumeScoringEngine, MetricRemixer, JDKeywordExtractor
from api_clients import LLMClientFactory

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(**config.STREAMLIT_CONFIG)

# ── Session state ──────────────────────────────────────────────────────────────
for key, default in [('user_id', None), ('kb_loaded', False), ('last_resume', None)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .provider-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 16px;
        margin: 4px 0;
        background: #fafafa;
    }
    .provider-card.connected {
        border-color: #2e7d32;
        background: #f1f8e9;
    }
    .provider-card.disconnected {
        border-color: #c62828;
        background: #fff3e0;
    }
    .ats-score-bar { height: 6px; border-radius: 3px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.title("👤 Account")
        username = st.text_input("Username:", value="default_user", key="username_input")

        if st.button("🔐 Sign In / Register", use_container_width=True):
            user = db.get_user(username)
            if user:
                st.session_state.user_id = user['user_id']
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                try:
                    user_id = db.create_user(username)
                    st.session_state.user_id = user_id
                    st.success(f"Account created for {username}")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        if st.session_state.user_id:
            st.success(f"✓ **{username}**")
            st.markdown("---")
            stats = db.get_user_stats(st.session_state.user_id)
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Runs", stats['total_optimizations'])
            with c2:
                st.metric("KB Versions", stats['kb_versions'])
            gain = stats['avg_score_gain']
            st.metric("Avg ATS Gain", f"{gain:+.1f}" if gain else "0")
            st.metric("Best Score", f"{stats['best_score']:.0f}/100")
            st.markdown("---")
            st.caption("AI Resume Optimizer v2.0")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════════════════
def render_kb_tab():
    st.subheader("Step 1: Build Your Master Knowledge Base")
    st.info(
        "Paste your **most complete resume** — with every real metric, achievement, "
        "skill, and certification you have ever earned. The system extracts the raw "
        "material; the AI remixes it for each JD without inventing a single number."
    )

    kb = db.get_knowledge_base(st.session_state.user_id)
    if kb:
        total_skills = sum(len(v) for v in kb['skills'].values())
        cols = st.columns(5)
        cols[0].metric("Metrics", len(kb['metrics']))
        cols[1].metric("Skills", total_skills)
        cols[2].metric("Achievements", len(kb['achievements']))
        cols[3].metric("Certifications", len(kb.get('certifications', [])))
        cols[4].metric("Education", len(kb.get('education', [])))

        with st.expander("📊 View All Extracted Data"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Metrics ({len(kb['metrics'])})**")
                for m in kb['metrics'][:8]:
                    st.write(f"• {m.get('raw_text', str(m.get('value')))}")
                if kb.get('contact'):
                    st.write("**Contact Detected**")
                    for k, v in kb['contact'].items():
                        st.write(f"• {k.title()}: {v}")
            with c2:
                st.write(f"**Skills ({total_skills})**")
                for cat, skills in kb['skills'].items():
                    st.write(f"• {cat.title()}: {', '.join(skills[:4])}")
                if kb.get('certifications'):
                    st.write("**Certifications**")
                    for cert in kb['certifications'][:4]:
                        st.write(f"• {cert[:60]}")
    else:
        st.warning("No Knowledge Base yet. Paste your resume below.")

    resume_input = st.text_area(
        "Paste your full master resume here:",
        height=350,
        key="kb_input",
        placeholder=(
            "JOHN SMITH\njohn@email.com | +1-555-0100 | linkedin.com/in/johnsmith\n\n"
            "PROFESSIONAL SUMMARY\n...\n\nPROFESSIONAL EXPERIENCE\n...\n\n"
            "SKILLS\nNetSuite | SuiteScript | Python | SQL | Power BI\n\n"
            "EDUCATION\nBachelor of Science, Computer Science — MIT, 2018\n\n"
            "CERTIFICATIONS\nNetSuite Certified | PMP | AWS Solutions Architect"
        ),
    )

    if st.button("💾 Extract & Save Knowledge Base", type="primary", use_container_width=True):
        if not resume_input or len(resume_input) < config.VALIDATION_RULES['min_resume_length']:
            st.error("Resume too short — paste your full resume (at least several hundred characters).")
            return

        with st.spinner("Extracting metrics, skills, contact, education, certifications…"):
            try:
                analysis = analyze_resume(resume_input)

                kb_id = db.save_knowledge_base(
                    st.session_state.user_id,
                    resume_input,
                    analysis['metrics'],
                    analysis['skills'],
                    analysis['achievements'],
                    contact=analysis.get('contact', {}),
                    education=analysis.get('education', []),
                    certifications=analysis.get('certifications', []),
                )

                st.success(f"✅ Knowledge Base saved (ID: {kb_id})")
                st.session_state.kb_loaded = True

                cols = st.columns(5)
                cols[0].metric("Metrics", len(analysis['metrics']))
                cols[1].metric("Skills", sum(len(v) for v in analysis['skills'].values()))
                cols[2].metric("Achievements", len(analysis['achievements']))
                cols[3].metric("Certifications", len(analysis.get('certifications', [])))
                cols[4].metric("Education", len(analysis.get('education', [])))

                if len(analysis['metrics']) < 3:
                    st.warning(
                        "Only a few metrics detected. Make sure your resume contains "
                        "quantified results (e.g., '95% completion rate', '$2M savings')."
                    )

            except Exception as e:
                st.error(f"Extraction error: {e}")
                logger.error(f"KB extraction error: {e}", exc_info=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — OPTIMIZE
# ══════════════════════════════════════════════════════════════════════════════
def render_optimize_tab():
    st.subheader("Step 2: Generate ATS-Optimised Resume")

    kb = db.get_knowledge_base(st.session_state.user_id)
    if not kb:
        st.warning("⚠️ Build your Knowledge Base first (Tab 1).")
        return

    st.info(
        "Paste the full job description. The engine extracts JD keywords, detects the "
        "role type, and generates a complete resume using ONLY your real metrics."
    )

    jd_input = st.text_area(
        "Paste the full job description:",
        height=300,
        key="jd_input",
        placeholder="Copy and paste the entire JD here — the more detail the better…",
    )

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        provider_labels = {
            "ollama":  "🖥  Ollama (Local — Free)",
            "gemini":  "🔵 Gemini (Google)",
            "openai":  "🟢 ChatGPT (OpenAI)",
            "grok":    "⚡ Grok (xAI)",
        }
        api_provider = st.selectbox(
            "AI Provider:",
            list(provider_labels.keys()),
            format_func=lambda x: provider_labels[x],
            help="All cloud providers require the API key set in your .env file",
        )
    with col2:
        tone = st.selectbox(
            "Resume Tone:",
            ["Professional", "Executive", "Technical", "Concise"],
            help="Adjusts how the AI frames your experience",
        )
    with col3:
        st.write("")  # spacer

    if st.button("🚀 Generate Full ATS Resume", type="primary", use_container_width=True):
        if not jd_input or len(jd_input) < config.VALIDATION_RULES['min_jd_length']:
            st.error("Job description is too short — paste the complete JD.")
            return

        with st.spinner("Analysing job description…"):
            detector = RoleDetector()
            role_type = detector.detect(jd_input)
            focus_areas = detector.get_focus_areas(jd_input)
            kw_extractor = JDKeywordExtractor()
            jd_keywords = kw_extractor.extract(jd_input, top_n=15)

        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"Detected Role: **{role_type}**  |  Focus: {', '.join(focus_areas[:3]) or 'General'}")
        with col_b:
            st.caption(f"Top JD Keywords: {', '.join(jd_keywords[:8])}")

        with st.spinner(f"Writing ATS resume via {provider_labels[api_provider]}…"):
            try:
                client = LLMClientFactory.create(api_provider)
                if not client:
                    st.error(f"Could not initialise {api_provider}. Check your .env / Settings tab.")
                    return

                remixer = MetricRemixer()
                prompt = remixer.remix(
                    kb['metrics'],
                    kb['skills'],
                    kb['achievements'],
                    role_type,
                    jd_input,
                    contact=kb.get('contact', {}),
                    education=kb.get('education', []),
                    certifications=kb.get('certifications', []),
                )

                optimized_resume, result = client.generate(prompt, max_tokens=config.ATS_MAX_TOKENS)

                if not result['success']:
                    st.error(f"API Error: {result.get('error', 'Unknown error')}")
                    return

                scorer = ResumeScoringEngine()
                score, breakdown = scorer.score(
                    optimized_resume,
                    len(kb['metrics']),
                    jd_text=jd_input,
                )

                opt_id = db.save_optimization(
                    st.session_state.user_id,
                    jd_id=None,
                    kb_id=kb['kb_id'],
                    original_resume="",
                    optimized_resume=optimized_resume,
                    original_score=0,
                    optimized_score=score,
                    role_type=role_type,
                    api_provider=api_provider,
                    api_model=result.get('model', 'unknown'),
                    metrics_used=[m['metric_id'] for m in kb['metrics'][:5]],
                    processing_time_ms=result.get('processing_time_ms', 0),
                )

                db.log_api_call(
                    st.session_state.user_id,
                    api_provider,
                    result.get('model', 'unknown'),
                    result.get('tokens', {}).get('prompt', 0),
                    result.get('tokens', {}).get('completion', 0),
                    result.get('processing_time_ms', 0),
                    success=True,
                )

                st.session_state.last_resume = optimized_resume

                # ── Score display ──────────────────────────────────────────
                st.success(f"✅ ATS Resume generated in {result.get('processing_time_ms', 0)/1000:.1f}s")

                c1, c2, c3, c4, c5 = st.columns(5)
                delta = score - 50
                c1.metric("ATS Score", f"{score:.0f}/100", delta=f"{delta:+.0f}")
                c2.metric("Metrics Density", f"{breakdown['real_metrics']:.0f}")
                c3.metric("Structure", f"{breakdown['structure']:.0f}")
                c4.metric("Word Count", f"{breakdown['word_count']:.0f}")
                c5.metric("Keyword Match", f"{breakdown['skill_match']:.0f}%")

                # ATS score guide
                if score >= 80:
                    st.success("🟢 Strong ATS score — ready to submit.")
                elif score >= 60:
                    st.warning("🟡 Good score — review for keyword density improvements.")
                else:
                    st.error("🔴 Low score — ensure the JD is pasted in full and your KB has real metrics.")

                # ── Resume output ──────────────────────────────────────────
                st.subheader("📄 Your ATS-Optimised Resume")
                st.text_area(
                    "Review your resume:",
                    value=optimized_resume,
                    height=500,
                    disabled=True,
                    key="result_resume",
                )

                filename = f"resume_{role_type.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                st.download_button(
                    "⬇️ Download Resume (.txt)",
                    optimized_resume,
                    filename,
                    "text/plain",
                    use_container_width=True,
                )

                with st.expander("🔬 Score Breakdown & Tips"):
                    st.write(f"**Metrics Density** {breakdown['real_metrics']:.0f}/100 — "
                             "Aim for at least 1 number per 50 words.")
                    st.write(f"**Structure** {breakdown['structure']:.0f}/100 — "
                             "ATS needs: Summary, Experience, Skills, Achievements.")
                    st.write(f"**Keyword Match** {breakdown['skill_match']:.0f}% — "
                             "Higher = more JD terms mirrored in your resume.")
                    st.write(f"**Model used:** {result.get('model', 'unknown')}")
                    tokens = result.get('tokens', {})
                    if tokens:
                        st.write(f"**Tokens:** {tokens.get('prompt', 0)} prompt / "
                                 f"{tokens.get('completion', 0)} completion")

            except Exception as e:
                st.error(f"Error: {e}")
                logger.error(f"Resume generation error: {e}", exc_info=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORY
# ══════════════════════════════════════════════════════════════════════════════
def render_history_tab():
    st.subheader("📈 Optimization History")

    optimizations = db.get_user_optimizations(st.session_state.user_id, limit=50)

    if not optimizations:
        st.info("No optimizations yet. Generate one in the Optimize tab!")
        return

    stats = db.get_user_stats(st.session_state.user_id)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Runs", stats['total_optimizations'])
    c2.metric("Best Score", f"{stats['best_score']:.0f}")
    c3.metric("Avg Score Gain", f"{stats['avg_score_gain']:+.1f}")
    c4.metric("KB Versions", stats['kb_versions'])

    st.markdown("---")
    st.write(f"**Last {min(len(optimizations), 25)} runs:**")

    for opt in optimizations[:25]:
        score = opt.get('optimized_score', 0) or 0
        if score >= 80:
            badge = "🟢"
        elif score >= 60:
            badge = "🟡"
        else:
            badge = "🔴"

        c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 2, 3])
        c1.write(f"{badge} **{score:.0f}**")
        c2.write(f"_{opt.get('role_type', '?')}_")
        c3.write(opt.get('api_provider', '?').upper())
        c4.write(f"{opt.get('metric_count', 0)} metrics used")
        c5.caption(str(opt.get('created_at', ''))[:16])
        st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
PROVIDER_META = {
    'ollama': {
        'icon': '🖥',
        'label': 'Ollama (Local)',
        'description': 'Free, runs on your machine. No API key needed.',
        'setup': '`ollama serve` then `ollama pull mistral`',
        'env_var': None,
        'docs': 'https://ollama.com',
        'model_key': 'OLLAMA_MODEL',
        'default_model': config.OLLAMA_DEFAULT_MODEL,
    },
    'gemini': {
        'icon': '🔵',
        'label': 'Gemini (Google AI)',
        'description': 'Fast & generous free tier. gemini-2.5-flash recommended.',
        'setup': 'Set `GEMINI_API_KEY` in your `.env` file',
        'env_var': 'GEMINI_API_KEY',
        'docs': 'https://aistudio.google.com/app/apikey',
        'model_key': 'GEMINI_MODEL',
        'default_model': config.GEMINI_MODEL,
    },
    'openai': {
        'icon': '🟢',
        'label': 'ChatGPT (OpenAI)',
        'description': 'gpt-4o-mini is fast and affordable. gpt-4o for best quality.',
        'setup': 'Set `OPENAI_API_KEY` in your `.env` file',
        'env_var': 'OPENAI_API_KEY',
        'docs': 'https://platform.openai.com/api-keys',
        'model_key': 'OPENAI_MODEL',
        'default_model': config.OPENAI_MODEL,
    },
    'grok': {
        'icon': '⚡',
        'label': 'Grok (xAI)',
        'description': 'Elon Musk\'s xAI model. grok-3-beta has strong reasoning.',
        'setup': 'Set `XAI_API_KEY` in your `.env` file',
        'env_var': 'XAI_API_KEY',
        'docs': 'https://console.x.ai',
        'model_key': 'GROK_MODEL',
        'default_model': config.GROK_MODEL,
    },
}


def render_settings_tab():
    st.subheader("⚙️ Settings & Connections")

    # ── API Connections ────────────────────────────────────────────────────
    st.markdown("### 🔌 API Connections")
    st.caption("Connections are read-only here. To add keys, edit your `.env` file and restart the app.")

    providers_status = LLMClientFactory.get_available_providers()
    status_map = {p['provider']: p for p in providers_status}

    cols = st.columns(4)
    for i, (provider_key, meta) in enumerate(PROVIDER_META.items()):
        p_status = status_map.get(provider_key, {'available': False, 'reason': 'Unknown'})
        connected = p_status['available']

        with cols[i]:
            badge = "🟢 Connected" if connected else "🔴 Not connected"
            model = ""
            if connected and 'info' in p_status:
                model = p_status['info'].get('model', '')

            st.markdown(f"""
<div class="provider-card {'connected' if connected else 'disconnected'}">
<b>{meta['icon']} {meta['label']}</b><br>
<small>{badge}</small><br>
<small>{model}</small>
</div>
""", unsafe_allow_html=True)

            if connected:
                st.success("Ready", icon="✅")
            else:
                reason = p_status.get('reason', meta['setup'])
                st.warning(reason, icon="⚠️")
                if meta.get('docs'):
                    st.caption(f"[Get API key →]({meta['docs']})")

    st.markdown("---")

    # ── Provider details ────────────────────────────────────────────────────
    st.markdown("### 📋 Provider Configuration Reference")
    for provider_key, meta in PROVIDER_META.items():
        with st.expander(f"{meta['icon']} {meta['label']}"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**About:** {meta['description']}")
                st.write(f"**Setup:** {meta['setup']}")
                if meta.get('env_var'):
                    st.code(f"{meta['env_var']}=your_key_here", language="bash")
                else:
                    st.code("No API key needed — run Ollama locally", language="bash")
            with col_b:
                st.write(f"**Current model:** `{meta['default_model']}`")
                st.write(f"**Override via:** `{meta['model_key']}=model-name` in .env")
                if meta.get('docs'):
                    st.write(f"**Docs:** {meta['docs']}")

    st.markdown("---")

    # ── System Info ─────────────────────────────────────────────────────────
    st.markdown("### 💾 System Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Database**")
        st.code(config.DATABASE_URL, language="text")
        st.write("**Logs**")
        st.code(str(config.LOG_FILE), language="text")
    with col2:
        st.write("**Data directory**")
        st.code(str(config.DATA_DIR), language="text")
        st.write("**Resume token limit**")
        st.code(f"{config.ATS_MAX_TOKENS} tokens", language="text")

    st.markdown("---")

    # ── .env template ───────────────────────────────────────────────────────
    st.markdown("### 📄 .env Template")
    st.caption("Copy this into a file named `.env` in the app directory, fill in your keys, and restart.")
    st.code("""# AI Resume Optimizer — API Keys
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
XAI_API_KEY=your_xai_key_here

# Optional overrides
# OLLAMA_BASE_URL=http://localhost:11434/v1
# OLLAMA_MODEL=mistral
# GEMINI_MODEL=gemini-2.5-flash
# OPENAI_MODEL=gpt-4o-mini
# GROK_MODEL=grok-3-beta
# LOG_LEVEL=INFO
""", language="bash")

    st.markdown("---")
    st.caption(f"AI Resume Optimizer v2.0 — Enterprise Edition | {datetime.now().strftime('%Y-%m-%d')}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    st.title("🚀 AI Resume Optimizer v2.0")
    st.markdown(
        "**Enterprise Edition** — Real metrics only · ATS-grade output · "
        "Ollama · Gemini · ChatGPT · Grok"
    )

    render_sidebar()

    if not st.session_state.user_id:
        st.warning("⚠️ Sign in using the sidebar to get started.")
        st.stop()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Knowledge Base",
        "✏️ Generate Resume",
        "📊 History",
        "⚙️ Settings",
    ])

    with tab1:
        render_kb_tab()
    with tab2:
        render_optimize_tab()
    with tab3:
        render_history_tab()
    with tab4:
        render_settings_tab()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        st.error(f"Application error — check logs at: {config.LOG_FILE}")
