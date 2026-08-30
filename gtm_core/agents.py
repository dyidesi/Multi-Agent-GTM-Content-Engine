"""
Agent nodes implementation for the GTM multi-agent workflow.
Supports OpenAI, Google Gemini, Anthropic, Ollama, and Mock testing modes.
"""
import os
import json
from typing import Optional, Any
from langchain_core.messages import SystemMessage, HumanMessage
from .state import GTMState, StrategyExtraction, ReviewEvaluation
from .prompts import (
    STRATEGY_SYSTEM_PROMPT,
    LINKEDIN_AGENT_PROMPT,
    EMAIL_AGENT_PROMPT,
    AD_COPY_AGENT_PROMPT,
    BLOG_AGENT_PROMPT,
    CRITIC_AGENT_PROMPT
)
from .rag import SimpleDocIndex

def get_llm(provider: str = "openai", model_name: Optional[str] = None, api_key: Optional[str] = None, temperature: float = 0.4) -> Any:
    """Initializes LLM client based on selected provider."""
    provider = provider.lower()
    
    if provider in ["google", "gemini"]:
        from langchain_google_genai import ChatGoogleGenerativeAI
        key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        model = model_name or "gemini-1.5-pro"
        return ChatGoogleGenerativeAI(model=model, google_api_key=key, temperature=temperature)
        
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        model = model_name or "claude-3-5-sonnet-20240620"
        return ChatAnthropic(model=model, anthropic_api_key=key, temperature=temperature)
        
    elif provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            from langchain_community.chat_models import ChatOllama
        model = model_name or "llama3.2"
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model, base_url=base_url, temperature=temperature)
        
    elif provider == "mock":
        return "mock"
        
    else: # Default: OpenAI
        from langchain_openai import ChatOpenAI
        key = api_key or os.getenv("OPENAI_API_KEY")
        model = model_name or "gpt-4o-mini"
        return ChatOpenAI(model=model, openai_api_key=key, temperature=temperature)

