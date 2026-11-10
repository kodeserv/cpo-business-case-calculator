"""Pessimistic, base and optimistic cases built from the user's own inputs."""

from cpo_calc.finance import SiteResult, evaluate
from cpo_calc.models import SiteInputs

# (utilisation factor, price factor) applied to the user's inputs
SCENARIO_FACTORS: dict[str, tuple[float, float]] = {
    "pessimistic": (0.7, 0.9),
    "base": (1.0, 1.0),
    "optimistic": (1.3, 1.1),
}


def scenario_inputs(site: SiteInputs, name: str) -> SiteInputs:
    util_factor, price_factor = SCENARIO_FACTORS[name]
    data = site.model_dump()
    ops, rev = data["operations"], data["revenue"]
    ops["utilisation_pct_year1"] = min(ops["utilisation_pct_year1"] * util_factor, 100)
    ops["utilisation_growth_pts_per_year"] *= util_factor
    rev["price_per_kwh_incl_gst"] *= price_factor
    return SiteInputs.model_validate(data)


def evaluate_scenarios(site: SiteInputs) -> dict[str, SiteResult]:
    return {name: evaluate(scenario_inputs(site, name)) for name in SCENARIO_FACTORS}
