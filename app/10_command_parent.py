"""
Graph 10: Subgraph Escape Hatch — Command(graph=Command.PARENT)
Concept: Normally a subgraph is isolated — it cannot influence the parent
         graph's routing. With Command(graph=Command.PARENT), a node inside
         a subgraph can break out and jump to a node in the PARENT graph.

Use case: Subgraph tries to handle a task. If it's "critical", it escalates
          to the parent's escalation_handler instead of finishing normally.

Flow (normal task):
  Parent: start → subgraph_worker (subgraph runs, returns normally) → END

Flow (critical task):
  Parent: start → subgraph_worker
                      ↓ (subgraph detects "critical")
                      Command(goto="escalation_handler", graph=Command.PARENT)
                  escalation_handler → END
"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command


class ParentState(TypedDict):
    task:      str
    escalated: bool
    result:    str


class SubState(TypedDict):
    task:      str
    escalated: bool
    result:    str


# ── Subgraph ───────────────────────────────────────────────────────────────────

def process_in_subgraph(state: SubState) -> dict | Command:
    """Try to handle the task. If critical, escape to parent via Command.PARENT."""
    if "critical" in state["task"].lower():
        print("🚨 Subgraph: Task is critical — escalating to parent!")
        return Command(
            goto="escalation_handler",   # node in the PARENT graph
            graph=Command.PARENT,        # ← break out of this subgraph
            update={"escalated": True, "result": "Escalated to human review"},
        )
    result = f"✅ Subgraph handled: {state['task']}"
    print(f"✅ Subgraph: Task handled normally.")
    return {"result": result}


sub_builder = StateGraph(SubState)
sub_builder.add_node("process", process_in_subgraph)
sub_builder.add_edge(START,     "process")
sub_builder.add_edge("process", END)
subgraph = sub_builder.compile()


# ── Parent Graph ───────────────────────────────────────────────────────────────

def start_task(state: ParentState) -> dict:
    print(f"🎯 Parent: Starting task '{state['task']}'")
    return {}


def escalation_handler(state: ParentState) -> dict:
    print(f"👨‍💼 Parent: Handling escalation for '{state['task']}'")
    return {"result": f"ESCALATED: '{state['task']}' sent to human review team"}


parent_builder = StateGraph(ParentState)
parent_builder.add_node("start",              start_task)
parent_builder.add_node("subgraph_worker",    subgraph)            # subgraph as node
parent_builder.add_node("escalation_handler", escalation_handler)

parent_builder.add_edge(START,             "start")
parent_builder.add_edge("start",           "subgraph_worker")
parent_builder.add_edge("subgraph_worker", END)
parent_builder.add_edge("escalation_handler", END)

app = parent_builder.compile()
