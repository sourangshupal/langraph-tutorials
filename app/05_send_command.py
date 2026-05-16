"""
Graph 5: Send API + Command — Workers Route to Different Downstream Nodes
Concept: Combine Send (fan-out) with Command(goto=...) inside the worker.
         After scoring, each chunk dynamically routes to a different next node:
         high score → use_chunk, low score → discard_chunk.
         This is the pattern used in RAG pipelines to filter irrelevant chunks.
"""

import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, Command


class RAGState(TypedDict):
    query:     str
    chunks:    list[dict]
    used:      Annotated[list[str], operator.add]
    discarded: Annotated[list[str], operator.add]
    answer:    str


class ChunkState(TypedDict):
    query:    str
    chunk_id: str
    text:     str
    score:    float


def retrieve_chunks(state: RAGState):
    chunks = [
        {"chunk_id": "C1", "text": "LangGraph supports stateful multi-agent workflows",    "score": 0.91},
        {"chunk_id": "C2", "text": "The weather in Paris is 22 degrees today",             "score": 0.12},
        {"chunk_id": "C3", "text": "Send API enables dynamic parallel node dispatch",      "score": 0.88},
        {"chunk_id": "C4", "text": "Recipe for pasta carbonara requires eggs and cheese",  "score": 0.08},
        {"chunk_id": "C5", "text": "Checkpointers enable persistence across graph runs",   "score": 0.76},
        {"chunk_id": "C6", "text": "Stock price of AAPL closed at $189 yesterday",        "score": 0.31},
    ]
    print(f"📥 Retrieved {len(chunks)} chunks for query: '{state['query']}'")
    return {"chunks": chunks}


def dispatch_scorers(state: RAGState) -> list[Send]:
    print(f"\n⚡ Dispatching {len(state['chunks'])} chunk scorers in parallel...")
    return [
        Send("score_chunk", {
            "query":    state["query"],
            "chunk_id": c["chunk_id"],
            "text":     c["text"],
            "score":    c["score"],
        })
        for c in state["chunks"]
    ]


def score_chunk(state: ChunkState) -> Command[Literal["use_chunk", "discard_chunk"]]:
    """Worker: scores one chunk, then routes to use_chunk or discard_chunk via Command."""
    threshold = 0.6
    if state["score"] >= threshold:
        print(f"  ✅ {state['chunk_id']} score={state['score']:.2f} → use_chunk")
        return Command(
            update={"used": [f"{state['chunk_id']}: {state['text'][:45]}..."]},
            goto="use_chunk",
        )
    else:
        print(f"  ❌ {state['chunk_id']} score={state['score']:.2f} → discard_chunk")
        return Command(
            update={"discarded": [f"{state['chunk_id']}: score too low ({state['score']:.2f})"]},
            goto="discard_chunk",
        )


def use_chunk(state: RAGState):
    print(f"  📎 use_chunk: adding to context window")
    return {}


def discard_chunk(state: RAGState):
    print(f"  🗑  discard_chunk: dropping from context")
    return {}


def generate_answer(state: RAGState):
    print(f"\n🤖 Generating answer from {len(state['used'])} high-quality chunks")
    print(f"   Used    : {[c.split(':')[0] for c in state['used']]}")
    print(f"   Discarded: {[c.split(':')[0] for c in state['discarded']]}")
    answer = f"Answer using {len(state['used'])} relevant chunks: [LLM response here]"
    return {"answer": answer}


builder = StateGraph(RAGState)
builder.add_node("retrieve_chunks", retrieve_chunks)
builder.add_node("score_chunk",     score_chunk)
builder.add_node("use_chunk",       use_chunk)
builder.add_node("discard_chunk",   discard_chunk)
builder.add_node("generate_answer", generate_answer)
builder.add_edge(START, "retrieve_chunks")
builder.add_conditional_edges("retrieve_chunks", dispatch_scorers, ["score_chunk"])
builder.add_edge("use_chunk",       "generate_answer")
builder.add_edge("discard_chunk",   "generate_answer")
builder.add_edge("generate_answer", END)

app = builder.compile()
