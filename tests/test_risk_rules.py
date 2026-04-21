from risk_rules import label_risk, score_transaction


def _base_tx(**overrides):
    """Minimal clean transaction that scores 0 — every field below every threshold."""
    tx = {
        "device_risk_score": 10,
        "is_international": 0,
        "amount_usd": 50,
        "velocity_24h": 1,
        "failed_logins_24h": 0,
        "prior_chargebacks": 0,
        "account_age_days": 500,
        "merchant_category": "grocery",
    }
    tx.update(overrides)
    return tx


# ---------------------------------------------------------------------------
# label_risk — exact boundaries
# ---------------------------------------------------------------------------

def test_label_risk_low():
    assert label_risk(0) == "low"
    assert label_risk(10) == "low"
    assert label_risk(29) == "low"


def test_label_risk_medium_lower_boundary():
    assert label_risk(30) == "medium"


def test_label_risk_medium():
    assert label_risk(35) == "medium"
    assert label_risk(59) == "medium"


def test_label_risk_high_lower_boundary():
    assert label_risk(60) == "high"


def test_label_risk_high():
    assert label_risk(75) == "high"
    assert label_risk(100) == "high"


# ---------------------------------------------------------------------------
# device_risk_score — exact points, thresholds, below-threshold
# ---------------------------------------------------------------------------

def test_device_risk_high_exact_points():
    assert score_transaction(_base_tx(device_risk_score=70)) == 25


def test_device_risk_high_above_threshold():
    assert score_transaction(_base_tx(device_risk_score=99)) == 25


def test_device_risk_just_below_high_threshold_uses_medium():
    assert score_transaction(_base_tx(device_risk_score=69)) == 10


def test_device_risk_medium_exact_points():
    assert score_transaction(_base_tx(device_risk_score=40)) == 10


def test_device_risk_just_below_medium_threshold_no_points():
    assert score_transaction(_base_tx(device_risk_score=39)) == 0


def test_device_risk_low_no_points():
    assert score_transaction(_base_tx(device_risk_score=10)) == 0


# ---------------------------------------------------------------------------
# is_international — exact points, off state
# ---------------------------------------------------------------------------

def test_international_exact_points():
    assert score_transaction(_base_tx(is_international=1)) == 15


def test_domestic_no_points():
    assert score_transaction(_base_tx(is_international=0)) == 0


# ---------------------------------------------------------------------------
# amount_usd — exact points, thresholds, below-threshold
# ---------------------------------------------------------------------------

def test_amount_high_exact_points():
    assert score_transaction(_base_tx(amount_usd=1000)) == 25


def test_amount_high_above_threshold():
    assert score_transaction(_base_tx(amount_usd=5000)) == 25


def test_amount_just_below_high_threshold_uses_medium():
    assert score_transaction(_base_tx(amount_usd=999)) == 10


def test_amount_medium_exact_points():
    assert score_transaction(_base_tx(amount_usd=500)) == 10


def test_amount_just_below_medium_threshold_no_points():
    assert score_transaction(_base_tx(amount_usd=499)) == 0


def test_amount_small_no_points():
    assert score_transaction(_base_tx(amount_usd=50)) == 0


# ---------------------------------------------------------------------------
# velocity_24h — exact points, thresholds, below-threshold
# ---------------------------------------------------------------------------

def test_velocity_high_exact_points():
    assert score_transaction(_base_tx(velocity_24h=6)) == 20


def test_velocity_high_above_threshold():
    assert score_transaction(_base_tx(velocity_24h=10)) == 20


def test_velocity_just_below_high_threshold_uses_medium():
    assert score_transaction(_base_tx(velocity_24h=5)) == 5


def test_velocity_medium_exact_points():
    assert score_transaction(_base_tx(velocity_24h=3)) == 5


def test_velocity_just_below_medium_threshold_no_points():
    assert score_transaction(_base_tx(velocity_24h=2)) == 0


def test_velocity_low_no_points():
    assert score_transaction(_base_tx(velocity_24h=1)) == 0


# ---------------------------------------------------------------------------
# failed_logins_24h — exact points, thresholds, below-threshold
# ---------------------------------------------------------------------------

def test_failed_logins_high_exact_points():
    assert score_transaction(_base_tx(failed_logins_24h=5)) == 20


def test_failed_logins_high_above_threshold():
    assert score_transaction(_base_tx(failed_logins_24h=9)) == 20


def test_failed_logins_just_below_high_threshold_uses_medium():
    assert score_transaction(_base_tx(failed_logins_24h=4)) == 10


def test_failed_logins_medium_exact_points():
    assert score_transaction(_base_tx(failed_logins_24h=2)) == 10


