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
    # The marker for the user's utilisation runs from zero upwards, so the breakeven label
    # placed below zero never collides with it.
    yours = site.operations.utilisation_pct_year1
    top = max(ebitda)
    fig.add_shape(
        type="line", x0=yours, x1=yours, y0=0, y1=top,
        line=dict(color=REFERENCE, width=1, dash="dash"),
    )
    fig.add_annotation(
        x=yours, y=top, text=f"Your year 1: {yours:g}%", showarrow=False,
        xanchor="left" if yours <= 13.5 else "right", yanchor="bottom", font=dict(size=11),
    )
    breakeven = result.breakeven_utilisation_pct
    if breakeven is not None and 2 <= breakeven <= 25:
        fig.add_trace(
            go.Scatter(
                x=[breakeven], y=[0], mode="markers+text",
                marker=dict(size=10, color=SERIES, line=dict(color="white", width=2)),
                text=[f"Breakeven {breakeven:.1f}%"],
                # The line rises left to right, so below-right and above-left of the point stay clear.
                textposition="bottom right" if breakeven <= 20 else "top left",
                hoverinfo="skip",
            )
        )
    return _layout(fig, "Utilisation (%)")
