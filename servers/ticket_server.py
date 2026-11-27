"""A support-ticket MCP server built with FastMCP.

Run over stdio (default):        python servers/ticket_server.py
Run over Streamable HTTP:        see Notebook 12, Part 3
Inspect with the MCP Inspector:  npx @modelcontextprotocol/inspector python servers/ticket_server.py
"""
from fastmcp import FastMCP

mcp = FastMCP("Ticket Server")

# ── A tiny in-memory "database" ───────────────────────────────────────────────
TICKETS = {
    1024: {"subject": "Charged twice this month", "category": "billing", "status": "open", "priority": "high"},
    1025: {"subject": "App crashes on iOS 17", "category": "technical", "status": "open", "priority": "high"},
    1026: {"subject": "Add dark mode", "category": "feature", "status": "closed", "priority": "low"},
    1027: {"subject": "Password reset not working", "category": "technical", "status": "in-progress", "priority": "medium"},
}


@mcp.tool
def get_ticket(ticket_id: int) -> dict:
    """Look up a support ticket by its ID."""
    ticket = TICKETS.get(ticket_id)
    if ticket is None:
        raise ValueError(f"Ticket {ticket_id} not found")
    return {"ticket_id": ticket_id, **ticket}


@mcp.tool
def list_open_tickets() -> list[dict]:
    """List all tickets whose status is 'open'."""
    return [{"ticket_id": tid, **t} for tid, t in TICKETS.items() if t["status"] == "open"]


@mcp.tool
def create_ticket(subject: str, category: str, priority: str = "medium") -> dict:
    """Create a new support ticket. Category must be billing, technical, feature, or general."""
    if category not in ("billing", "technical", "feature", "general"):
        raise ValueError(f"Invalid category: {category}")
    new_id = max(TICKETS) + 1
    TICKETS[new_id] = {"subject": subject, "category": category, "status": "open", "priority": priority}
    return {"ticket_id": new_id, **TICKETS[new_id]}


@mcp.resource("tickets://open")
def open_tickets_summary() -> str:
    """Live summary of all open tickets."""
    open_tickets = [
        f"#{tid} {t['subject']} ({t['priority']})"
        for tid, t in TICKETS.items()
        if t["status"] == "open"
    ]
    return "Open tickets:\n" + "\n".join(open_tickets)


@mcp.prompt
def triage_ticket(ticket_text: str) -> str:
    """Create a triage prompt for a raw customer message."""
    return (
        "Triage this customer message. Classify it as billing, technical, feature, or general, "
        "assign a priority (low/medium/high), and suggest the first response.\n\n"
        f"Message: {ticket_text}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
