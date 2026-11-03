"""Deterministic policy engine: the final authority on every decision.

The LLM only extracts what the customer wants (intent and merchant) and writes
the explanation. Whether a refund is approved, rejected or escalated is decided
here, in plain code, and each decision cites the policy clause it applied
(see policies/*.txt).
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime

APPROVE = "APPROVE"
REJECT = "REJECT"
ESCALATE = "ESCALATE"
AWAITING_CLARIFICATION = "AWAITING_CLARIFICATION"

VELOCITY_WINDOW_SECONDS = 120
HIGH_VALUE_THRESHOLD = 500.00
LOCKED_STATUSES = {"FRAUD_LOCK", "SUSPENDED"}
REVIEW_STATUSES = {"UNDER_REVIEW"}
LOCKED_FULFILLMENT = {"shipped", "completed", "finalized"}
COLLECTION_FLAGS = {"past_due", "collection_pending"}
DIGITAL_SUBSCRIPTION_MERCHANTS = {"netflix", "spotify"}

REFUND_INTENTS = {"refund"}
FRAUD_INTENTS = {"fraud"}
CANCEL_INTENTS = {"subscription", "order_cancellation"}
KNOWN_INTENTS = REFUND_INTENTS | FRAUD_INTENTS | CANCEL_INTENTS


@dataclass
class PolicyDecision:
    decision: str
    clause: str | None
    reasons: list[str] = field(default_factory=list)
    target_txn_ids: list[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def _ts(txn):
    return datetime.fromisoformat(txn["timestamp"].replace("Z", "+00:00"))


def _successful(txns):
    return [t for t in txns if t.get("status") == "SUCCESS"]


def find_rapid_clusters(transactions):
    """Find repeated charges: same merchant and amount, all inside the velocity window.

    Returns the largest such cluster for each merchant/amount pair that has at least two charges.
    """
    groups = {}
    for txn in _successful(transactions):
        groups.setdefault((txn["merchant"].lower(), txn["amount"]), []).append(txn)

    clusters = []
    for txns in groups.values():
        txns.sort(key=_ts)
        best = []
        for i, first in enumerate(txns):
            window = [t for t in txns[i:] if (_ts(t) - _ts(first)).total_seconds() <= VELOCITY_WINDOW_SECONDS]
            if len(window) > len(best):
                best = window
        if len(best) >= 2:
            clusters.append(best)
    return clusters


def _in_collections(transactions):
    for txn in transactions:
        flags = {str(txn.get("status", "")).lower(), str(txn.get("failure_reason", "")).lower()}
        if flags & COLLECTION_FLAGS:
            return True
    return False


def _ids(txns):
    return [t["txn_id"] for t in txns]


def evaluate(intent, user, transactions, merchant=None, injection=None):
    """Apply the policy rules in priority order and return a PolicyDecision."""
    if injection:
        return PolicyDecision(REJECT, "PROMPT-INJECTION-DEFENSE-GUARD", [f"Prompt-injection pattern detected: '{injection}'"])

    if user is None:
        return PolicyDecision(REJECT, "ACCOUNT-STATUS-GATE", ["User ID does not match any customer record"])

    if intent not in KNOWN_INTENTS:
        return PolicyDecision(AWAITING_CLARIFICATION, None, ["Request type could not be identified"])

    status = user.get("status", "ACTIVE")
    if status in LOCKED_STATUSES:
        return PolicyDecision(REJECT, "ACCOUNT-STATUS-GATE", [f"Account status is {status}"])

    targets = transactions
    if merchant:
        targets = [t for t in transactions if t["merchant"].lower() == merchant.lower()]
        if not targets:
            return PolicyDecision(REJECT, "LEDGER-MATCH-REQUIREMENT", [f"No {merchant} charge in this customer's ledger"])
    elif intent == "subscription":
        # "Cancel my subscription" with no merchant means their recurring digital plans.
        targets = [t for t in transactions if t["merchant"].lower() in DIGITAL_SUBSCRIPTION_MERCHANTS]
        if not targets:
            return PolicyDecision(REJECT, "SUBSCRIPTION-CANCELLATION-RULE", ["No active subscription found to cancel"])
    if not targets:
        return PolicyDecision(REJECT, "LEDGER-MATCH-REQUIREMENT", ["Customer has no transactions on record"])

    clusters = find_rapid_clusters(targets)
    attack = next((c for c in clusters if len(c) >= 3), None)
    if attack:
        return PolicyDecision(
            REJECT, "VELOCITY-ATTACK-FLAG",
            [f"{len(attack)} identical {attack[0]['merchant']} charges within {VELOCITY_WINDOW_SECONDS}s: treated as automated card testing"],
            _ids(attack),
        )

    if status in REVIEW_STATUSES:
        return PolicyDecision(ESCALATE, "ACCOUNT-STATUS-GATE", [f"Account status is {status}"], _ids(targets))

    high_value = [t for t in _successful(targets) if t["amount"] >= HIGH_VALUE_THRESHOLD]
    if high_value:
        return PolicyDecision(
            ESCALATE, "HIGH-VALUE-COMPLIANCE-LIMIT",
            [f"{t['txn_id']} ({t['merchant']}, ${t['amount']:.2f}) is at or above ${HIGH_VALUE_THRESHOLD:.2f}" for t in high_value],
            _ids(high_value),
        )

    if intent in REFUND_INTENTS | FRAUD_INTENTS:
        pair = next((c for c in clusters if len(c) == 2), None)
        if pair:
            return PolicyDecision(
                ESCALATE, "DUPLICATE-CHARGE-EXCEPTION",
                [f"Two identical {pair[0]['merchant']} charges of ${pair[0]['amount']:.2f} within {VELOCITY_WINDOW_SECONDS}s: likely double billing"],
                _ids(pair),
            )

    if intent in FRAUD_INTENTS:
        return PolicyDecision(ESCALATE, "UNAUTHORIZED-CHARGE-REPORT", ["Customer reports an unauthorized charge with no velocity pattern"], _ids(targets))

    if intent in REFUND_INTENTS:
        charged = _successful(targets)
        if not charged:
            return PolicyDecision(REJECT, "REFUND-ELIGIBILITY-MATRIX", ["No successful charge to refund"], _ids(targets))
        locked = [t for t in charged if str(t.get("fulfillment", "")).lower() in LOCKED_FULFILLMENT]
        if len(locked) == len(charged):
            return PolicyDecision(REJECT, "REFUND-ELIGIBILITY-MATRIX", [f"{t['txn_id']} is already {t['fulfillment']}" for t in locked], _ids(locked))
        return PolicyDecision(ESCALATE, "REFUND-ELIGIBILITY-MATRIX", ["Disputed charge with no binary rule: manual review"], _ids(charged))

    # Cancellations (subscriptions and physical orders)
    if _in_collections(transactions):
        return PolicyDecision(REJECT, "SUBSCRIPTION-CANCELLATION-RULE", ["Account has a past-due or collection-pending invoice (Case C)"])

    charged = _successful(targets)
    digital = [t for t in charged if t["merchant"].lower() in DIGITAL_SUBSCRIPTION_MERCHANTS]
    physical = [t for t in charged if t["merchant"].lower() not in DIGITAL_SUBSCRIPTION_MERCHANTS]

    if intent == "order_cancellation":
        if not physical:
            return PolicyDecision(ESCALATE, "SUBSCRIPTION-CANCELLATION-RULE", ["Order cancellation requested but the ledger only shows digital subscriptions (Case B)"], _ids(digital))
        open_orders = [t for t in physical if str(t.get("fulfillment", "")).lower() not in LOCKED_FULFILLMENT]
        if not open_orders:
            return PolicyDecision(REJECT, "REFUND-ELIGIBILITY-MATRIX", [f"{t['txn_id']} is already {t.get('fulfillment')}" for t in physical], _ids(physical))
        return PolicyDecision(APPROVE, "SUBSCRIPTION-CANCELLATION-RULE", ["Open order with no past-due invoices (Case A)"], _ids(open_orders))

    if not digital:
        return PolicyDecision(REJECT, "SUBSCRIPTION-CANCELLATION-RULE", ["No active subscription found to cancel"])
    return PolicyDecision(APPROVE, "SUBSCRIPTION-CANCELLATION-RULE", ["Active subscription with no past-due invoices (Case A)"], _ids(digital))
