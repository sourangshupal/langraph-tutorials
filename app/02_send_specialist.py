"""
Graph 2: Send API — Different Node Per Item (Specialist Routing)
Concept: Each Send() can target a DIFFERENT node.
         A billing ticket goes to a billing agent, a tech ticket to a tech agent.
         Critical tickets of any type get escalated immediately.
"""

import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class OverallState(TypedDict):
    tickets: list[dict]
    resolved: Annotated[list[str], operator.add]


class TicketState(TypedDict):
    ticket_id: str
    message: str
    priority: str


def handle_billing(state: TicketState):
    print(f"  💳 BILLING  agent → ticket {state['ticket_id']}: '{state['message'][:30]}'")
    return {"resolved": [f"[BILLING]  {state['ticket_id']} resolved"]}


def handle_tech(state: TicketState):
    print(f"  🔧 TECH     agent → ticket {state['ticket_id']}: '{state['message'][:30]}'")
    return {"resolved": [f"[TECH]     {state['ticket_id']} resolved"]}


def handle_escalation(state: TicketState):
    print(f"  🚨 ESCALATE agent → ticket {state['ticket_id']}: '{state['message'][:30]}' [PRIORITY: {state['priority']}]")
    return {"resolved": [f"[ESCALATE] {state['ticket_id']} escalated to manager"]}


def load_tickets(state: OverallState):
    tickets = [
        {"ticket_id": "T001", "type": "billing",  "priority": "low",      "message": "I was charged twice this month"},
        {"ticket_id": "T002", "type": "tech",      "priority": "medium",   "message": "App crashes on startup"},
        {"ticket_id": "T003", "type": "billing",   "priority": "critical", "message": "Fraudulent charge on account"},
        {"ticket_id": "T004", "type": "tech",      "priority": "low",      "message": "Dark mode not working"},
        {"ticket_id": "T005", "type": "tech",      "priority": "critical", "message": "Data loss after update"},
    ]
    print(f"📥 Loaded {len(tickets)} support tickets.")
    return {"tickets": tickets}


def dispatch_tickets(state: OverallState) -> list[Send]:
    """KEY: each ticket routes to a DIFFERENT specialist node."""
    sends = []
    for t in state["tickets"]:
        worker_state = {
            "ticket_id": t["ticket_id"],
            "message":   t["message"],
            "priority":  t["priority"],
        }
        if t["priority"] == "critical":
            sends.append(Send("handle_escalation", worker_state))
        elif t["type"] == "billing":
            sends.append(Send("handle_billing", worker_state))
        else:
            sends.append(Send("handle_tech", worker_state))
    print(f"\n🚦 Dispatching {len(sends)} tickets to different specialist nodes in parallel...")
    return sends


def report(state: OverallState):
    print(f"\n📊 All {len(state['resolved'])} tickets resolved:")
    for r in sorted(state["resolved"]):
        print(f"   {r}")
    return {}


builder = StateGraph(OverallState)
builder.add_node("load_tickets",      load_tickets)
builder.add_node("handle_billing",    handle_billing)
builder.add_node("handle_tech",       handle_tech)
builder.add_node("handle_escalation", handle_escalation)
builder.add_node("report",            report)
builder.add_edge(START, "load_tickets")
builder.add_conditional_edges(
    "load_tickets", dispatch_tickets,
    ["handle_billing", "handle_tech", "handle_escalation"],
)
builder.add_edge("handle_billing",    "report")
builder.add_edge("handle_tech",       "report")
builder.add_edge("handle_escalation", "report")
builder.add_edge("report", END)

app = builder.compile()
