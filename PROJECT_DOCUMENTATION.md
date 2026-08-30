# Project Submission Document: Multi-Agent GTM Content Engine

## 1. Project Overview & Problem Statement
- **Certification**: Mastering Agentic AI — Week 3 Project (The Gen Academy)
- **Project Selected**: Project 3D: GTM Agent — Ideation to Copy
- **Author**: Student Submission
- **Repository Track**: Code-heavy track (LangChain + LangGraph + Streamlit)

### Problem
Product Marketing Managers and Founders spend 4 to 8 hours translating a single product release document into multi-channel marketing assets (LinkedIn posts, customer launch emails, paid social ads, and technical blog posts). During manual copy creation, subtle hallucinations occur (e.g., misquoted pricing, wrong launch dates, inaccurate API specs).

### Solution
An autonomous multi-agent state graph built on **LangGraph**, **LangChain**, **Ollama (local `llama3.2:latest`)**, and **Streamlit**. The system ingests product briefs via RAG, extracts core positioning pillars, fans out to 4 specialized copywriter agents, and validates outputs using a Critic QA Agent before handing off to a human for inline review and export.

---

## 2. Agent Framework Breakdown
- **Surface**: Streamlit Web Application featuring a 3-panel workspace (Sidebar controls, Human-in-the-Loop text editor, and Live Rendered Markdown Preview).
- **Default LLM Provider**: Local Ollama (`llama3.2:latest`) for private, zero-cost, high-speed execution. Also supports Google Gemini, OpenAI GPT-4o, Anthropic Claude, and Mock Mode.
- **Theme & UI**: Obsidian & Slate Dark Theme (`#0B0F19` / `#161E2E`) with custom glassmorphic cards and live preview formatting.
- **Workflow / Control Flow**:
  1. `RAG Retrieval`: Ingests and chunks source Markdown/PDF documents.
  2. `Strategist Agent`: Extracts ICP, pain points, core transformation, pricing, and timelines into structured JSON.
  3. `Specialized Writers`: Concurrently/sequentially drafts LinkedIn, Email, Ad variations, and Blog posts.
  4. `Critic QA Agent`: Audits output against source text for factual grounding and tone consistency.
  5. `Human-in-the-Loop`: Side-by-side editing with real-time Markdown preview panel and 1-click Markdown/JSON export.
- **State & Persistence**: LangGraph `TypedDict` (`GTMState`) tracking state, revision counts, logs, and user edits.
- **Resilience & Error Handling**: Graceful fallback on malformed JSON, automatic revision loop when score < 80, and zero-setup Mock Mode for offline demo execution.

---

## 3. Datasets & Test Documents Used
1. `ai_code_assistant_brief.md`: A realistic enterprise B2B product launch brief for *OmniCode AI 2.0* featuring pricing tiers, launch promo codes, and technical capabilities.
2. `cloud_security_brief.md`: An enterprise cybersecurity product brief for *SentinelShield 3.0 CSPM*.

---

## 4. Prompts & Iterations
- Initial versions of copywriter agents had a tendency to hallucinate unlisted features (e.g., "50% off" when the document stated "20% off").
- Refined prompt templates to enforce strict factual grounding constraints: *"Constraint: Must adhere 100% to facts from the product brief. No hallucinated stats or imaginary features."*
- Implemented structured output parsing with markdown codeblock striping (`json.loads`) to handle varied LLM markdown formatting.

---

## 5. Key Learnings & Observations
- **Separation of Concerns**: Splitting copy generation into specialized domain agents (LinkedIn vs. Email vs. Ads vs. Blog) produces significantly higher quality content than asking a single general-purpose LLM to output all 4 simultaneously.
- **Local AI Readiness**: Utilizing `langchain-ollama` with `llama3.2:latest` delivers instant, private, on-device intelligence without third-party API keys or rate limits.
- **The Value of the Critic Node**: Having an explicit QA evaluator agent catching discrepancies against the source document provides the safety layer necessary for enterprise adoption.
- **Side-by-Side Human-in-the-Loop**: Giving marketing leads the ability to edit drafts on the left while instantly previewing the rendered Markdown on the right speeds up campaign delivery by 10x.
