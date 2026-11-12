"""Input form layout and the mapping between form state and SiteInputs.

Kept free of Streamlit imports so it can be unit tested.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from cpo_calc.models import SiteInputs

Kind = Literal["count", "kw", "rupees", "rate", "pct", "toggle"]


@dataclass(frozen=True)
class FormField:
    path: str  # "<group>.<field>"; "charger" is the single charger group
    label: str
    hint: str
    kind: Kind


GROUPS: list[tuple[str, list[FormField]]] = [
    ("Site", [
        FormField("charger.power_kw", "Charger power (kW)", "Rated output of one charger, from the datasheet.", "kw"),
        FormField("charger.count", "Number of chargers", "Identical chargers at this site.", "count"),
        FormField("charger.hardware_cost_each", "Hardware cost per charger (₹)", "Vendor quote per charger, including installation.", "rupees"),
    ]),
    ("Capex and subsidy", [
        FormField("capex.electrical", "Electrical upstream (₹)", "Transformer, cabling, metering and DISCOM connection charges. Often the largest item for DC sites.", "rupees"),
        FormField("capex.civil", "Civil works (₹)", "Foundation, canopy, signage, parking marking.", "rupees"),
        FormField("capex.software_and_commissioning", "Software and commissioning (₹)", "CSMS onboarding, SIMs, testing.", "rupees"),
        FormField("capex.subsidy", "Subsidy (₹)", "Amount sanctioned under PM E-DRIVE or a state scheme. Keep 0 until it is sanctioned.", "rupees"),
    ]),
    ("Electricity", [
        FormField("energy.energy_charge_per_kwh", "Energy charge (₹/kWh)", "EV charging category in your DISCOM's current tariff order. With time-of-day pricing on, enter the normal rate.", "rate"),
        FormField("energy.time_of_day", "Time-of-day pricing", "Public stations under the 2024 MoP guidelines pay 0.7x the energy charge from 9 am to 4 pm and 1.3x at other times. Captive connections follow their state's own time-of-day tariff: leave this off and enter a blended rate.", "toggle"),
        FormField("energy.solar_hours_share_pct", "Charging in solar hours (%)", "Share of energy sold between 9 am and 4 pm. Highway and office sites charge more by day; depots and homes mostly at night.", "pct"),
        FormField("energy.demand_charge_per_kva_month", "Demand charge (₹/kVA/month)", "Public stations: usually 0, as the 2024 MoP guidelines ask for an energy-only tariff until March 2028. Captive or depot connections often pay it. Check your state's tariff order.", "rate"),
        FormField("energy.contracted_load_kva", "Contracted load (kVA)", "Sanctioned load on the connection.", "kw"),
        FormField("energy.losses_pct", "Losses (%)", "Charger and cable losses; 5-8% is typical.", "pct"),
    ]),
    ("Revenue", [
        FormField("revenue.price_per_kwh_incl_gst", "Selling price (₹/kWh incl. GST)", "What a driver pays per kWh, as shown in the app.", "rate"),
        FormField("revenue.gst_pct", "GST (%)", "Usually 18% for charging as a service; confirm with your CA.", "pct"),
        FormField("revenue.payment_fees_pct", "Payment and platform fees (%)", "UPI or card gateway fees plus any eMSP or aggregator commission.", "pct"),
        FormField("revenue.other_income_per_month", "Other income (₹/month)", "Ads, parking, retail tie-ups.", "rupees"),
    ]),
    ("Operations", [
        FormField("operations.utilisation_pct_year1", "Utilisation in year 1 (%)", "Energy delivered / (rated power x 24 h x 365), the usual energy-based measure. Indian public chargers often run at 1-10%.", "pct"),
        FormField("operations.utilisation_growth_pts_per_year", "Utilisation growth (points/year)", "Added each year: 2 means 8% -> 10% -> 12%.", "pct"),
        FormField("operations.max_utilisation_pct", "Maximum utilisation (%)", "Growth stops here. Busy public DC sites rarely pass 15-20%; an overnight depot is limited by its charging window (8 h a day is about 33%).", "pct"),
        FormField("operations.uptime_pct", "Uptime (%)", "Share of time the chargers are working. Utilisation cannot exceed it.", "pct"),
        FormField("operations.om_per_charger_year", "O&M and AMC (₹/charger/year)", "AMC quote from the charger vendor.", "rupees"),
        FormField("operations.csms_per_charger_month", "CSMS (₹/charger/month)", "From your CSMS contract.", "rupees"),
        FormField("operations.rent_per_month", "Fixed rent (₹/month)", "Use this or revenue share, not both.", "rupees"),
        FormField("operations.rent_share_pct", "Revenue share to landowner (%)", "Share of revenue excluding GST. Use this or fixed rent, not both.", "pct"),
        FormField("operations.staff_and_other_per_month", "Staff and other (₹/month)", "Attendant, security, insurance, internet.", "rupees"),
    ]),
    ("Finance", [
        FormField("finance.project_life_years", "Project life (years)", "Years over which payback, NPV and IRR are measured.", "count"),
        FormField("finance.discount_rate_pct", "Discount rate (%)", "Return you expect from money at this risk, e.g. 12%.", "pct"),
        FormField("finance.tariff_escalation_pct", "Electricity tariff rise (%/year)", "Expected yearly rise in energy and demand charges.", "pct"),
        FormField("finance.price_escalation_pct", "Selling price rise (%/year)", "Expected yearly rise in your selling price.", "pct"),
    ]),
]

ALL_FIELDS = [f for _, fields in GROUPS for f in fields]

# The three inputs that move the result most; shown as large sliders in the main area.
KEY_FIELDS = ("operations.utilisation_pct_year1", "revenue.price_per_kwh_incl_gst", "energy.energy_charge_per_kwh")

POWER_OPTIONS_KW = (3.3, 7.4, 11.0, 22.0, 30.0, 50.0, 60.0, 120.0, 150.0, 180.0, 240.0, 360.0)


@dataclass(frozen=True)
class SliderRange:
    low: float
    high: float
    step: float


# Rupee amounts are left as typed inputs, since they come from quotes and contracts.
SLIDERS: dict[str, SliderRange] = {
    "charger.count": SliderRange(1, 20, 1),
    "energy.energy_charge_per_kwh": SliderRange(0, 20, 0.25),
    "energy.demand_charge_per_kva_month": SliderRange(0, 500, 10),
    "energy.contracted_load_kva": SliderRange(0, 1000, 10),
    "energy.losses_pct": SliderRange(0, 20, 0.5),
    "energy.solar_hours_share_pct": SliderRange(0, 100, 5),
    "revenue.price_per_kwh_incl_gst": SliderRange(0, 40, 0.5),
    "revenue.gst_pct": SliderRange(0, 28, 1),
    "revenue.payment_fees_pct": SliderRange(0, 10, 0.25),
    "operations.utilisation_pct_year1": SliderRange(0, 50, 0.5),
    "operations.utilisation_growth_pts_per_year": SliderRange(0, 5, 0.25),
    "operations.max_utilisation_pct": SliderRange(0, 60, 1),
    "operations.uptime_pct": SliderRange(50, 100, 0.5),
    "operations.rent_share_pct": SliderRange(0, 30, 0.5),
    "finance.project_life_years": SliderRange(1, 25, 1),
    "finance.discount_rate_pct": SliderRange(0, 25, 0.5),
    "finance.tariff_escalation_pct": SliderRange(0, 10, 0.25),
    "finance.price_escalation_pct": SliderRange(0, 10, 0.25),
}
_LABELS = {f.path: f.label for f in ALL_FIELDS}


def error_message(loc: tuple, msg: str) -> str:
    """Prefix a pydantic error with the form label it belongs to, when there is one."""
    msg = msg.removeprefix("Value error, ")
    if loc and loc[0] == "chargers":
        loc = ("charger", *loc[2:])
    label = _LABELS.get(".".join(str(part) for part in loc[:2]))
    return f"{label}: {msg}" if label else msg


def to_state(site: SiteInputs) -> dict[str, float | int | bool]:
    """Flatten a SiteInputs (single charger group) into form values keyed by path."""
    data = site.model_dump()
    data["charger"] = data.pop("chargers")[0]
    state = {}
    for f in ALL_FIELDS:
        group, name = f.path.split(".")
        value = data[group][name]
        cast = {"count": int, "toggle": bool}.get(f.kind, float)
        state[f.path] = cast(value)
    return state


def from_state(state: Mapping[str, float | int | bool]) -> SiteInputs:
    """Build validated SiteInputs from form values; raises pydantic.ValidationError."""
    data: dict[str, dict] = {}
    for f in ALL_FIELDS:
        group, name = f.path.split(".")
        data.setdefault(group, {})[name] = state[f.path]
    data["chargers"] = [data.pop("charger")]
    return SiteInputs.model_validate(data)
