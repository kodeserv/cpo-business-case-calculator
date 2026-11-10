import pytest

from cpo_calc.models import Energy, Revenue
from cpo_calc.yearly import breakeven_utilisation_pct, year_row, yearly_model
from tests.factories import simple_site


def test_hand_checked_year_one():
    row = year_row(simple_site(), 1)
    assert row.energy_kwh == pytest.approx(8_760)  # 10 kW x 8760 h x 10%
    assert row.revenue == pytest.approx(87_600)  # 8760 kWh x Rs 10
    assert row.energy_cost == pytest.approx(43_800)  # 8760 kWh x Rs 5
    assert row.fixed_costs == pytest.approx(10_000)
    assert row.ebitda == pytest.approx(33_800)


def test_payment_fees_are_on_the_amount_the_driver_pays():
    site = simple_site().model_copy(
        update={"revenue": Revenue(price_per_kwh_incl_gst=11.8, payment_fees_pct=2)}
    )
    assert year_row(site, 1).payment_fees == pytest.approx(8_760 * 11.8 * 0.02)


def test_losses_increase_energy_bought_not_energy_sold():
    site = simple_site().model_copy(update={"energy": Energy(energy_charge_per_kwh=5, losses_pct=20)})
    row = year_row(site, 1)
    assert row.energy_kwh == pytest.approx(8_760)
    assert row.energy_cost == pytest.approx(8_760 / 0.8 * 5)


def test_utilisation_grows_by_points_and_caps_at_100():
    rows = yearly_model(simple_site(utilisation_growth_pts_per_year=50))
    assert [r.utilisation_pct for r in rows] == [10, 60, 100]


def test_revenue_share_comes_off_revenue_and_fixed_rent_goes_to_fixed_costs():
    share = year_row(simple_site(rent_share_pct=10), 1)
    fixed = year_row(simple_site(rent_per_month=1_000), 1)
    assert share.revenue_share == pytest.approx(8_760)
    assert fixed.fixed_costs == pytest.approx(10_000 + 12_000)


def test_one_row_per_year_of_project_life():
    assert [r.year for r in yearly_model(simple_site())] == [1, 2, 3]


def test_breakeven_utilisation_hand_checked():
    # margin Rs 5/kWh, fixed Rs 10,000 -> 2,000 kWh a year out of 87,600 available = 2.283%
    assert breakeven_utilisation_pct(simple_site()) == pytest.approx(2_000 / 87_600 * 100)


def test_ebitda_is_zero_at_breakeven_utilisation():
    site = simple_site()
    at_breakeven = site.model_copy(
        update={"operations": site.operations.model_copy(
            update={"utilisation_pct_year1": breakeven_utilisation_pct(site)})}
    )
    assert year_row(at_breakeven, 1).ebitda == pytest.approx(0, abs=1e-6)


def test_no_breakeven_when_energy_costs_more_than_the_selling_price():
    site = simple_site().model_copy(update={"energy": Energy(energy_charge_per_kwh=12, losses_pct=0)})
    assert breakeven_utilisation_pct(site) is None


def test_breakeven_is_zero_when_other_income_covers_fixed_costs():
    site = simple_site().model_copy(
        update={"revenue": Revenue(price_per_kwh_incl_gst=11.8, other_income_per_month=1_000)}
    )
    assert breakeven_utilisation_pct(site) == 0
