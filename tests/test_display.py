from cpo_calc.finance import evaluate
from cpo_calc.presets import PRESETS
from cpo_calc.scenarios import evaluate_scenarios
from display import pct, rupees_lakh, scenario_table, yearly_table, years


def test_formats_for_missing_values():
    assert rupees_lakh(4_300_000) == "₹43.0 L"
    assert rupees_lakh(-1_744_355) == "-₹17.4 L"
    assert years(None, 10) == "Not within 10 years"
    assert pct(None, "Not reachable") == "Not reachable"


def test_yearly_table_has_a_row_per_year_ending_in_cumulative_cash():
    result = evaluate(PRESETS["apartment_ac"].inputs)
    table = yearly_table(result)
    assert len(table) == 10
    assert table["Cumulative cash"].iloc[-1] == round(result.cumulative_cash[-1])


def test_scenario_table_has_three_columns():
    site = PRESETS["fleet_depot_dc"].inputs
    table = scenario_table(evaluate_scenarios(site), 10)
    assert list(table.columns) == ["Pessimistic", "Base", "Optimistic"]
