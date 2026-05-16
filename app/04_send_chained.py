"""
Graph 4: Send API — Chained / Two-Level Fan-Out
Concept: Wave 1 workers each fan out into Wave 2 workers.
         KEY rule: a node cannot both return a dict AND return [Send(...)].
         Fix: introduce an intermediate fan-in node (collect_depts) that
         gathers Wave 1 results, then a separate dispatch function for Wave 2.

Flow:
  start_audit
      → [dispatch_departments] → audit_department ×3  (Wave 1 parallel)
                                       ↓ fan-in
                                 collect_depts
                                       ↓ [dispatch_employees]
                                 audit_employee ×9  (Wave 2 parallel)
                                       ↓ fan-in
                                 compile_report → END
"""

import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class AuditState(TypedDict):
    company:   str
    dept_data: Annotated[list[dict], operator.add]
    audit_log: Annotated[list[str],  operator.add]


class DeptState(TypedDict):
    company:   str
    dept:      str
    employees: list[str]


class EmpState(TypedDict):
    company:  str
    dept:     str
    employee: str


def start_audit(state: AuditState):
    print(f"🏢 Starting HR audit for: {state['company']}")
    return {"audit_log": [f"Audit started for {state['company']}"]}


def dispatch_departments(state: AuditState) -> list[Send]:
    """Wave 1 fan-out: one Send per department."""
    departments = {
        "Engineering": ["Alice", "Bob", "Charlie"],
        "Marketing":   ["Diana", "Eve"],
        "Finance":     ["Frank", "Grace", "Henry", "Ivy"],
    }
    print(f"\n  📂 Fan-out LEVEL 1: dispatching {len(departments)} dept auditors in parallel...")
    return [
        Send("audit_department", {
            "company":   state["company"],
            "dept":      dept,
            "employees": emps,
        })
        for dept, emps in departments.items()
    ]


def audit_department(state: DeptState):
    """Wave 1 worker: returns a dict (stores dept data for Wave 2 dispatch)."""
    print(f"  🗂  [{state['dept']}] auditing dept — {len(state['employees'])} employees found")
    return {
        "dept_data": [{
            "company":   state["company"],
            "dept":      state["dept"],
            "employees": state["employees"],
        }],
        "audit_log": [f"Dept audited: {state['dept']} ({len(state['employees'])} employees)"],
    }


def collect_depts(state: AuditState):
    """Intermediate fan-in: runs after ALL Wave 1 workers finish."""
    total = sum(len(d["employees"]) for d in state["dept_data"])
    print(f"\n  ✅ All {len(state['dept_data'])} depts collected. Total employees: {total}")
    return {}


def dispatch_employees(state: AuditState) -> list[Send]:
    """Wave 2 fan-out: one Send per employee, read from Wave 1 results."""
    sends = [
        Send("audit_employee", {
            "company":  d["company"],
            "dept":     d["dept"],
            "employee": emp,
        })
        for d in state["dept_data"]
        for emp in d["employees"]
    ]
    print(f"  📂 Fan-out LEVEL 2: dispatching {len(sends)} employee auditors in parallel...")
    return sends


def audit_employee(state: EmpState):
    entry = f"✓ {state['company']} | {state['dept']:12s} | {state['employee']}"
    print(f"    👤 {entry}")
    return {"audit_log": [entry]}


def compile_report(state: AuditState):
    emp_logs = [l for l in state["audit_log"] if l.startswith("✓")]
    print(f"\n📋 AUDIT COMPLETE — {len(emp_logs)} employees audited:")
    for log in sorted(emp_logs):
        print(f"   {log}")
    return {}


builder = StateGraph(AuditState)
builder.add_node("start_audit",      start_audit)
builder.add_node("audit_department", audit_department)
builder.add_node("collect_depts",    collect_depts)
builder.add_node("audit_employee",   audit_employee)
builder.add_node("compile_report",   compile_report)

builder.add_edge(START, "start_audit")
builder.add_conditional_edges("start_audit",   dispatch_departments, ["audit_department"])
builder.add_edge("audit_department",           "collect_depts")
builder.add_conditional_edges("collect_depts", dispatch_employees,   ["audit_employee"])
builder.add_edge("audit_employee",             "compile_report")
builder.add_edge("compile_report",             END)

app = builder.compile()
