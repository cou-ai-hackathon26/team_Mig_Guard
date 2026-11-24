from app.utils.license import normalize_license
from app.utils.money import parse_money


def test_parse_bdt_grouped():
    parsed = parse_money("Fee Tk 1,50,000")
    assert parsed is not None
    assert parsed.amount == 150000
    assert parsed.currency == "BDT"


def test_parse_monthly_usd():
    parsed = parse_money("Salary USD 8000 per month")
    assert parsed is not None
    assert parsed.amount == 8000
    assert parsed.currency == "USD"
    assert parsed.period == "month"


def test_normalize_license_variants():
    assert normalize_license("rl-1857") == "RL1857"
    assert normalize_license("1857") == "RL1857"
    assert normalize_license("RL 0027") == "RL0027"
    assert normalize_license("not a licence") is None
