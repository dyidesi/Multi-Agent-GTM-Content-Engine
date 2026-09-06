"""
Streamlit Web Application for Project 3D: GTM Agent (Ideation to Copy)
"""
import os
import streamlit as st
import json
from dotenv import load_dotenv

# Load local environment variables if present
load_dotenv()

from gtm_core.rag import load_document_text
from gtm_core.graph import build_gtm_graph

st.set_page_config(
    page_title="GTM Agent Swarm - Ideation to Copy",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for Dark Theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    .agent-card {
        background-color: #161E2E;
        border: 1px solid #2E384D;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .score-badge {
        font-size: 1.3rem;
        font-weight: bold;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        display: inline-block;
    }
    .stTextArea textarea {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .preview-container {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1.2rem;
        min-height: 380px;
        color: #F8FAFC;
    }
    .preview-header-tag {
        display: inline-flex;
        align-items: center;
        background-color: #1E293B;
        color: #818CF8;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        margin-bottom: 0.8rem;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300, show_spinner=False)
def fetch_available_gemini_models(api_key_str: str):
    if not api_key_str or len(api_key_str.strip()) < 10:
        return []
    import urllib.request
    clean_key = api_key_str.strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={clean_key}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Streamlit-GTM-Agent"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode())
            models = []
            for m in data.get("models", []):
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    name = m.get("name", "").replace("models/", "")
                    if name:
                        models.append(name)
            return sorted(models)
    except Exception:
        return []

# ----------------- SIDEBAR CONFIG -----------------
with st.sidebar:
    st.markdown("## 🤖 **GTM Agent Engine**")
    st.caption("Week 3 Agentic AI Certification • Project 3D")
    
    st.divider()
    st.subheader("⚙️ Model Configuration")
    
    provider_options = [
        "Ollama (Local)",
        "Demo / Mock Mode (Zero Setup)",
        "Google Gemini",
        "OpenAI",
        "Anthropic"
    ]
    
    provider_selection = st.selectbox("LLM Provider", provider_options, index=0)
    
    provider_map = {
        "Ollama (Local)": "ollama",
        "Demo / Mock Mode (Zero Setup)": "mock",
        "Google Gemini": "google",
        "OpenAI": "openai",
        "Anthropic": "anthropic"
    }
    provider_key = provider_map[provider_selection]
    
    api_key = ""
    model_name = None
    
    if provider_key == "google":
        default_gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
        api_key = st.text_input("Gemini API Key", value=default_gemini_key, type="password", placeholder="AIzaSy...")
        
        dynamic_gemini_models = fetch_available_gemini_models(api_key)
        if dynamic_gemini_models:
            st.success(f"🟢 Found {len(dynamic_gemini_models)} available Gemini models")
            # Default to gemini-flash-lite-latest if present
            default_idx = 0
            for i, m in enumerate(dynamic_gemini_models):
                if m == "gemini-flash-lite-latest" or "flash-lite-latest" in m:
                    default_idx = i
                    break
                elif "flash-lite" in m:
                    default_idx = i
                    break
                elif m == "gemini-1.5-flash":
                    default_idx = i
            model_name = st.selectbox("Available Gemini Model", dynamic_gemini_models, index=default_idx)
        else:
            if api_key and len(api_key.strip()) >= 10:
                st.caption("ℹ️ Using standard model catalogue (Check API key if connection fails)")
            gemini_model_options = [
                "gemini-flash-lite-latest",
                "gemini-1.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash-8b",
                "gemini-1.5-pro",
                "gemini-1.5-pro-latest",
                "gemini-1.5-flash-latest",
                "Custom Model Name..."
            ]
            chosen_gemini = st.selectbox("Model", gemini_model_options, index=0)
            if chosen_gemini == "Custom Model Name...":
                model_name = st.text_input("Enter Gemini Model Name", value="gemini-flash-lite-latest")
            else:
                model_name = chosen_gemini
    elif provider_key == "openai":
        default_openai_key = os.getenv("OPENAI_API_KEY", "")
        api_key = st.text_input("OpenAI API Key", value=default_openai_key, type="password", placeholder="sk-...")
        openai_model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "Custom Model Name..."]
        chosen_openai = st.selectbox("Model", openai_model_options, index=0)
        if chosen_openai == "Custom Model Name...":
            model_name = st.text_input("Enter OpenAI Model Name", value="gpt-4o-mini")
        else:
            model_name = chosen_openai
    elif provider_key == "anthropic":
        default_anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        api_key = st.text_input("Anthropic API Key", value=default_anthropic_key, type="password", placeholder="sk-ant-...")
        anthropic_model_options = ["claude-3-5-sonnet-20240620", "claude-3-haiku-20240307", "Custom Model Name..."]
        chosen_anthropic = st.selectbox("Model", anthropic_model_options, index=0)
        if chosen_anthropic == "Custom Model Name...":
            model_name = st.text_input("Enter Anthropic Model Name", value="claude-3-5-sonnet-20240620")
        else:
            model_name = chosen_anthropic
    elif provider_key == "ollama":
        import urllib.request
        detected_models = []
        try:
            with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1.5) as resp:
                data = json.loads(resp.read().decode())
                detected_models = [m["name"] for m in data.get("models", [])]
        except Exception:
            pass

        if detected_models:
            st.success(f"🟢 Connected to Ollama ({len(detected_models)} models found)")
            # Default to llama3.2:latest if present
            default_idx = 0
            for i, m in enumerate(detected_models):
                if "llama3.2" in m:
                    default_idx = i
                    break
            model_name = st.selectbox("Detected Ollama Model", detected_models, index=default_idx)
        else:
            st.warning("Could not auto-detect Ollama models. Is `ollama serve` running?")
            model_name = st.text_input("Ollama Model Name", value="llama3.2:latest")
        
    st.divider()
    st.subheader("🎯 Campaign Settings")
    campaign_tone = st.selectbox(
        "Brand Voice & Tone",
        [
            "Inspiring & Visionary",
            "Technical & Developer-Centric",
            "Direct & Conversion-Focused",
            "Punchy, High-Energy & Bold",
            "Executive & Authoritative"
        ],
        index=0
    )
    
    st.divider()
    st.info("💡 **Tip**: Switch to 'Demo / Mock Mode' for instantaneous walkthroughs without needing API credits.")

# ----------------- MAIN INTERFACE -----------------
st.markdown('<div class="main-header">🚀 Multi-Agent GTM Content Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous multi-agent system that turns raw product briefs into a fully reviewed Go-To-Market content suite (LinkedIn, Email, Ads, Blog).</div>', unsafe_allow_html=True)

# Input Section: Tabs for Sample vs Upload
input_tab1, input_tab2 = st.tabs(["📄 Preloaded Sample Briefs", "📤 Upload Custom Brief"])

raw_doc_text = ""
selected_filename = ""

with input_tab1:
    sample_choice = st.radio(
        "Choose a test product brief:",
        ["OmniCode AI 2.0 (Developer Tools & AI)", "SentinelShield 3.0 (Enterprise Cloud Security)"],
        horizontal=True
    )
    
    sample_path = (
        "sample_data/ai_code_assistant_brief.md"
        if "OmniCode" in sample_choice
        else "sample_data/cloud_security_brief.md"
    )
    
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            raw_doc_text = f.read()
            selected_filename = os.path.basename(sample_path)
            
        with st.expander("👁️ Preview Selected Sample Brief", expanded=False):
            st.markdown(raw_doc_text)
    else:
        st.warning("Sample brief file not found. Please upload a file.")

with input_tab2:
    uploaded_file = st.file_uploader("Upload Product Spec, Launch Plan or Feature Doc (.md, .txt, .pdf)", type=["md", "txt", "pdf"])
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        raw_doc_text = load_document_text(file_bytes, uploaded_file.name)
        selected_filename = uploaded_file.name
        st.success(f"Loaded '{uploaded_file.name}' ({len(raw_doc_text)} characters)")

st.write("")
run_col1, run_col2 = st.columns([1, 4])
with run_col1:
    execute_btn = st.button("✨ Run GTM Agent Swarm", type="primary", use_container_width=True)

# Initialize Session State for Results
if "gtm_results" not in st.session_state:
    st.session_state.gtm_results = None

if execute_btn:
    if not raw_doc_text.strip():
        st.error("Please select a sample brief or upload a document first.")
    else:
        status_container = st.status("🤖 Agent Swarm in Progress...", expanded=True)
        
        try:
            with status_container:
                st.write("🔧 Initializing LangGraph state graph...")
                graph = build_gtm_graph(
                    provider=provider_key,
                    model_name=model_name,
                    api_key=api_key
                )
                
                initial_state = {
                    "raw_document": raw_doc_text,
                    "filename": selected_filename,
                    "selected_tone": campaign_tone,
                    "status_logs": [],
                    "revision_count": 0,
                    "max_revisions": 1
                }
                
                st.write("🧠 Strategist analyzing positioning pillars & audience...")
                st.write("✍️ LinkedIn, Email, Ads, and Blog specialized writer agents executing...")
                st.write("🧐 QA Critic reviewing factual grounding against source document...")
                
                # Execute graph
                final_state = graph.invoke(initial_state)
                
                st.session_state.gtm_results = final_state
                status_container.update(label="✅ GTM Content Suite Successfully Generated & Reviewed!", state="complete", expanded=False)
                
        except Exception as e:
            status_container.update(label="❌ Pipeline Error", state="error")
            st.error(f"Execution failed: {str(e)}")

# ----------------- DISPLAY RESULTS -----------------
results = st.session_state.gtm_results

if results:
    st.divider()
    
    # Overview Banner
    col_score, col_status, col_prod, col_date = st.columns([1.5, 2, 2.5, 2])
    score = results.get("review_score", 90)
    passed = results.get("review_passed", True)
    
    with col_score:
        st.metric("QA Review Score", f"{score}/100", delta="PASSED" if passed else "REVISION")
    with col_status:
        st.metric("Human-in-the-Loop", "Ready for Approval ✍️")
    with col_prod:
        st.metric("Product", results.get("product_name", "Featured Product"))
    with col_date:
        st.metric("Target Launch", results.get("launch_date", "TBD"))
        
    # View Mode Toggle
    st.write("")
    ctrl_col1, ctrl_col2 = st.columns([2, 1])
    with ctrl_col1:
        show_preview = st.toggle("👁️ Show Live Markdown Preview Panel (Side-by-Side)", value=True)
    
    # Main Output Tabs
    tab_linkedin, tab_email, tab_ads, tab_blog, tab_strategy, tab_qa = st.tabs([
        "💼 LinkedIn Post",
        "📧 Promotional Email",
        "🎯 Ad Variations",
        "📝 Announcement Blog",
        "📊 Strategy & Positioning",
        "🛡️ QA Critic Review"
    ])
    
    with tab_linkedin:
        st.subheader("💼 High-Impact LinkedIn Post")
        current_val = results.get("linkedin_post", "")
        if show_preview:
            col_edit, col_prev = st.columns([1, 1])
            with col_edit:
                linkedin_text = st.text_area(
                    "Edit LinkedIn Copy (Human-in-the-loop):",
                    value=current_val,
                    height=450,
                    key="edit_linkedin"
                )
            with col_prev:
                with st.container(border=True):
                    st.markdown('<div class="preview-header-tag">👁️ Live LinkedIn Preview</div>', unsafe_allow_html=True)
                    preview_content = st.session_state.get("edit_linkedin", current_val)
                    st.markdown(preview_content)
        else:
            linkedin_text = st.text_area(
                "Edit LinkedIn Copy (Human-in-the-loop):",
                value=current_val,
                height=350,
                key="edit_linkedin"
            )
        
    with tab_email:
        st.subheader("📧 Promotional Email Campaign")
        current_email = results.get("promo_email", "")
        if show_preview:
            col_edit, col_prev = st.columns([1, 1])
            with col_edit:
                email_text = st.text_area(
                    "Edit Email Copy (Human-in-the-loop):",
                    value=current_email,
                    height=450,
                    key="edit_email"
                )
            with col_prev:
                with st.container(border=True):
                    st.markdown('<div class="preview-header-tag">👁️ Live Email Rendered Preview</div>', unsafe_allow_html=True)
                    email_preview = st.session_state.get("edit_email", current_email)
                    st.markdown(email_preview)
        else:
            email_text = st.text_area(
                "Edit Email Copy (Human-in-the-loop):",
                value=current_email,
                height=350,
                key="edit_email"
            )
        
    with tab_ads:
        st.subheader("🎯 Performance Paid Social Ads (3 Variants)")
        current_ads = results.get("ad_variations", "")
        if show_preview:
            col_edit, col_prev = st.columns([1, 1])
            with col_edit:
                ads_text = st.text_area(
                    "Edit Ad Variations (Human-in-the-loop):",
                    value=current_ads,
                    height=450,
                    key="edit_ads"
                )
            with col_prev:
                with st.container(border=True):
                    st.markdown('<div class="preview-header-tag">👁️ Live Ad Variations Preview</div>', unsafe_allow_html=True)
                    ads_preview = st.session_state.get("edit_ads", current_ads)
                    st.markdown(ads_preview)
        else:
            ads_text = st.text_area(
                "Edit Ad Variations (Human-in-the-loop):",
                value=current_ads,
                height=350,
                key="edit_ads"
            )
        
    with tab_blog:
        st.subheader("📝 Official Launch Announcement Blog")
        current_blog = results.get("blog_post", "")
        if show_preview:
            col_edit, col_prev = st.columns([1, 1])
            with col_edit:
                blog_text = st.text_area(
                    "Edit Blog Markdown (Human-in-the-loop):",
                    value=current_blog,
                    height=500,
                    key="edit_blog"
                )
            with col_prev:
                with st.container(border=True):
                    st.markdown('<div class="preview-header-tag">👁️ Live Rendered Blog Article</div>', unsafe_allow_html=True)
                    blog_preview = st.session_state.get("edit_blog", current_blog)
                    st.markdown(blog_preview)
        else:
            blog_text = st.text_area(
                "Edit Blog Markdown (Human-in-the-loop):",
                value=current_blog,
                height=400,
                key="edit_blog"
            )
            
    with tab_strategy:
        st.subheader("📊 Extracted GTM Strategic Pillars")
        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            st.markdown(f"**Target Audience / ICP:**\n{results.get('target_audience', 'N/A')}")
            st.markdown(f"**Core Value Proposition:**\n{results.get('core_value_prop', 'N/A')}")
            st.markdown(f"**Pricing & Primary CTA:**\n{results.get('pricing_and_cta', 'N/A')}")
        with col_s2:
            st.markdown("**Key Features & Capabilities:**")
            for feat in results.get("key_features", []):
                st.markdown(f"- {feat}")
            
    with tab_qa:
        st.subheader("🛡️ Quality Assurance & Fact-Checking Audit")
        col_qa1, col_qa2 = st.columns([1, 1])
        with col_qa1:
            st.markdown(results.get("review_feedback", "No QA audit recorded."))
        with col_qa2:
            st.subheader("📜 Agent Execution Trace")
            for log in results.get("status_logs", []):
                st.markdown(log)

    # Export Section
    st.divider()
    st.subheader("📥 Export Final GTM Suite")
    
    full_markdown_bundle = f"""# GTM Launch Suite: {results.get('product_name', 'Product Launch')}
**Target Audience**: {results.get('target_audience')}
**Target Launch Date**: {results.get('launch_date')}
**QA Score**: {results.get('review_score')}/100

---

## 1. LinkedIn Launch Post
{st.session_state.get('edit_linkedin', results.get('linkedin_post', ''))}

---

## 2. Promotional Email Campaign
{st.session_state.get('edit_email', results.get('promo_email', ''))}

---

## 3. Social Ad Variations
{st.session_state.get('edit_ads', results.get('ad_variations', ''))}

---

## 4. Launch Announcement Blog
{st.session_state.get('edit_blog', results.get('blog_post', ''))}

---

## 5. QA Audit Report
{results.get('review_feedback', '')}
"""

    col_dl1, col_dl2 = st.columns([1, 1])
    with col_dl1:
        st.download_button(
            label="📥 Download Full GTM Kit (.md)",
            data=full_markdown_bundle,
            file_name=f"GTM_Kit_{results.get('product_name', 'Launch').replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_dl2:
        json_export = json.dumps({
            "product_name": results.get("product_name"),
            "target_audience": results.get("target_audience"),
            "linkedin_post": st.session_state.get("edit_linkedin", results.get("linkedin_post")),
            "promo_email": st.session_state.get("edit_email", results.get("promo_email")),
            "ad_variations": st.session_state.get("edit_ads", results.get("ad_variations")),
            "blog_post": st.session_state.get("edit_blog", results.get("blog_post")),
            "qa_score": results.get("review_score")
        }, indent=2)
        
        st.download_button(
            label="📦 Export Structured JSON Data",
            data=json_export,
            file_name="gtm_assets.json",
            mime="application/json",
            use_container_width=True
        )
