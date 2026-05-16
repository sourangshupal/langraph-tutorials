"""
Graph 3: Send API — Variable Fan-Out Count
Concept: The number of parallel workers is NOT fixed at build time.
         It is computed at runtime from the current state.
         Here: one grader per student submission — 0 to N workers.
         Workers also receive extra metadata (exam_name, total_marks)
         alongside their primary item.
"""

import operator
import random
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class ExamState(TypedDict):
    exam_name:   str
    total_marks: int
    submissions: list[dict]
    grades:      Annotated[list[dict], operator.add]


class GraderState(TypedDict):
    student_id:  str
    answers:     list[int]
    exam_name:   str
    total_marks: int


def collect_submissions(state: ExamState):
    """Simulate receiving N submissions. N is random — only known at runtime."""
    random.seed(42)
    n_students = random.randint(4, 7)
    submissions = [
        {
            "student_id": f"STU-{i+1:03d}",
            "answers":    [random.randint(0, 10) for _ in range(5)],
        }
        for i in range(n_students)
    ]
    print(f"📋 Collected {n_students} submissions for '{state['exam_name']}'")
    return {"submissions": submissions}


def dispatch_graders(state: ExamState) -> list[Send]:
    """Variable fan-out: one Send per submission, count only known here."""
    n = len(state["submissions"])
    print(f"⚡ Spawning {n} grader workers dynamically...")
    return [
        Send("grade_submission", {
            "student_id":  sub["student_id"],
            "answers":     sub["answers"],
            "exam_name":   state["exam_name"],
            "total_marks": state["total_marks"],
        })
        for sub in state["submissions"]
    ]


def grade_submission(state: GraderState):
    raw   = sum(state["answers"])
    pct   = round(raw / state["total_marks"] * 100, 1)
    grade = "A" if pct >= 80 else "B" if pct >= 65 else "C" if pct >= 50 else "F"
    result = {"student": state["student_id"], "score": raw, "pct": pct, "grade": grade}
    print(f"  📝 {state['student_id']}: {raw}/{state['total_marks']} = {pct}% → Grade {grade}")
    return {"grades": [result]}


def compute_stats(state: ExamState):
    grades = state["grades"]
    avg    = round(sum(g["pct"] for g in grades) / len(grades), 1)
    top    = max(grades, key=lambda x: x["pct"])
    dist: dict = {}
    for g in grades:
        dist[g["grade"]] = dist.get(g["grade"], 0) + 1
    print(f"\n📊 {state['exam_name']} Results ({len(grades)} students):")
    print(f"   Class average : {avg}%")
    print(f"   Top student   : {top['student']} ({top['pct']}%)")
    print(f"   Grade dist    : {dist}")
    return {}


builder = StateGraph(ExamState)
builder.add_node("collect_submissions", collect_submissions)
builder.add_node("grade_submission",    grade_submission)
builder.add_node("compute_stats",       compute_stats)
builder.add_edge(START, "collect_submissions")
builder.add_conditional_edges("collect_submissions", dispatch_graders, ["grade_submission"])
builder.add_edge("grade_submission", "compute_stats")
builder.add_edge("compute_stats",    END)

app = builder.compile()
