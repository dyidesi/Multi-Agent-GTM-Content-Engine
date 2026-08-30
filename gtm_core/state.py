"""
State definition for the GTM Multi-Agent Workflow using TypedDict & Pydantic models.
"""
from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field

class GTMState(TypedDict, total=False):
    # Ingestion & RAG Context
    raw_document: str
    filename: str
    
    # Extracted Strategy & Positioning
    product_name: str
    target_audience: str
    core_value_prop: str
    key_features: List[str]
    launch_date: str
    pricing_and_cta: str
    selected_tone: str
    
    # Generated Copy Assets
    linkedin_post: str
    promo_email: str
    blog_post: str
    ad_variations: str
    
    # Review & Quality Assurance
    review_score: int
    review_feedback: str
    review_passed: bool
    revision_count: int
    max_revisions: int
    
    # Execution Tracing & Logs
    status_logs: List[str]
    error: Optional[str]

class StrategyExtraction(BaseModel):
    product_name: str = Field(description="Name of the product or feature")
    target_audience: str = Field(description="Primary target personas and ICP")
    core_value_prop: str = Field(description="Core value proposition and main problem solved")
    key_features: List[str] = Field(description="Top 3 to 5 key features or capabilities")
    launch_date: str = Field(description="Launch date or availability timeline")
    pricing_and_cta: str = Field(description="Pricing details, promo codes, and primary calls to action")

class ReviewEvaluation(BaseModel):
    score: int = Field(description="Overall quality and factual alignment score between 0 and 100")
    passed: bool = Field(description="True if score >= 80 and no severe hallucinations or tone mismatches")
    strengths: List[str] = Field(description="Key strengths of the generated content suite")
    issues_found: List[str] = Field(description="Any factual errors, ungrounded claims, or missing details")
    actionable_revisions: str = Field(description="Specific feedback for writers if revisions are required")
