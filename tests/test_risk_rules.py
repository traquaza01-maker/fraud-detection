from risk_rules import label_risk, score_transaction


def _base_tx(**overrides):
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


def test_label_risk_thresholds():
    assert label_risk(10) == "low"
    assert label_risk(35) == "medium"
    assert label_risk(75) == "high"


def test_large_amount_adds_risk():
    assert score_transaction(_base_tx(amount_usd=1200)) >= 25


# --- Bug fixes: all four signals must now increase score ---

def test_high_device_risk_adds_risk():
    high = score_transaction(_base_tx(device_risk_score=80))
    low = score_transaction(_base_tx(device_risk_score=10))
    assert high > low


def test_medium_device_risk_adds_risk():
    mid = score_transaction(_base_tx(device_risk_score=50))
    low = score_transaction(_base_tx(device_risk_score=10))
    assert mid > low


def test_international_adds_risk():
    intl = score_transaction(_base_tx(is_international=1))
    dom = score_transaction(_base_tx(is_international=0))
    assert intl > dom


def test_high_velocity_adds_risk():
    high = score_transaction(_base_tx(velocity_24h=7))
    low = score_transaction(_base_tx(velocity_24h=1))
    assert high > low


def test_medium_velocity_adds_risk():
    mid = score_transaction(_base_tx(velocity_24h=4))
    low = score_transaction(_base_tx(velocity_24h=1))
    assert mid > low


def test_prior_chargebacks_two_adds_risk():
    cb2 = score_transaction(_base_tx(prior_chargebacks=2))
    cb0 = score_transaction(_base_tx(prior_chargebacks=0))
    assert cb2 > cb0


def test_prior_chargebacks_one_adds_risk():
    cb1 = score_transaction(_base_tx(prior_chargebacks=1))
    cb0 = score_transaction(_base_tx(prior_chargebacks=0))
    assert cb1 > cb0


# --- New signals ---

def test_very_new_account_adds_risk():
    new = score_transaction(_base_tx(account_age_days=15))
    old = score_transaction(_base_tx(account_age_days=500))
    assert new > old


def test_moderately_new_account_adds_risk():
    mid = score_transaction(_base_tx(account_age_days=60))
    old = score_transaction(_base_tx(account_age_days=500))
    assert mid > old


def test_very_new_account_riskier_than_moderately_new():
    very_new = score_transaction(_base_tx(account_age_days=15))
    mid_new = score_transaction(_base_tx(account_age_days=60))
    assert very_new > mid_new


def test_gift_cards_adds_risk():
    gc = score_transaction(_base_tx(merchant_category="gift_cards"))
    gr = score_transaction(_base_tx(merchant_category="grocery"))
    assert gc > gr


def test_crypto_adds_risk():
    crypto = score_transaction(_base_tx(merchant_category="crypto"))
    gr = score_transaction(_base_tx(merchant_category="grocery"))
    assert crypto > gr


def test_score_clamped_at_100():
    # Maximally suspicious transaction should not exceed 100.
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


def test_score_clamped_at_0():
    # Cleanest possible transaction should not go below 0.
    assert score_transaction(_base_tx()) >= 0
