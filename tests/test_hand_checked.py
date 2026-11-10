"""Year-1 figures for each preset, worked by hand in examples/hand_checked.md."""

import pytest

from cpo_calc.finance import evaluate
from cpo_calc.presets import PRESETS

EXPECTED = {
    "highway_dc": dict(
        revenue=1_489_497, payment_fees=35_152, revenue_share=148_950,
        energy_cost=644_284, fixed_costs=820_000, ebitda=-158_889, net_capex=4_300_000,
    ),
    "apartment_ac": dict(
        revenue=350_709, payment_fees=8_277, revenue_share=0,
        energy_cost=217_809, fixed_costs=34_400, ebitda=90_223, net_capex=460_000,
    ),
    "fleet_depot_dc": dict(
        revenue=2_538_915, payment_fees=0, revenue_share=0,
        energy_cost=1_610_710, fixed_costs=1_010_400, ebitda=-82_194, net_capex=3_780_000,
    ),
}


@pytest.mark.parametrize("key", list(EXPECTED))
def test_year_one_matches_hand_calculation_to_the_rupee(key):
    result = evaluate(PRESETS[key].inputs)
    year1 = result.rows[0]
    actual = {name: round(getattr(year1, name)) for name in EXPECTED[key] if name != "net_capex"}
    actual["net_capex"] = round(result.net_capex)
    assert actual == EXPECTED[key]
