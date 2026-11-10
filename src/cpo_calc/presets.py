"""Starting points so a visitor sees a result before typing anything.

Every number here is illustrative (India, late 2026), not a quote or a tariff
order. Users are expected to replace them with their own.
"""

from dataclasses import dataclass

from cpo_calc.models import (
    Capex,
    ChargerGroup,
    Energy,
    Finance,
    Operations,
    Revenue,
    SiteInputs,
)

ILLUSTRATIVE_NOTE = (
    "Illustrative numbers only. Replace them with your vendor quotes, "
    "your DISCOM tariff and your scheme sanction."
)


@dataclass(frozen=True)
class Preset:
    key: str
    title: str
    summary: str
    inputs: SiteInputs


_FINANCE = Finance(
    project_life_years=10,
    discount_rate_pct=12,
    tariff_escalation_pct=3,
    price_escalation_pct=2,
)

HIGHWAY_DC = Preset(
    key="highway_dc",
    title="Highway DC",
    summary="2 x 60 kW DC at a fuel station or dhaba, land on revenue share.",
    inputs=SiteInputs(
        chargers=[ChargerGroup(power_kw=60, count=2, hardware_cost_each=1_100_000)],
        capex=Capex(electrical=1_500_000, civil=500_000, software_and_commissioning=100_000),
        # Public station: single-part tariff (energy only) under the 2024 MoP guidelines.
        energy=Energy(energy_charge_per_kwh=7.5, contracted_load_kva=140, losses_pct=7),
        revenue=Revenue(price_per_kwh_incl_gst=22, payment_fees_pct=2),
        operations=Operations(
            utilisation_pct_year1=8,
            utilisation_growth_pts_per_year=2,
            om_per_charger_year=50_000,
            csms_per_charger_month=1_000,
            rent_share_pct=10,
            staff_and_other_per_month=30_000,
        ),
        finance=_FINANCE,
    ),
)

APARTMENT_AC = Preset(
    key="apartment_ac",
    title="Apartment society AC",
    summary="4 x 7.4 kW AC in a residents' parking, society hosts for free.",
    inputs=SiteInputs(
        chargers=[ChargerGroup(power_kw=7.4, count=4, hardware_cost_each=60_000)],
        capex=Capex(electrical=150_000, civil=50_000, software_and_commissioning=20_000),
        energy=Energy(energy_charge_per_kwh=7, losses_pct=5),
        revenue=Revenue(price_per_kwh_incl_gst=14, payment_fees_pct=2),
        operations=Operations(
            utilisation_pct_year1=12,
            utilisation_growth_pts_per_year=2,
            om_per_charger_year=5_000,
            csms_per_charger_month=300,
        ),
        finance=_FINANCE,
    ),
)

FLEET_DEPOT_DC = Preset(
    key="fleet_depot_dc",
    title="Fleet depot DC",
    summary="4 x 30 kW DC charging a cab or delivery fleet overnight in a corner of its yard rented to the operator, billed by invoice.",
    inputs=SiteInputs(
        chargers=[ChargerGroup(power_kw=30, count=4, hardware_cost_each=600_000)],
        capex=Capex(electrical=1_000_000, civil=300_000, software_and_commissioning=80_000),
        # Captive connection, so a demand charge applies; charging is mostly overnight.
        energy=Energy(
            energy_charge_per_kwh=7,
            demand_charge_per_kva_month=150,
            contracted_load_kva=130,
            losses_pct=7,
        ),
        # Priced below public DC (Rs 18-24/kWh) so the fleet has a reason to sign.
        revenue=Revenue(price_per_kwh_incl_gst=17),
        operations=Operations(
            utilisation_pct_year1=20,
            utilisation_growth_pts_per_year=2,
            om_per_charger_year=30_000,
            csms_per_charger_month=800,
            rent_per_month=10_000,
            staff_and_other_per_month=20_000,
        ),
        finance=_FINANCE,
    ),
)

PRESETS: dict[str, Preset] = {p.key: p for p in (HIGHWAY_DC, APARTMENT_AC, FLEET_DEPOT_DC)}
