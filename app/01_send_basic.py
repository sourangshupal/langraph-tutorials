"""
Graph 1: Send API — Basic Parallel Fan-Out
Concept: Use Send() to process a list of items in parallel.
         Results accumulate via Annotated[list, operator.add].
"""

import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class BatchState(TypedDict):
    items: list
    results: Annotated[list, operator.add]


class ItemState(TypedDict):
    item: str


def distribute_work(state: BatchState):
    """Dispatch one parallel worker per item via Send."""
    print(f"📦 Distributing {len(state['items'])} items for processing")
    return [Send("process_item", {"item": item}) for item in state["items"]]


def process_item(state: ItemState) -> dict:
    """Worker: processes a single item (runs in parallel)."""
    item = state["item"]
    print(f"  ⚙️  Processing: {item}")
    result = f"Processed: {item.upper()}"
    return {"results": [result]}


builder = StateGraph(BatchState)
builder.add_node("process_item", process_item)
builder.add_conditional_edges(START, distribute_work, ["process_item"])
builder.add_edge("process_item", END)

app = builder.compile()
