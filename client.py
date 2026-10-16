"""Autonomous Support Ticket Triage and SOP Workflow Executor.
100% Python Standard Library.
"""

from typing import List, Dict, Any
import re


class SupportTicketSOPExecutor:
    """Classifies incoming customer support tickets, executes multi-step Standard Operating Procedure (SOP)
    decision trees against CRM context, and routes between autonomous deflection and human escalation."""

    INTENT_KEYWORDS = {
        "billing_dispute": ["overcharged", "duplicate charge", "invoice", "billing", "charged twice"],
        "subscription_cancel": ["cancel subscription", "unsubscribe", "stop renewal", "cancel my plan"],
        "account_lockout": ["locked out", "reset password", "mfa", "2fa", "cannot login", "login issue"],
        "shipment_delay": ["where is my order", "tracking", "delayed", "lost package", "not delivered"],
    }

    @classmethod
    def classify_ticket(cls, subject: str, body: str) -> Dict[str, Any]:
        """Determines primary ticket intent and urgency severity from customer message."""
        combined = f"{subject} {body}".lower()
        detected_intent = "general_inquiry"
        matched_keywords = []

        for intent, kws in cls.INTENT_KEYWORDS.items():
            hits = [kw for kw in kws if kw in combined]
            if hits:
                detected_intent = intent
                matched_keywords = hits
                break

        urgent_signals = ["urgent", "immediately", "lawyer", "fraud", "production down", "outage"]
        urgency = "high" if any(u in combined for u in urgent_signals) else "normal"

        return {
            "intent": detected_intent,
            "urgency": urgency,
            "matched_signals": matched_keywords,
        }

    @classmethod
    def execute_sop_workflow(
        cls,
        ticket: Dict[str, Any],
        crm_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Executes deterministic SOP steps based on ticket intent and live CRM customer data."""
        classification = cls.classify_ticket(ticket.get("subject", ""), ticket.get("body", ""))
        intent = classification["intent"]
        urgency = classification["urgency"]
        steps_executed: List[str] = ["classified_ticket_intent"]

        if urgency == "high":
            steps_executed.append("flagged_high_urgency_priority_queue")

        # SOP 1: Duplicate Charge / Billing Dispute
        if intent == "billing_dispute":
            steps_executed.append("inspected_crm_recent_transactions")
            duplicate_tx = bool(crm_record.get("has_duplicate_charge", False))
            disputed_amount = float(crm_record.get("disputed_amount", 0.0))

            if duplicate_tx and disputed_amount <= 150.0:
                steps_executed.append("auto_reversed_duplicate_charge")
                return {
                    "ticket_id": ticket.get("id", "tkt_unknown"),
                    "intent": intent,
                    "urgency": urgency,
                    "resolution_status": "AUTONOMOUSLY_RESOLVED",
                    "deflected": True,
                    "sop_steps_executed": steps_executed,
                    "automated_action": {"type": "refund_duplicate_tx", "amount": disputed_amount},
                    "customer_reply": f"We verified a duplicate charge of ${disputed_amount:.2f} on your account and have automatically issued a full reversal.",
                }
            steps_executed.append("routed_to_billing_specialist")
            return {
                "ticket_id": ticket.get("id", "tkt_unknown"),
                "intent": intent,
                "urgency": urgency,
                "resolution_status": "ESCALATED_TO_HUMAN",
                "deflected": False,
                "sop_steps_executed": steps_executed,
                "escalation_reason": "No clear duplicate transaction or amount exceeds $150 autonomous cap.",
            }

        # SOP 2: Subscription Cancellation with Retention Offer
        if intent == "subscription_cancel":
            steps_executed.append("checked_contract_lock_in_and_tenure")
            is_annual_contract = bool(crm_record.get("is_annual_contract", False))
            months_active = int(crm_record.get("months_active", 1))

            if is_annual_contract:
                steps_executed.append("routed_to_account_executive")
                return {
                    "ticket_id": ticket.get("id", "tkt_unknown"),
                    "intent": intent,
                    "urgency": urgency,
                    "resolution_status": "ESCALATED_TO_HUMAN",
                    "deflected": False,
                    "sop_steps_executed": steps_executed,
                    "escalation_reason": "Customer is on an active annual enterprise contract.",
                }

            steps_executed.append("processed_self_serve_cancellation")
            return {
                "ticket_id": ticket.get("id", "tkt_unknown"),
                "intent": intent,
                "urgency": urgency,
                "resolution_status": "AUTONOMOUSLY_RESOLVED",
                "deflected": True,
                "sop_steps_executed": steps_executed,
                "automated_action": {
                    "type": "cancel_monthly_renewal",
                    "retention_offer_attached": months_active >= 3,
                },
                "customer_reply": "Your monthly subscription auto-renewal has been canceled. Your access remains active through the end of the current billing cycle.",
            }

        # SOP 3: Account Lockout
        if intent == "account_lockout":
            steps_executed.append("verified_identity_status")
            if crm_record.get("identity_verified", False):
                steps_executed.append("dispatched_password_reset_and_mfa_unlock")
                return {
                    "ticket_id": ticket.get("id", "tkt_unknown"),
                    "intent": intent,
                    "urgency": urgency,
                    "resolution_status": "AUTONOMOUSLY_RESOLVED",
                    "deflected": True,
                    "sop_steps_executed": steps_executed,
                    "automated_action": {"type": "trigger_sso_reset_link"},
                    "customer_reply": "We have unlocked your account session and sent a verified password reset link to your registered email.",
                }

        # Default fallback
        steps_executed.append("queued_for_tier1_support")
        return {
            "ticket_id": ticket.get("id", "tkt_unknown"),
            "intent": intent,
            "urgency": urgency,
            "resolution_status": "ESCALATED_TO_HUMAN",
            "deflected": False,
            "sop_steps_executed": steps_executed,
            "escalation_reason": "Standard Operating Procedure requires human verification for this request.",
        }
