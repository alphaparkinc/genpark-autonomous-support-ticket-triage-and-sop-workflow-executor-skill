"""MCP server for Autonomous Support Ticket Triage & SOP Workflow Executor."""
import sys
import json
from client import SupportTicketSOPExecutor


def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "classify_support_ticket",
                    "description": "Classifies support ticket intent and urgency level from subject and body text",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "subject": {"type": "string"},
                            "body": {"type": "string"},
                        },
                        "required": ["subject", "body"],
                    },
                },
                {
                    "name": "execute_ticket_sop_workflow",
                    "description": "Runs multi-step SOP decision workflow against CRM state to resolve or escalate support tickets",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "ticket": {"type": "object"},
                            "crm_record": {"type": "object"},
                        },
                        "required": ["ticket", "crm_record"],
                    },
                },
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "classify_support_ticket":
            res = SupportTicketSOPExecutor.classify_ticket(
                args.get("subject", ""),
                args.get("body", ""),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "execute_ticket_sop_workflow":
            res = SupportTicketSOPExecutor.execute_sop_workflow(
                args.get("ticket", {}),
                args.get("crm_record", {}),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
    return {"error": "Method not found"}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle_request(json.loads(line))))
            sys.stdout.flush()
