"""Project returns: net capex, payback, NPV and IRR over the project life.

Cash flow is EBITDA only: no debt, tax, depreciation or charger replacement (v0.2).
"""

from dataclasses import dataclass

from cpo_calc.models import SiteInputs
from cpo_calc.yearly import YearRow, breakeven_utilisation_pct, yearly_model


@dataclass(frozen=True)
class SiteResult:
    rows: list[YearRow]
    net_capex: float
    cumulative_cash: list[float]  # index 0 is the investment, index t is end of year t
    payback_years: float | None
    npv: float
    irr_pct: float | None
    breakeven_utilisation_pct: float | None
    ebitda_year3: float | None


def npv(rate_pct: float, cash_flows: list[float]) -> float:
    rate = rate_pct / 100
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))


def irr_pct(cash_flows: list[float]) -> float | None:
    """Rate where NPV is zero, by bisection; None if NPV never changes sign."""
    lo, hi = -99.0, 1_000.0
    if npv(lo, cash_flows) * npv(hi, cash_flows) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(lo, cash_flows) * npv(mid, cash_flows) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def payback_years(cumulative_cash: list[float]) -> float | None:
    """Years until cumulative cash turns non-negative, interpolated within the year."""
    for t in range(1, len(cumulative_cash)):
        before, after = cumulative_cash[t - 1], cumulative_cash[t]
        if after >= 0:
            return t - 1 + (-before / (after - before) if before < 0 else 0)
    return None


def evaluate(site: SiteInputs) -> SiteResult:
    rows = yearly_model(site)
    net_capex = site.gross_capex - site.capex.subsidy
    cash_flows = [-net_capex] + [r.ebitda for r in rows]

    cumulative, running = [], 0.0
    for cf in cash_flows:
        running += cf
        cumulative.append(running)

    return SiteResult(
        rows=rows,
        net_capex=net_capex,
        cumulative_cash=cumulative,
        payback_years=payback_years(cumulative),
        npv=npv(site.finance.discount_rate_pct, cash_flows),
        irr_pct=irr_pct(cash_flows),
        breakeven_utilisation_pct=breakeven_utilisation_pct(site),
        ebitda_year3=rows[2].ebitda if len(rows) >= 3 else None,
    )