def test_failed_logins_just_below_medium_threshold_no_points():
    assert score_transaction(_base_tx(failed_logins_24h=1)) == 0


def test_failed_logins_zero_no_points():
    assert score_transaction(_base_tx(failed_logins_24h=0)) == 0


# ---------------------------------------------------------------------------
# prior_chargebacks — exact points, thresholds, below-threshold
# ---------------------------------------------------------------------------

def test_prior_chargebacks_two_exact_points():
    assert score_transaction(_base_tx(prior_chargebacks=2)) == 20


def test_prior_chargebacks_above_two_same_points():
    assert score_transaction(_base_tx(prior_chargebacks=5)) == 20


def test_prior_chargebacks_one_exact_points():
    assert score_transaction(_base_tx(prior_chargebacks=1)) == 5


def test_prior_chargebacks_zero_no_points():
    assert score_transaction(_base_tx(prior_chargebacks=0)) == 0


def test_prior_chargebacks_two_riskier_than_one():
    assert score_transaction(_base_tx(prior_chargebacks=2)) > score_transaction(_base_tx(prior_chargebacks=1))


# ---------------------------------------------------------------------------
# account_age_days — exact points, thresholds, below-threshold
# ---------------------------------------------------------------------------

def test_account_very_new_exact_points():
    assert score_transaction(_base_tx(account_age_days=29)) == 15


def test_account_very_new_lower_bound():
    assert score_transaction(_base_tx(account_age_days=1)) == 15


def test_account_age_at_30_uses_moderate_tier():
    assert score_transaction(_base_tx(account_age_days=30)) == 5


def test_account_moderately_new_exact_points():
    assert score_transaction(_base_tx(account_age_days=60)) == 5


def test_account_just_below_90_gets_points():
    assert score_transaction(_base_tx(account_age_days=89)) == 5


def test_account_age_at_90_no_points():
    assert score_transaction(_base_tx(account_age_days=90)) == 0


def test_account_old_no_points():
    assert score_transaction(_base_tx(account_age_days=500)) == 0


def test_very_new_account_riskier_than_moderately_new():
    assert score_transaction(_base_tx(account_age_days=15)) > score_transaction(_base_tx(account_age_days=60))


# ---------------------------------------------------------------------------
# merchant_category — exact points, safe categories
# ---------------------------------------------------------------------------

def test_gift_cards_exact_points():
    assert score_transaction(_base_tx(merchant_category="gift_cards")) == 15


def test_crypto_exact_points():
    assert score_transaction(_base_tx(merchant_category="crypto")) == 15


def test_grocery_no_points():
    assert score_transaction(_base_tx(merchant_category="grocery")) == 0


def test_electronics_no_points():
    assert score_transaction(_base_tx(merchant_category="electronics")) == 0


def test_travel_no_points():
    assert score_transaction(_base_tx(merchant_category="travel")) == 0


# ---------------------------------------------------------------------------
# Optional keys — missing account_age_days or merchant_category must not crash
# ---------------------------------------------------------------------------

def test_missing_account_age_does_not_crash_or_add_points():
    tx = {k: v for k, v in _base_tx().items() if k != "account_age_days"}
    assert score_transaction(tx) == 0


def test_missing_merchant_category_does_not_crash_or_add_points():
    tx = {k: v for k, v in _base_tx().items() if k != "merchant_category"}
    assert score_transaction(tx) == 0


def test_missing_both_optional_keys_does_not_crash():
    tx = {k: v for k, v in _base_tx().items() if k not in ("account_age_days", "merchant_category")}
    assert score_transaction(tx) == 0


# ---------------------------------------------------------------------------
# Multi-signal combination — verify contributions stack correctly
# ---------------------------------------------------------------------------

def test_two_signals_combine():
    # device_risk=70 (+25) + is_international=1 (+15) = 40
    assert score_transaction(_base_tx(device_risk_score=70, is_international=1)) == 40


def test_three_signals_combine():
    # device_risk=70 (+25) + is_international=1 (+15) + velocity_24h=6 (+20) = 60
    assert score_transaction(_base_tx(device_risk_score=70, is_international=1, velocity_24h=6)) == 60


def test_all_signals_at_max_tier_clamp_to_100():
    tx = _base_tx(
        device_risk_score=90,
        is_international=1,
        amount_usd=2000,
        velocity_24h=10,
        failed_logins_24h=8,
        prior_chargebacks=3,
        account_age_days=5,
        merchant_category="crypto",
    )
    assert score_transaction(tx) == 100


# ---------------------------------------------------------------------------
# Score bounds
# ---------------------------------------------------------------------------

def test_score_never_below_zero():
    assert score_transaction(_base_tx()) >= 0


def test_clean_transaction_scores_zero():
    assert score_transaction(_base_tx()) == 0