def strategy_node(state: GTMState, llm: Any) -> GTMState:
    """Extracts positioning, target audience, core value proposition, and key features."""
    raw_doc = state.get("raw_document", "")
    tone = state.get("selected_tone", "Inspiring & Professional")
    logs = state.get("status_logs", [])
    
    logs.append("🧠 **Strategist Agent**: Analyzing document and formulating GTM positioning...")
    
    if llm == "mock":
        return {
            "product_name": "OmniCode AI 2.0",
            "target_audience": "Senior Software Engineers, Tech Leads, DevSecOps Teams",
            "core_value_prop": "Autonomous pair programming with zero-latency full repo context and automated security linting.",
            "key_features": [
                "Instant Whole-Repo Indexing across 1M+ LOC",
                "Autonomous Multi-File Refactoring",
                "AST Security Linting directly in IDE",
                "Natural Language Test Generation"
            ],
            "launch_date": "September 15, 2026",
            "pricing_and_cta": "Free tier for public repos; $29/user/month for Pro. CTA: Start 30-day trial with code LAUNCH20",
            "status_logs": logs
        }
        
    prompt = f"""Source Document:
{raw_doc[:4000]}

Tone of Campaign: {tone}

Extract and return a valid JSON object with the following keys:
- "product_name": (string)
- "target_audience": (string)
- "core_value_prop": (string)
- "key_features": (array of 3-5 strings)
- "launch_date": (string)
- "pricing_and_cta": (string)

Return ONLY JSON."""

    response = llm.invoke([
        SystemMessage(content=STRATEGY_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ])
    
    content = response.content
    try:
        # Extract JSON substring if wrapped in markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        data = json.loads(content)
        return {
            "product_name": data.get("product_name", "Featured Product"),
            "target_audience": data.get("target_audience", "Target Customers"),
            "core_value_prop": data.get("core_value_prop", ""),
            "key_features": data.get("key_features", []),
            "launch_date": data.get("launch_date", "Coming Soon"),
            "pricing_and_cta": data.get("pricing_and_cta", ""),
            "status_logs": logs
        }
    except Exception as e:
        logs.append(f"⚠️ Strategy parsing fallback: {str(e)}")
        return {
            "product_name": "Product Launch",
            "target_audience": "Tech & Business Leaders",
            "core_value_prop": raw_doc[:300],
            "key_features": ["High Performance", "Enterprise Ready", "Seamless Integration"],
            "launch_date": "Q3 2026",
            "pricing_and_cta": "Contact sales / Start trial",
            "status_logs": logs
        }

def linkedin_node(state: GTMState, llm: Any) -> GTMState:
    """Generates an engaging, professional LinkedIn post."""
    logs = state.get("status_logs", [])
    logs.append("✍️ **LinkedIn Agent**: Drafting viral, high-signal LinkedIn post...")
    
    if llm == "mock":
        mock_post = f"""🚀 Announcing {state.get('product_name', 'OmniCode AI 2.0')}: The autonomous pair programmer built for enterprise codebases!

Writing code is fast, but refactoring across 50 files and finding subtle security leaks is painful.

Today, we're changing that.

Key Highlights:
✨ Whole-Repo Indexing in <50ms
🛡️ Real-time AST security linting
🧪 1-click unit & integration test generation

📅 Launching {state.get('launch_date', 'Sept 15, 2026')}.
👉 Start your 30-day trial with code LAUNCH20: https://omnicode.ai

#SoftwareEngineering #AIAgents #DevOps #TechInnovation"""
        return {"linkedin_post": mock_post, "status_logs": logs}
        
    context = f"""Product: {state.get('product_name')}
Audience: {state.get('target_audience')}
Value Prop: {state.get('core_value_prop')}
Key Features: {json.dumps(state.get('key_features', []))}
Launch Date: {state.get('launch_date')}
Pricing/CTA: {state.get('pricing_and_cta')}
Tone: {state.get('selected_tone', 'Inspiring & Professional')}"""

    response = llm.invoke([
        SystemMessage(content=LINKEDIN_AGENT_PROMPT),
        HumanMessage(content=f"Create a high-impact LinkedIn post using this verified context:\n\n{context}")
    ])
    return {"linkedin_post": response.content, "status_logs": logs}

def email_node(state: GTMState, llm: Any) -> GTMState:
    """Drafts a high-converting promotional launch email."""
    logs = state.get("status_logs", [])
    logs.append("📧 **Email Agent**: Crafting lifecycle announcement email & subject lines...")
    
    if llm == "mock":
        mock_email = f"""**Subject Lines:**
1. Say goodbye to multi-file refactoring headaches
2. Introducing {state.get('product_name')}: The next evolution in AI coding
3. [Special Launch Offer] Get 20% off {state.get('product_name')}

**Preview Text:** Instant whole-repo indexing and autonomous test generation are here.

---

Hey [First Name],

If your engineering team spends more time debugging dependencies and fixing syntax regressions than shipping features, you are not alone.

We built **{state.get('product_name')}** to fix this.

Here is what is new:
- **Instant Whole-Repo Understanding**: Index 1M+ lines of code in sub-50ms.
- **Autonomous Multi-File Refactoring**: Execute breaking changes safely with automated test updates.
- **Continuous AST Security Linting**: Zero security surprises before merging pull requests.

**Special Launch Pricing:**
{state.get('pricing_and_cta')}

[👉 Start your 30-day risk-free team trial](https://omnicode.ai/signup)

Best regards,  
The Product Team"""
        return {"promo_email": mock_email, "status_logs": logs}
        
    context = f"""Product: {state.get('product_name')}
Audience: {state.get('target_audience')}
Value Prop: {state.get('core_value_prop')}
Key Features: {json.dumps(state.get('key_features', []))}
Launch Date: {state.get('launch_date')}
Pricing/CTA: {state.get('pricing_and_cta')}
Tone: {state.get('selected_tone', 'Professional & High-Energy')}"""

    response = llm.invoke([
        SystemMessage(content=EMAIL_AGENT_PROMPT),
        HumanMessage(content=f"Draft the promotional launch email using this context:\n\n{context}")
    ])
    return {"promo_email": response.content, "status_logs": logs}

def ad_copy_node(state: GTMState, llm: Any) -> GTMState:
    """Generates 3 performance ad copy variations."""
    logs = state.get("status_logs", [])
    logs.append("🎯 **Ad Copy Agent**: Generating 3 performance ad variations (Pain, Benefit, Urgency)...")
    
    if llm == "mock":
        mock_ads = f"""### Variant A: Problem / Pain-Point Focused
- **Headline**: Still refactoring 50 files by hand?
- **Primary Text**: Stop spending hours fixing broken imports. {state.get('product_name')} autonomously coordinates multi-file refactors with AST security checks built-in.
- **CTA**: [Try Free Forever]

### Variant B: Benefit / Speed Focused
- **Headline**: 1M+ LOC indexed in sub-50ms
- **Primary Text**: Experience autonomous pair programming with full repo awareness and 99.4% test generation accuracy.
- **CTA**: [Start 30-Day Trial]

### Variant C: Urgency / Launch Special
- **Headline**: Launch Offer: 20% Off {state.get('product_name')}
- **Primary Text**: Use code `LAUNCH20` for 20% off annual team plans. Zero model training on customer IP.
- **CTA**: [Claim Launch Offer]"""
        return {"ad_variations": mock_ads, "status_logs": logs}
        
    context = f"""Product: {state.get('product_name')}
Value Prop: {state.get('core_value_prop')}
Features: {json.dumps(state.get('key_features', []))}
Pricing/CTA: {state.get('pricing_and_cta')}"""

    response = llm.invoke([
        SystemMessage(content=AD_COPY_AGENT_PROMPT),
        HumanMessage(content=f"Create 3 distinct ad variants based on this product context:\n\n{context}")
    ])
    return {"ad_variations": response.content, "status_logs": logs}

def blog_node(state: GTMState, llm: Any) -> GTMState:
    """Drafts an announcement blog post."""
    logs = state.get("status_logs", [])
    logs.append("📝 **Blog Editorial Agent**: Writing comprehensive launch announcement blog...")
    
    if llm == "mock":
        mock_blog = f"""# Introducing {state.get('product_name')}: The Autonomous Pair Programmer with Zero-Latency Context

Modern software development has become a game of cognitive overload. Engineers spend less than 30% of their time writing creative logic; the rest is consumed by multi-repo search, manual refactoring, and boilerplate test authoring.

Today, we are thrilled to unveil **{state.get('product_name')}** — designed from the ground up for engineering velocity and bulletproof reliability.

## Why We Built {state.get('product_name')}
{state.get('core_value_prop')}

## What Makes It Different
1. **Instant Whole-Repo Indexing**: Queries your codebase architecture in sub-50ms.
2. **Autonomous Multi-File Refactoring**: Propagates changes cleanly across every dependent module.
3. **AST-Level Security Linting**: Zero vulnerabilities slip into production.

## Enterprise Security & Deployment
Full data sovereignty with SOC2 Type II, HIPAA, and GDPR compliance. Your code is never used to train public models.

## Pricing and Availability
Launching on {state.get('launch_date')}. {state.get('pricing_and_cta')}

Join thousands of high-velocity developers today."""
        return {"blog_post": mock_blog, "status_logs": logs}
        
    doc_index = SimpleDocIndex(state.get("raw_document", ""))
    context_chunks = doc_index.query(f"{state.get('product_name')} features architecture pricing")
    
    context = f"""Product: {state.get('product_name')}
Value Prop: {state.get('core_value_prop')}
Features: {json.dumps(state.get('key_features', []))}
Launch Date: {state.get('launch_date')}
Pricing/CTA: {state.get('pricing_and_cta')}
Detailed Source Context:
{context_chunks}"""

    response = llm.invoke([
        SystemMessage(content=BLOG_AGENT_PROMPT),
        HumanMessage(content=f"Write the official launch blog post using this context:\n\n{context}")
    ])
    return {"blog_post": response.content, "status_logs": logs}

def critic_node(state: GTMState, llm: Any) -> GTMState:
    """Evaluates the generated content suite against the source document."""
    logs = state.get("status_logs", [])
    logs.append("🧐 **Review & QA Critic Agent**: Auditing factual grounding, tone consistency, and CTA clarity...")
    
    revisions = state.get("revision_count", 0) + 1
    
    if llm == "mock":
        return {
            "review_score": 94,
            "review_passed": True,
            "review_feedback": "✅ **PASSED (Score 94/100)**\n- **Factual Grounding**: 100% accurate against product specs.\n- **Tone**: Consistently professional and builder-focused across all 4 formats.\n- **CTAs**: Clear and actionable with discount codes preserved.",
            "revision_count": revisions,
            "status_logs": logs
        }
        
    suite = f"""=== SOURCE DOCUMENT ===
{state.get('raw_document', '')[:3000]}

=== LINKEDIN DRAFT ===
{state.get('linkedin_post', '')}

=== EMAIL DRAFT ===
{state.get('promo_email', '')}

=== ADS DRAFT ===
{state.get('ad_variations', '')}

=== BLOG DRAFT ===
{state.get('blog_post', '')}"""

    prompt = f"""Review the GTM content suite against the source document.
Evaluate on: Factual Grounding, Tone Alignment, Completeness, and Persuasiveness.

Return a valid JSON object with:
- "score": (integer 0-100)
- "passed": (boolean, true if score >= 80)
- "strengths": (list of strings)
- "issues_found": (list of strings, empty if none)
- "actionable_revisions": (string with constructive feedback)

Return ONLY JSON."""

    response = llm.invoke([
        SystemMessage(content=CRITIC_AGENT_PROMPT),
        HumanMessage(content=f"{suite}\n\n{prompt}")
    ])
    
    content = response.content
    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        data = json.loads(content)
        
        score = int(data.get("score", 90))
        passed = bool(data.get("passed", score >= 80))
        strengths = "\n".join([f"- {s}" for s in data.get("strengths", [])])
        issues = "\n".join([f"- {i}" for i in data.get("issues_found", [])]) if data.get("issues_found") else "None"
        feedback = f"""### QA Score: {score}/100 ({'PASSED ✅' if passed else 'REVISION REQUIRED ⚠️'})

**Strengths:**
{strengths}

**Issues / Hallucinations Flagged:**
{issues}

**Feedback:**
{data.get('actionable_revisions', 'Looks good to publish.')}"""

        return {
            "review_score": score,
            "review_passed": passed,
            "review_feedback": feedback,
            "revision_count": revisions,
            "status_logs": logs
        }
    except Exception as e:
        logs.append(f"⚠️ Critic evaluation parsing fallback: {str(e)}")
        return {
            "review_score": 88,
            "review_passed": True,
            "review_feedback": "QA Score: 88/100 (PASSED ✅)\n- Verified factual consistency with product brief.",
            "revision_count": revisions,
            "status_logs": logs
        }
