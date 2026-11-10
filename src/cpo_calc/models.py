"""Input models for one charging site. All money is in rupees, all rates in percent."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

Rupees = Annotated[float, Field(ge=0)]
Percent = Annotated[float, Field(ge=0, le=100)]


class _Input(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ChargerGroup(_Input):
    """Identical chargers, e.g. 2 x DC 60 kW."""

    power_kw: Annotated[float, Field(gt=0)]
    count: Annotated[int, Field(ge=1)]
    hardware_cost_each: Rupees


class Capex(_Input):
    electrical: Rupees = 0
    civil: Rupees = 0
    software_and_commissioning: Rupees = 0
    subsidy: Rupees = 0


class Energy(_Input):
    energy_charge_per_kwh: Rupees
    demand_charge_per_kva_month: Rupees = 0
    contracted_load_kva: Annotated[float, Field(ge=0)] = 0
    losses_pct: Annotated[float, Field(ge=0, lt=100)] = 7


class Revenue(_Input):
    price_per_kwh_incl_gst: Rupees
    gst_pct: Percent = 18
    payment_fees_pct: Percent = 0
    other_income_per_month: Rupees = 0


class Operations(_Input):
    utilisation_pct_year1: Percent
    utilisation_growth_pts_per_year: Annotated[float, Field(ge=0)] = 0
    uptime_pct: Percent = 95
    om_per_charger_year: Rupees = 0
    csms_per_charger_month: Rupees = 0
    rent_per_month: Rupees = 0
    rent_share_pct: Percent = 0
    staff_and_other_per_month: Rupees = 0

    @model_validator(mode="after")
    def _one_rent_model(self) -> "Operations":
        if self.rent_per_month > 0 and self.rent_share_pct > 0:
            raise ValueError("use either fixed rent or revenue share, not both")
        return self


class Finance(_Input):
    project_life_years: Annotated[int, Field(ge=1, le=25)] = 10
    discount_rate_pct: Percent = 12
    tariff_escalation_pct: Percent = 0
    price_escalation_pct: Percent = 0


class SiteInputs(_Input):
    chargers: Annotated[list[ChargerGroup], Field(min_length=1)]
    capex: Capex
    energy: Energy
    revenue: Revenue
    operations: Operations
    finance: Finance = Finance()

    @property
    def total_power_kw(self) -> float:
        return sum(g.power_kw * g.count for g in self.chargers)

    @property
    def charger_count(self) -> int:
        return sum(g.count for g in self.chargers)

    @property
    def gross_capex(self) -> float:
        c = self.capex
        hardware = sum(g.hardware_cost_each * g.count for g in self.chargers)
        return hardware + c.electrical + c.civil + c.software_and_commissioning

    @model_validator(mode="after")
    def _subsidy_within_capex(self) -> "SiteInputs":
        if self.capex.subsidy > self.gross_capex:
            raise ValueError("subsidy cannot exceed total capex")
        return self
