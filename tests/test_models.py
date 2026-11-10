import pytest
from pydantic import ValidationError

from cpo_calc.models import (
    Capex,
    ChargerGroup,
    Energy,
    Operations,
    Revenue,
    SiteInputs,
)


def make_site(**overrides) -> SiteInputs:
    fields = dict(
        chargers=[
            ChargerGroup(power_kw=60, count=2, hardware_cost_each=1_200_000),
            ChargerGroup(power_kw=7.4, count=2, hardware_cost_each=60_000),
        ],
        capex=Capex(electrical=1_500_000),
        energy=Energy(energy_charge_per_kwh=8),
        revenue=Revenue(price_per_kwh_incl_gst=22),
        operations=Operations(utilisation_pct_year1=10),
    )
    return SiteInputs(**(fields | overrides))


def test_totals_across_charger_groups():
    site = make_site()
    assert site.total_power_kw == pytest.approx(134.8)
    assert site.charger_count == 4


def test_negative_price_is_rejected():
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        Revenue(price_per_kwh_incl_gst=-5)


def test_fixed_rent_and_revenue_share_together_are_rejected():
    with pytest.raises(ValidationError, match="not both"):
        Operations(utilisation_pct_year1=10, rent_per_month=20_000, rent_share_pct=10)


def test_site_needs_at_least_one_charger():
    with pytest.raises(ValidationError):
        make_site(chargers=[])


def test_misspelt_field_is_rejected():
    with pytest.raises(ValidationError, match="Extra inputs"):
        Energy(energy_charge_per_kwh=8, loses_pct=7)


def test_inputs_are_immutable():
    site = make_site()
    with pytest.raises(ValidationError):
        site.capex.subsidy = 100


def test_gross_capex_adds_hardware_and_site_costs():
    # 2 x 12 lakh + 2 x 60k hardware + 15 lakh electrical
    assert make_site().gross_capex == 2_400_000 + 120_000 + 1_500_000


def test_subsidy_above_capex_is_rejected():
    with pytest.raises(ValidationError, match="cannot exceed"):
        make_site(capex=Capex(electrical=100_000, subsidy=10_000_000))


def test_utilisation_above_uptime_is_rejected():
    with pytest.raises(ValidationError, match="cannot exceed maximum utilisation or uptime"):
        Operations(utilisation_pct_year1=96, uptime_pct=95)


def test_utilisation_above_maximum_is_rejected():
    with pytest.raises(ValidationError, match="cannot exceed maximum utilisation"):
        Operations(utilisation_pct_year1=20, max_utilisation_pct=15)
