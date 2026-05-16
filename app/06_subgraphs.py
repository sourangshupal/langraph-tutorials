"""
Graph 6: Subgraphs — Graphs Inside Graphs
Concept: A compiled graph can be used as a node inside a parent graph.
         Each subgraph has its own private state keys; keys with matching
         names flow automatically between parent and subgraph.

         Subgraph A (PreprocState): cleans text, counts chars
         Subgraph B (AnalysisState): extracts keywords, scores sentiment
         Parent (ParentState): chains A → B → format as a linear pipeline.

State sharing rule:
  - 'text' key exists in both subgraph states AND ParentState → shared
  - 'char_count' (SubgraphA only) and 'keywords' (SubgraphB only) → private
"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


# ── Subgraph A: Preprocessing ─────────────────────────────────────────────────

class PreprocState(TypedDict):
    text:       str   # shared with parent
    char_count: int   # private — stays inside subgraph A


def clean_text(state: PreprocState):
    cleaned = state["text"].strip().lower()
    print(f"  [SubA] clean_text: '{cleaned[:40]}...'")
    return {"text": cleaned}


def count_chars(state: PreprocState):
    n = len(state["text"])
    print(f"  [SubA] count_chars: {n} chars")
    return {"char_count": n}


preproc_builder = StateGraph(PreprocState)
preproc_builder.add_node("clean_text",  clean_text)
preproc_builder.add_node("count_chars", count_chars)
preproc_builder.add_edge(START,          "clean_text")
preproc_builder.add_edge("clean_text",  "count_chars")
preproc_builder.add_edge("count_chars", END)
preproc_subgraph = preproc_builder.compile()


# ── Subgraph B: Analysis ───────────────────────────────────────────────────────

class AnalysisState(TypedDict):
    text:     str         # shared with parent
    keywords: list[str]   # private — stays inside subgraph B


def extract_keywords(state: AnalysisState):
    words = [w for w in state["text"].split() if len(w) > 5]
    print(f"  [SubB] extract_keywords: {words[:4]}")
    return {"keywords": words}


def score_sentiment(state: AnalysisState):
    pos_words = ["great", "good", "excellent", "amazing", "fantastic"]
    score     = sum(1 for w in state["keywords"] if w in pos_words)
    label     = "positive" if score > 0 else "neutral"
    print(f"  [SubB] score_sentiment: {label}")
    return {"text": f"[{label.upper()}] {state['text']}"}


analysis_builder = StateGraph(AnalysisState)
analysis_builder.add_node("extract_keywords", extract_keywords)
analysis_builder.add_node("score_sentiment",  score_sentiment)
analysis_builder.add_edge(START,               "extract_keywords")
analysis_builder.add_edge("extract_keywords", "score_sentiment")
analysis_builder.add_edge("score_sentiment",  END)
analysis_subgraph = analysis_builder.compile()


# ── Parent Graph ───────────────────────────────────────────────────────────────

class ParentState(TypedDict):
    text:   str   # shared key — both subgraphs read and write this
    result: str


def format_result(state: ParentState):
    print(f"  [Parent] Formatting result.")
    return {"result": f"DONE: {state['text']}"}


parent = StateGraph(ParentState)
parent.add_node("preprocess", preproc_subgraph)    # entire subgraph A as one node
parent.add_node("analyse",    analysis_subgraph)   # entire subgraph B as one node
parent.add_node("format",     format_result)
parent.add_edge(START,        "preprocess")
parent.add_edge("preprocess", "analyse")
parent.add_edge("analyse",    "format")
parent.add_edge("format",     END)

app = parent.compile()
