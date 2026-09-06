"""
LangGraph orchestration for the GTM multi-agent workflow.
"""
from typing import Any, Dict
from langgraph.graph import StateGraph, START, END
from .state import GTMState
from .agents import (
    strategy_node,
    linkedin_node,
    email_node,
    ad_copy_node,
    blog_node,
    critic_node,
    get_llm
)

def build_gtm_graph(provider: str = "mock", model_name: str = None, api_key: str = None):
    """Builds and compiles the stateful LangGraph for the GTM Agent."""
    llm = get_llm(provider=provider, model_name=model_name, api_key=api_key)
    
    workflow = StateGraph(GTMState)
    
    # Define node wrapper functions that inject the initialized LLM
    def run_strategist(state: GTMState) -> GTMState:
        return strategy_node(state, llm)
        
    def run_linkedin(state: GTMState) -> GTMState:
        return linkedin_node(state, llm)
        
    def run_email(state: GTMState) -> GTMState:
        return email_node(state, llm)
        
    def run_ads(state: GTMState) -> GTMState:
        return ad_copy_node(state, llm)
        
    def run_blog(state: GTMState) -> GTMState:
        return blog_node(state, llm)
        
    def run_critic(state: GTMState) -> GTMState:
        return critic_node(state, llm)
        
    # Add Nodes
    workflow.add_node("strategist", run_strategist)
    workflow.add_node("linkedin_writer", run_linkedin)
    workflow.add_node("email_writer", run_email)
    workflow.add_node("ad_writer", run_ads)
    workflow.add_node("blog_writer", run_blog)
    workflow.add_node("critic", run_critic)
    
    # Parallel Fan-Out: Strategist concurrently triggers all 4 specialized copywriters
    workflow.add_edge(START, "strategist")
    workflow.add_edge("strategist", "linkedin_writer")
    workflow.add_edge("strategist", "email_writer")
    workflow.add_edge("strategist", "ad_writer")
    workflow.add_edge("strategist", "blog_writer")
    
    # Parallel Fan-In: All 4 copywriters merge into the QA Critic evaluator
    workflow.add_edge("linkedin_writer", "critic")
    workflow.add_edge("email_writer", "critic")
    workflow.add_edge("ad_writer", "critic")
    workflow.add_edge("blog_writer", "critic")
    
    # Conditional edge for QA review loop
    def should_revise(state: GTMState) -> str:
        passed = state.get("review_passed", True)
        revisions = state.get("revision_count", 0)
        max_revisions = state.get("max_revisions", 1)
        
        if not passed and revisions < max_revisions:
            return "linkedin_writer"
        return END

    workflow.add_conditional_edges(
        "critic",
        should_revise,
        {
            "linkedin_writer": "linkedin_writer",
            END: END
        }
    )
    
    return workflow.compile()
