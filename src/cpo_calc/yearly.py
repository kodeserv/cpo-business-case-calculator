"""Year-by-year operating model: energy sold, revenue, costs and EBITDA."""

from dataclasses import dataclass

from cpo_calc.models import SiteInputs

HOURS_PER_YEAR = 8760


@dataclass(frozen=True)
class YearRow:
    year: int
    utilisation_pct: float
    energy_kwh: float
    revenue: float
    payment_fees: float
    revenue_share: float
    energy_cost: float
    other_income: float
    fixed_costs: float
    ebitda: float


def utilisation_pct(site: SiteInputs, year: int) -> float:
    """Energy-based utilisation: kWh delivered / (rated kW x all hours), growing up to the ceiling."""
    ops = site.operations
    grown = ops.utilisation_pct_year1 + ops.utilisation_growth_pts_per_year * (year - 1)
    return min(grown, ops.utilisation_ceiling_pct)


@dataclass(frozen=True)
class _PerKwh:
    """Money per kWh delivered to the vehicle, in a given year."""

    revenue: float
    payment_fees: float
    revenue_share: float
    energy_cost: float

    @property
    def margin(self) -> float:
        return self.revenue - self.payment_fees - self.revenue_share - self.energy_cost


def _per_kwh(site: SiteInputs, year: int) -> _PerKwh:
    e, r, o = site.energy, site.revenue, site.operations
    tariff_factor = (1 + site.finance.tariff_escalation_pct / 100) ** (year - 1)
    price_factor = (1 + site.finance.price_escalation_pct / 100) ** (year - 1)

    price_incl_gst = r.price_per_kwh_incl_gst * price_factor
    revenue = price_incl_gst / (1 + r.gst_pct / 100)
    return _PerKwh(
        revenue=revenue,
        payment_fees=price_incl_gst * r.payment_fees_pct / 100,
        revenue_share=revenue * o.rent_share_pct / 100,
        energy_cost=e.effective_energy_charge_per_kwh * tariff_factor / (1 - e.losses_pct / 100),
    )


def _fixed_costs(site: SiteInputs, year: int) -> float:
    e, o = site.energy, site.operations
    tariff_factor = (1 + site.finance.tariff_escalation_pct / 100) ** (year - 1)
    return (
        e.demand_charge_per_kva_month * e.contracted_load_kva * 12 * tariff_factor
        + o.om_per_charger_year * site.charger_count
        + o.csms_per_charger_month * site.charger_count * 12
        + o.rent_per_month * 12
        + o.staff_and_other_per_month * 12
    )


def _rated_kwh(site: SiteInputs) -> float:
    """Energy the site would deliver running at rated power every hour of the year."""
    return site.total_power_kw * HOURS_PER_YEAR


def year_row(site: SiteInputs, year: int) -> YearRow:
    util = utilisation_pct(site, year)
    energy_kwh = _rated_kwh(site) * util / 100
    unit = _per_kwh(site, year)
    fixed_costs = _fixed_costs(site, year)
    other_income = site.revenue.other_income_per_month * 12
    return YearRow(
        year=year,
        utilisation_pct=util,
        energy_kwh=energy_kwh,
        revenue=energy_kwh * unit.revenue,
        payment_fees=energy_kwh * unit.payment_fees,
        revenue_share=energy_kwh * unit.revenue_share,
        energy_cost=energy_kwh * unit.energy_cost,
        other_income=other_income,
        fixed_costs=fixed_costs,
        ebitda=energy_kwh * unit.margin + other_income - fixed_costs,
    )


def breakeven_utilisation_pct(site: SiteInputs, year: int = 1) -> float | None:
    """Utilisation at which EBITDA is zero in `year`; None if it is above the utilisation ceiling."""
    gap = _fixed_costs(site, year) - site.revenue.other_income_per_month * 12
    if gap <= 0:
        return 0.0
    margin = _per_kwh(site, year).margin
    if margin <= 0:
        return None
    pct = gap / (_rated_kwh(site) * margin) * 100
    return pct if pct <= site.operations.utilisation_ceiling_pct else None


def yearly_model(site: SiteInputs) -> list[YearRow]:
    return [year_row(site, t) for t in range(1, site.finance.project_life_years + 1)]


def ebitda_at_utilisation(site: SiteInputs, utilisation_pct: float, year: int = 1) -> float:
    """EBITDA in `year` if the site ran at `utilisation_pct`, all else unchanged."""
    energy_kwh = _rated_kwh(site) * utilisation_pct / 100
    other_income = site.revenue.other_income_per_month * 12
    return energy_kwh * _per_kwh(site, year).margin + other_income - _fixed_costs(site, year)


def price_breakdown(site: SiteInputs, year: int = 1) -> list[tuple[str, float]] | None:
    """Where each rupee of the selling price goes in `year`, per kWh sold.

    Fixed costs and other income are spread over the kWh sold that year, so the last item,
    profit per kWh, equals EBITDA / kWh. None when nothing is sold.
    """
    row = year_row(site, year)
    if row.energy_kwh == 0:
        return None
    unit = _per_kwh(site, year)
    price = site.revenue.price_per_kwh_incl_gst * (1 + site.finance.price_escalation_pct / 100) ** (year - 1)
    return [
        ("Price paid by driver", price),
        ("GST", -(price - unit.revenue)),
        ("Payment and platform fees", -unit.payment_fees),
        ("Landowner's revenue share", -unit.revenue_share),
        ("Electricity, incl. losses", -unit.energy_cost),
        ("Fixed costs", -row.fixed_costs / row.energy_kwh),
        ("Other income", row.other_income / row.energy_kwh),
        ("Profit (EBITDA)", row.ebitda / row.energy_kwh),
    ]
