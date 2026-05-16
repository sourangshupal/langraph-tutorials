"""
Graph 7: Multi-Agent System — Subgraph Agents + Command Orchestration
Concept: Two specialist agents (WebAgent, CodeAgent) are compiled as
         subgraphs and registered as nodes in the orchestrator graph.
         The orchestrator uses Command(goto=...) to route each task
         to the right agent based on simple keyword matching.
         (No LLM calls — pure structural routing for demo purposes.)

Flow:
  START → orchestrator → web_agent (subgraph)  → synthesizer → END
                       → code_agent (subgraph) → synthesizer → END
"""

import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command


# ── Shared state across all agents ────────────────────────────────────────────

class AgentState(TypedDict):
    task:   str
    log:    Annotated[list[str], operator.add]
    result: str


# ── Sub-Agent 1: Web Research Agent ───────────────────────────────────────────

class WebState(TypedDict):
    task:   str
    log:    Annotated[list[str], operator.add]
    result: str


def web_search(state: WebState):
    print("  🌐 WebAgent: searching the web...")
    return {"log": ["web_search completed"]}


def web_summarize(state: WebState):
    print("  🌐 WebAgent: summarizing results...")
    summary = f"[WEB RESULT] Found 5 sources about: {state['task']}"
    return {"result": summary, "log": ["web_summarize completed"]}


web_builder = StateGraph(WebState)
web_builder.add_node("web_search",    web_search)
web_builder.add_node("web_summarize", web_summarize)
web_builder.add_edge(START,            "web_search")
web_builder.add_edge("web_search",    "web_summarize")
web_builder.add_edge("web_summarize", END)
web_agent = web_builder.compile()


# ── Sub-Agent 2: Code Agent ────────────────────────────────────────────────────

class CodeState(TypedDict):
    task:   str
    log:    Annotated[list[str], operator.add]
    result: str


def write_code(state: CodeState):
    print("  💻 CodeAgent: writing code...")
    return {"log": ["write_code completed"]}


def test_code(state: CodeState):
    print("  💻 CodeAgent: running tests...")
    code_out = f"[CODE RESULT] Python solution for: {state['task']}"
    return {"result": code_out, "log": ["test_code completed"]}


code_builder = StateGraph(CodeState)
code_builder.add_node("write_code", write_code)
code_builder.add_node("test_code",  test_code)
code_builder.add_edge(START,        "write_code")
code_builder.add_edge("write_code", "test_code")
code_builder.add_edge("test_code",  END)
code_agent = code_builder.compile()


# ── Orchestrator + Parent Graph ────────────────────────────────────────────────

def orchestrator(state: AgentState) -> Command[Literal["web_agent", "code_agent"]]:
    """Routes task to the right specialist via Command — no LLM needed here."""
    task = state["task"].lower()
    print(f"🎯 Orchestrator received: '{state['task']}'")
    if "code" in task or "python" in task or "function" in task:
        print("  → Routing to CODE AGENT")
        return Command(
            update={"log": ["orchestrator: delegated to code_agent"]},
            goto="code_agent",
        )
    else:
        print("  → Routing to WEB AGENT")
        return Command(
            update={"log": ["orchestrator: delegated to web_agent"]},
            goto="web_agent",
        )


def synthesizer(state: AgentState):
    print(f"\n📋 Synthesizer received result: {state['result'][:60]}...")
    print(f"   Full log: {state['log']}")
    return {}


builder = StateGraph(AgentState)
builder.add_node("orchestrator", orchestrator)
builder.add_node("web_agent",    web_agent)    # subgraph as node
builder.add_node("code_agent",   code_agent)   # subgraph as node
builder.add_node("synthesizer",  synthesizer)
builder.add_edge(START,          "orchestrator")
builder.add_edge("web_agent",    "synthesizer")
builder.add_edge("code_agent",   "synthesizer")
builder.add_edge("synthesizer",  END)

app = builder.compile()
