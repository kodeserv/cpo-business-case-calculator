import pytest

from cpo_calc.finance import evaluate, irr_pct, npv, payback_years
from tests.factories import simple_site


def test_npv_hand_checked():
    # -100 now, +110 in a year, at 10% -> exactly zero
    assert npv(10, [-100, 110]) == pytest.approx(0)
    assert npv(0, [-100, 30, 30, 30]) == pytest.approx(-10)


def test_irr_finds_the_rate_where_npv_is_zero():
    assert irr_pct([-100, 110]) == pytest.approx(10, abs=1e-6)
    assert irr_pct([-1_000, 300, 400, 500]) == pytest.approx(8.896, abs=1e-3)


def test_irr_is_none_when_project_never_recovers_its_cost():
    assert irr_pct([-1_000, -50, -50]) is None


def test_payback_is_interpolated_within_the_year():
    # -100, then +40 a year: cumulative -60, -20, +20 -> 2.5 years
    assert payback_years([-100, -60, -20, 20]) == pytest.approx(2.5)


def test_payback_is_none_when_cash_never_turns_positive():
    assert payback_years([-100, -90, -80]) is None


def test_evaluate_ties_capex_ebitda_and_cumulative_cash_together():
    # 1 x 10 kW, hardware Rs 1 lakh, EBITDA Rs 33,800 a year
    result = evaluate(simple_site())
    assert result.net_capex == 100_000
    assert result.cumulative_cash == pytest.approx([-100_000, -66_200, -32_400, 1_400])
    assert result.payback_years == pytest.approx(2 + 32_400 / 33_800)
    assert result.ebitda_year3 == pytest.approx(33_800)
