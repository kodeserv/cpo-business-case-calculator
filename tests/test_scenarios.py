import pytest

from cpo_calc.finance import evaluate
from cpo_calc.presets import PRESETS
from cpo_calc.scenarios import evaluate_scenarios, scenario_inputs
from tests.factories import simple_site


def test_base_scenario_is_the_users_own_case():
    site = simple_site()
    assert evaluate_scenarios(site)["base"] == evaluate(site)


def test_pessimistic_cuts_utilisation_and_price():
    s = scenario_inputs(simple_site(utilisation_growth_pts_per_year=2), "pessimistic")
    assert s.operations.utilisation_pct_year1 == pytest.approx(7)
    assert s.operations.utilisation_growth_pts_per_year == pytest.approx(1.4)
    assert s.revenue.price_per_kwh_incl_gst == pytest.approx(11.8 * 0.9)


def test_optimistic_utilisation_never_exceeds_uptime():
    site = simple_site()
    high = site.model_copy(
        update={"operations": site.operations.model_copy(update={"utilisation_pct_year1": 80, "uptime_pct": 90})}
    )
    assert scenario_inputs(high, "optimistic").operations.utilisation_pct_year1 == 90


@pytest.mark.parametrize("key", list(PRESETS))
def test_npv_rises_from_pessimistic_to_optimistic(key):
    results = evaluate_scenarios(PRESETS[key].inputs)
    assert results["pessimistic"].npv < results["base"].npv < results["optimistic"].npv
