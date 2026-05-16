"""
Graph 8: Map-Reduce Pattern
Concept: Classic two-phase pattern.
  MAP phase:    Send API fans out one worker per item (all run in parallel).
  REDUCE phase: Annotated[list, operator.add] collects all worker results.
                The reduce node runs only AFTER all workers finish.

Example: Generate 4 essay outlines in parallel using different approaches,
         then pick the highest-scoring one (the reduce step).

OverallState = the shared graph state (topic, approaches, outlines, best)
WorkerState  = private state for each worker (topic + one approach)
"""

import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class OverallState(TypedDict):
    topic:        str
    approaches:   list[str]
    outlines:     Annotated[list[dict], operator.add]   # REDUCE collector
    best_outline: str


class WorkerState(TypedDict):
    topic:    str
    approach: str   # each worker gets a different approach


def generate_approaches(state: OverallState):
    """Setup node: generates the list of items to map over."""
    approaches = [
        "chronological narrative",
        "problem-solution framework",
        "compare and contrast",
        "case study based",
    ]
    print(f"📋 Generated {len(approaches)} essay approaches to evaluate in parallel.")
    return {"approaches": approaches}


def dispatch_workers(state: OverallState) -> list[Send]:
    """MAP: one Send per approach = N parallel workers."""
    return [
        Send("write_outline", {"topic": state["topic"], "approach": a})
        for a in state["approaches"]
    ]


def write_outline(state: WorkerState):
    """MAP worker: runs N times in parallel, each with a different approach."""
    approach = state["approach"]
    topic    = state["topic"]
    scores = {
        "chronological narrative":    72,
        "problem-solution framework": 91,
        "compare and contrast":       68,
        "case study based":           85,
    }
    score   = scores.get(approach, 50)
    outline = {
        "approach": approach,
        "score":    score,
        "preview":  f"Essay on '{topic}' using {approach}",
    }
    print(f"  ✍️  Worker [{approach}] → score: {score}")
    return {"outlines": [outline]}   # appended to OverallState.outlines via operator.add


def pick_best_outline(state: OverallState):
    """REDUCE: runs after ALL workers finish. Picks highest-scoring outline."""
    print(f"\n🔀 REDUCE: received {len(state['outlines'])} outlines.")
    best = max(state["outlines"], key=lambda x: x["score"])
    print(f"🏆 Best approach: '{best['approach']}' (score: {best['score']})")
    return {"best_outline": best["preview"]}


builder = StateGraph(OverallState)
builder.add_node("generate_approaches", generate_approaches)
builder.add_node("write_outline",       write_outline)       # MAP worker
builder.add_node("pick_best_outline",   pick_best_outline)   # REDUCE
builder.add_edge(START,                   "generate_approaches")
builder.add_conditional_edges("generate_approaches", dispatch_workers, ["write_outline"])
builder.add_edge("write_outline",       "pick_best_outline")
builder.add_edge("pick_best_outline",   END)

app = builder.compile()
