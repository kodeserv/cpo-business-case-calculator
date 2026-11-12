"""Plotly figures for the results page."""

import plotly.graph_objects as go

from cpo_calc.finance import SiteResult
from cpo_calc.models import SiteInputs
from cpo_calc.yearly import ebitda_at_utilisation
from display import LAKH

SERIES = "#2a78d6"
REFERENCE = "#8a8984"


def _layout(fig: go.Figure, x_title: str) -> go.Figure:
    fig.update_layout(
        margin=dict(l=8, r=8, t=8, b=8),
        height=320,
        showlegend=False,
        hovermode="x unified",
        xaxis=dict(title=x_title, showgrid=False),
        yaxis=dict(title="₹ lakh", zeroline=True, zerolinewidth=1, zerolinecolor=REFERENCE),
    )
    return fig


def cumulative_cash(result: SiteResult) -> go.Figure:
    years = list(range(len(result.cumulative_cash)))
    fig = go.Figure(
        go.Scatter(
            x=years,
            y=[c / LAKH for c in result.cumulative_cash],
            mode="lines+markers",
            line=dict(color=SERIES, width=2),
            marker=dict(size=8),
            hovertemplate="₹%{y:,.1f} L<extra></extra>",
            name="Cumulative cash",
        )
    )
    if result.payback_years is not None:
        fig.add_vline(
            x=result.payback_years, line=dict(color=REFERENCE, width=1, dash="dot"),
            annotation_text=f"Payback {result.payback_years:.1f} yrs", annotation_position="top left",
        )
    return _layout(fig, "Year (0 = investment)")


def ebitda_vs_utilisation(site: SiteInputs, result: SiteResult) -> go.Figure:
    utils = [u / 2 for u in range(4, 51)]  # 2% to 25% in half-point steps
    ebitda = [ebitda_at_utilisation(site, u) / LAKH for u in utils]
    fig = go.Figure(
        go.Scatter(
            x=utils,
            y=ebitda,
            mode="lines",
            line=dict(color=SERIES, width=2),
            hovertemplate="₹%{y:,.1f} L<extra></extra>",
            name="Year-1 EBITDA",
        )
    )
    # Both reference marks are explained in the caption under the chart, so no labels can collide.
    fig.add_vline(x=site.operations.utilisation_pct_year1, line=dict(color=REFERENCE, width=1, dash="dash"))
    breakeven = result.breakeven_utilisation_pct
    if breakeven is not None and 2 <= breakeven <= 25:
        fig.add_trace(
            go.Scatter(
                x=[breakeven], y=[0], mode="markers",
                marker=dict(size=10, color=SERIES, line=dict(color="white", width=2)),
                hovertemplate=f"Breakeven {breakeven:.1f}%<extra></extra>",
            )
        )
    return _layout(fig, "Utilisation (%)")


DEDUCTION = "#eb6834"
ADDITION = "#1baf7a"


def price_breakdown(items: list[tuple[str, float]]) -> go.Figure:
    """Horizontal waterfall from the driver's price down to profit per kWh."""
    shown = [items[0]] + [(label, v) for label, v in items[1:-1] if abs(v) >= 0.005] + [items[-1]]
    # Values ride in the category labels, so no bar text can collide with an axis label on a phone.
    labels = [f"{label}  {'−' if v < 0 else ''}₹{abs(v):,.2f}" for label, v in shown]
    values = [v for _, v in shown]
    measures = ["absolute"] + ["relative"] * (len(shown) - 2) + ["total"]
    fig = go.Figure(
        go.Waterfall(
            orientation="h",
            y=labels,
            x=values,
            measure=measures,
            decreasing=dict(marker=dict(color=DEDUCTION)),
            increasing=dict(marker=dict(color=ADDITION)),
            totals=dict(marker=dict(color=SERIES)),
            connector=dict(line=dict(color=REFERENCE, width=1, dash="dot")),
            hovertemplate="%{y}: ₹%{x:,.2f} per kWh<extra></extra>",
        )
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=8, b=8),
        height=60 + 40 * len(shown),
        showlegend=False,
        xaxis=dict(title="₹ per kWh", zeroline=True, zerolinecolor=REFERENCE),
        yaxis=dict(autorange="reversed"),
    )
    return fig
