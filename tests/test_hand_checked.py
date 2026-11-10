"""Year-1 figures for each preset, worked by hand in examples/hand_checked.md."""

import pytest

from cpo_calc.finance import evaluate
from cpo_calc.presets import PRESETS

EXPECTED = {
    "highway_dc": dict(
        revenue=1_567_892, payment_fees=37_002, revenue_share=156_789,
        energy_cost=678_194, fixed_costs=484_000, ebitda=211_907, net_capex=4_300_000,
    ),
    "apartment_ac": dict(
        revenue=369_167, payment_fees=8_712, revenue_share=0,
        energy_cost=229_272, fixed_costs=34_400, ebitda=96_783, net_capex=460_000,
    ),
    "fleet_depot_dc": dict(
        revenue=3_028_881, payment_fees=0, revenue_share=0,
        energy_cost=1_582_452, fixed_costs=752_400, ebitda=694_030, net_capex=3_780_000,
    ),
}


@pytest.mark.parametrize("key", list(EXPECTED))
def test_year_one_matches_hand_calculation_to_the_rupee(key):
    result = evaluate(PRESETS[key].inputs)
    year1 = result.rows[0]
    actual = {name: round(getattr(year1, name)) for name in EXPECTED[key] if name != "net_capex"}
    actual["net_capex"] = round(result.net_capex)
    assert actual == EXPECTED[key]
