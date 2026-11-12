"""Formatting and table shaping for the results. Free of Streamlit so it can be unit tested."""

import pandas as pd

from cpo_calc.finance import SiteResult

LAKH = 100_000


def rupees_lakh(amount: float) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}₹{abs(amount) / LAKH:,.1f} L"


def years(value: float | None, project_life: int) -> str:
    return f"{value:.1f} years" if value is not None else f"Over {project_life} years"


def pct(value: float | None, missing: str = "n/a") -> str:
    return f"{value:.1f}%" if value is not None else missing


def verdict(result: SiteResult, discount_rate_pct: float, project_life: int) -> tuple[str, str]:
    """A plain-language summary and its level: 'good', 'warn' or 'bad'."""
    target = f"{discount_rate_pct:g}%"
    if result.payback_years is None:
        return "bad", (
            f"This site does not earn back its cost within {project_life} years. "
            "Try more usage, a higher price, lower rent or a subsidy."
        )
    returns = pct(result.irr_pct)
    if result.npv < 0:
        return "warn", (
            f"It pays back in {result.payback_years:.1f} years, but earns {returns} a year, "
            f"below the {target} you could expect elsewhere."
        )
    return "good", (
        f"It pays back in {result.payback_years:.1f} years and earns {returns} a year, "
        f"above the {target} you could expect elsewhere."
    )


def yearly_table(result: SiteResult) -> pd.DataFrame:
    """One row per year, rounded to the rupee; the table view and the CSV export."""
    rows = [
        {
            "Year": r.year,
            "Utilisation %": round(r.utilisation_pct, 2),
            "Energy sold kWh": round(r.energy_kwh),
            "Revenue excl. GST": round(r.revenue),
            "Payment fees": round(r.payment_fees),
            "Revenue share": round(r.revenue_share),
            "Energy cost": round(r.energy_cost),
            "Other income": round(r.other_income),
            "Fixed costs": round(r.fixed_costs),
            "EBITDA": round(r.ebitda),
            "Cumulative cash": round(cum),
        }
        for r, cum in zip(result.rows, result.cumulative_cash[1:], strict=True)
    ]
    return pd.DataFrame(rows)


def scenario_table(results: dict[str, SiteResult], project_life: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            name.capitalize(): {
                "Payback": years(r.payback_years, project_life),
                "NPV": rupees_lakh(r.npv),
                "IRR": pct(r.irr_pct),
                "Year-3 EBITDA": rupees_lakh(r.ebitda_year3) if r.ebitda_year3 is not None else "n/a",
                "Breakeven utilisation": pct(r.breakeven_utilisation_pct, "Not reachable"),
            }
            for name, r in results.items()
        }
    )
