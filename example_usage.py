"""Example usage for Autonomous Support Ticket Triage & SOP Workflow Executor."""
from client import SupportTicketSOPExecutor

if __name__ == "__main__":
    ticket_1 = {
        "id": "tkt_501",
        "subject": "Charged twice on my credit card!",
        "body": "Hi, I noticed a duplicate charge on my latest invoice. Please refund immediately.",
    }
    crm_1 = {
        "customer_id": "cust_88",
        "has_duplicate_charge": True,
        "disputed_amount": 49.00,
    }

    res1 = SupportTicketSOPExecutor.execute_sop_workflow(ticket_1, crm_1)
    print("Ticket 1 Status:", res1["resolution_status"], "| Deflected:", res1["deflected"])
    print("SOP Steps:", " -> ".join(res1["sop_steps_executed"]))
    print("Reply:", res1.get("customer_reply"))
