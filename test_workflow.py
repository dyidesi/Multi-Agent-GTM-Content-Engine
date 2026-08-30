"""
Verification test script for GTM Agent multi-agent graph.
"""
import os
import sys
import io

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from gtm_core.graph import build_gtm_graph

def test_pipeline():
    sample_file = os.path.join("sample_data", "ai_code_assistant_brief.md")
    with open(sample_file, "r", encoding="utf-8") as f:
        raw_doc = f.read()

    print("[1/3] Building LangGraph state graph...")
    graph = build_gtm_graph(provider="mock")

    initial_state = {
        "raw_document": raw_doc,
        "filename": "ai_code_assistant_brief.md",
        "selected_tone": "Inspiring & Visionary",
        "status_logs": [],
        "revision_count": 0,
        "max_revisions": 1
    }

    print("[2/3] Invoking multi-agent swarm...")
    result = graph.invoke(initial_state)

    print("\n--- Pipeline Execution Output ---")
    print(f"Product Name: {result.get('product_name')}")
    print(f"Target Audience: {result.get('target_audience')}")
    print(f"QA Review Score: {result.get('review_score')}/100")
    print(f"Passed: {result.get('review_passed')}")
    print(f"LinkedIn post length: {len(result.get('linkedin_post', ''))} chars")
    print(f"Promo email length: {len(result.get('promo_email', ''))} chars")
    print(f"Ad variations length: {len(result.get('ad_variations', ''))} chars")
    print(f"Blog post length: {len(result.get('blog_post', ''))} chars")

    assert result.get("linkedin_post") is not None
    assert result.get("promo_email") is not None
    assert result.get("ad_variations") is not None
    assert result.get("blog_post") is not None
    assert result.get("review_score") is not None
    print("\n[3/3] [PASS] All automated pipeline assertions passed successfully!")

if __name__ == "__main__":
    test_pipeline()
