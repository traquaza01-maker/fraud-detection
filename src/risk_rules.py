from __future__ import annotations

from typing import Dict


def score_transaction(tx: Dict) -> int:
    """Return a simple fraud risk score from 0 to 100."""
    score = 0

    # High device risk signals a compromised or spoofed device.
    if tx["device_risk_score"] >= 70:
        score += 25
    elif tx["device_risk_score"] >= 40:
        score += 10

    # International transactions carry elevated cross-border fraud risk.
    if tx["is_international"] == 1:
        score += 15

    # High purchase amounts should matter.
    if tx["amount_usd"] >= 1000:
        score += 25
    elif tx["amount_usd"] >= 500:
        score += 10

    # High transaction velocity signals card testing or account takeover.
    if tx["velocity_24h"] >= 6:
        score += 20
    elif tx["velocity_24h"] >= 3:
        score += 5

    # Prior login failures can signal account takeover.
    if tx["failed_logins_24h"] >= 5:
        score += 20
    elif tx["failed_logins_24h"] >= 2:
        score += 10

    # Prior chargeback history is a strong fraud predictor.
    if tx["prior_chargebacks"] >= 2:
        score += 20
    elif tx["prior_chargebacks"] == 1:
        score += 5

    # Very new accounts are a common vector for synthetic identity and ATO fraud.
    account_age = tx.get("account_age_days", 9999)
    if account_age < 30:
        score += 15
    elif account_age < 90:
        score += 5

    # Gift cards and crypto are the top cash-out categories in payment fraud.
    if tx.get("merchant_category") in ("gift_cards", "crypto"):
        score += 15

    return max(0, min(score, 100))


def label_risk(score: int) -> str:
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"
