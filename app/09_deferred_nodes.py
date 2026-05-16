"""
Graph 9: Deferred Nodes — Race-Condition-Free Aggregation
Concept: When multiple parallel branches converge at one node, that node
         may run before all branches finish (race condition).
         defer=True tells LangGraph: wait until EVERY parallel branch
         that feeds into this node has completed before running it.

Without defer=True:
  research_topic A finishes → synthesizer starts (topics B, C not done yet)

With defer=True:
  research_topic A ─┐
  research_topic B ─┼─ ALL done → synthesizer runs (all findings available)
  research_topic C ─┘
"""

import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class ResearchState(TypedDict):
    topics:       list[str]
    findings:     Annotated[list[str], operator.add]   # accumulated from parallel branches
    final_report: str


def coordinator(state: ResearchState) -> list[Send]:
    """Distribute research topics in parallel — one worker per topic."""
    print(f"📋 Coordinating research on {len(state['topics'])} topics")
    return [
        Send("research_topic", {"topics": [topic], "findings": [], "final_report": ""})
        for topic in state["topics"]
    ]


def research_topic(state: ResearchState) -> dict:
    """Worker: researches a single topic (runs in parallel)."""
    topic   = state["topics"][0]
    finding = f"Research finding for '{topic}': key insight discovered"
    print(f"🔬 Researching: {topic}")
    return {"findings": [finding]}


def synthesize_report(state: ResearchState) -> dict:
    """
    Reduce node — ONLY runs after ALL research_topic branches complete.
    defer=True guarantees this even when branches finish at different times.
    """
    print(f"\n📊 Synthesizing {len(state['findings'])} findings...")
    findings_text = "\n".join(f"• {f}" for f in state["findings"])
    report = "FINAL REPORT:\n" + findings_text
    return {"final_report": report}


builder = StateGraph(ResearchState)
builder.add_node("research_topic", research_topic)
builder.add_node("synthesizer",    synthesize_report, defer=True)   # ← key line

builder.add_conditional_edges(START, coordinator, ["research_topic"])
builder.add_edge("research_topic", "synthesizer")
builder.add_edge("synthesizer",    END)

app = builder.compile()
