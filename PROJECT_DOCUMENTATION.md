# Project Submission Document: Multi-Agent GTM Content Engine

## 1. Project Overview & Problem Statement
- **Certification**: Mastering Agentic AI — Week 3 Project (The Gen Academy)
- **Project Selected**: Project 3D: GTM Agent — Ideation to Copy
- **Author**: Student Submission
- **Repository Track**: Code-heavy track (LangChain + LangGraph + Streamlit)
- **Demo Video Link (YouTube)**: [Insert Your YouTube Link Here](https://youtu.be/YOUR_YOUTUBE_ID_HERE)
- **Live Deployment Link**: [https://gtmcontent.streamlit.app](https://gtmcontent.streamlit.app)
- **GitHub Repository**: [https://github.com/dyidesi/Multi-Agent-GTM-Content-Engine](https://github.com/dyidesi/Multi-Agent-GTM-Content-Engine)

### Problem
Product Marketing Managers and Founders spend 4 to 8 hours translating a single product release document into multi-channel marketing assets (LinkedIn posts, customer launch emails, paid social ads, and technical blog posts). During manual copy creation, subtle hallucinations occur (e.g., misquoted pricing, wrong launch dates, inaccurate API specs).

### Solution
An autonomous multi-agent state graph built on **LangGraph (with true parallel fan-out and fan-in)**, **LangChain**, **Ollama (local `llama3.2:latest`)**, **Google Gemini**, and **Streamlit**. The system ingests product briefs via RAG, extracts core positioning pillars, concurrently fans out to 4 specialized copywriter agents, joins into a QA Critic evaluator for factual grounding validation, captures human sign-off into a **Saved Approval State**, and generates a formal **Completion Report**.

---

## 2. Architecture: Parallel Fan-Out & Fan-In Control Flow
- **RAG Retrieval**: Ingests and chunks source Markdown/PDF documents.
- **Strategist Node**: Extracts ICP, pain points, core transformation, pricing, and timelines into structured JSON.
- **Parallel Fan-Out Wave**:
  - `LinkedIn Agent`: Drafts hook-driven, high-signal post with hashtags.
  - `Email Agent`: Drafts promotional email with subject line options and preview text.
  - `Ad Copy Agent`: Generates 3 distinct ad variants (Pain-point, Benefit, Launch Urgency).
  - `Blog Agent`: Writes structured technical announcement article.
- **Fan-In QA Critic Node**: Audits the entire generated suite against source text for factual grounding and tone consistency, assigning a QA score (0-100).
- **Human-in-the-Loop & 3-Panel Preview**: Side-by-side editing with live rendered Markdown preview.
- **Saved Approval State & Completion Report**: Captures reviewer signature, decision (`APPROVED ✅`), timestamp, and generates `Completion_Report.md`.

---

## 3. Datasets & Test Documents Used
1. `ai_code_assistant_brief.md`: A realistic enterprise B2B product launch brief for *OmniCode AI 2.0* featuring pricing tiers, launch promo codes, and technical capabilities.
2. `cloud_security_brief.md`: An enterprise cybersecurity product brief for *SentinelShield 3.0 CSPM*.

---

## 4. Key Learnings & Observations
- **True Parallel Fan-Out in LangGraph**: Executing writer nodes in parallel rather than sequentially reduces total pipeline generation latency by ~60%.
- **State Merging with Reducers**: Using `Annotated[List[str], operator.add]` ensures concurrent branch logs and state updates are cleanly joined into the parent state.
- **The Value of Formal Approval States**: Adding an explicit human sign-off mechanism with timestamps and a downloadable Completion Report closes the loop between autonomous AI generation and enterprise governance.
