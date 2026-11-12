import streamlit as st
from pydantic import ValidationError

import charts
import landing
from cpo_calc.finance import evaluate
from cpo_calc.presets import ILLUSTRATIVE_NOTE, PRESETS
from cpo_calc.scenarios import SCENARIO_FACTORS, evaluate_scenarios
from display import pct, rupees_lakh, scenario_table, verdict, yearly_table, years
from form import (
    GROUPS,
    KEY_FIELDS,
    POWER_OPTIONS_KW,
    SLIDERS,
    FormField,
    error_message,
    from_state,
    to_state,
)

DISCLAIMER = "For estimation and learning. Not a certified compliance or financial tool."
REPO_URL = "https://github.com/kodeserv/cpo-business-case-calculator"

FORMAT = {"count": "%d", "kw": "%.0f", "rupees": "%.0f", "rate": "₹%.2f", "pct": "%.1f%%"}
VERDICT_BOX = {"good": st.success, "warn": st.warning, "bad": st.error}
VERDICT_ICON = {"good": "✅", "warn": "⚠️", "bad": "⛔"}


def load_preset() -> None:
    st.session_state.update(to_state(PRESETS[st.session_state.preset].inputs))


def field_input(f: FormField) -> None:
    if f.path == "charger.power_kw":
        st.select_slider(
            f.label, options=POWER_OPTIONS_KW, key=f.path, help=f.hint, format_func=lambda kw: f"{kw:g} kW"
        )
    elif f.path in SLIDERS:
        r = SLIDERS[f.path]
        cast = int if f.kind == "count" else float
        st.slider(
            f.label, min_value=cast(r.low), max_value=cast(r.high), step=cast(r.step),
            key=f.path, help=f.hint, format=FORMAT[f.kind],
        )
    else:
        st.number_input(f.label, key=f.path, help=f.hint, min_value=0.0, step=1_000.0, format=FORMAT[f.kind])


st.set_page_config(page_title="CPO Business Case Calculator", page_icon="⚡", layout="wide")

if "preset" not in st.session_state:
    st.session_state.preset = next(iter(PRESETS))
    load_preset()

landing.render()

st.subheader("Start with a site")
st.selectbox(
    "Start from a preset",
    options=list(PRESETS),
    format_func=lambda key: PRESETS[key].title,
    key="preset",
    on_change=load_preset,
    label_visibility="collapsed",
)
st.caption(f"{PRESETS[st.session_state.preset].summary} {ILLUSTRATIVE_NOTE}")

st.subheader("Try the three numbers that matter most")
fields_by_path = {f.path: f for _, fields in GROUPS for f in fields}
for col, path in zip(st.columns(3), KEY_FIELDS):
    with col:
        field_input(fields_by_path[path])
st.caption("Every other input is in the panel on the left (tap » on a phone).")

with st.sidebar:
    st.header("All inputs")
    for title, fields in GROUPS:
        with st.expander(title, expanded=title == "Site"):
            for f in fields:
                if f.path not in KEY_FIELDS:
                    field_input(f)

try:
    site = from_state(st.session_state)
except ValidationError as e:
    for err in e.errors():
        st.error(error_message(err["loc"], err["msg"]))
    st.stop()

result = evaluate(site)
life = site.finance.project_life_years

level, message = verdict(result, site.finance.discount_rate_pct, life)
VERDICT_BOX[level](message, icon=VERDICT_ICON[level])

tiles = [
    ("Net capex", rupees_lakh(result.net_capex), "Total capex minus subsidy."),
    ("Payback", years(result.payback_years, life), "When cumulative cash turns positive."),
    ("Breakeven utilisation", pct(result.breakeven_utilisation_pct, "Not reachable"),
     "Year-1 utilisation at which EBITDA is zero."),
    ("Year-3 EBITDA", rupees_lakh(result.ebitda_year3) if result.ebitda_year3 is not None else "n/a",
     "Operating profit in year 3, before tax and loan costs."),
    ("NPV", rupees_lakh(result.npv), f"At a {site.finance.discount_rate_pct:g}% discount rate over {life} years."),
    ("IRR", pct(result.irr_pct), "Return at which NPV is zero."),
]
for row in (tiles[:3], tiles[3:]):
    for col, (label, value, hint) in zip(st.columns(3), row):
        col.metric(label, value, help=hint, border=True)

left, right = st.columns(2)
with left:
    st.subheader("Cumulative cash")
    st.plotly_chart(charts.cumulative_cash(result))
with right:
    st.subheader("Year-1 EBITDA by utilisation")
    st.plotly_chart(charts.ebitda_vs_utilisation(site, result))
    if result.breakeven_utilisation_pct is None:
        st.caption(
            f"No utilisation up to your {site.operations.utilisation_ceiling_pct:g}% ceiling "
            "(maximum utilisation or uptime) covers the fixed costs at this margin."
        )
    else:
        st.caption(
            f"Breakeven (dot) at {result.breakeven_utilisation_pct:.1f}% utilisation; "
            f"your year-1 assumption (dashed) is {site.operations.utilisation_pct_year1:g}%."
        )

st.subheader("Scenarios")
factors = ", ".join(
    f"{name}: {u:.0%} of utilisation, {p:.0%} of price" for name, (u, p) in SCENARIO_FACTORS.items() if name != "base"
)
st.caption(f"Same inputs with {factors}.")
st.dataframe(scenario_table(evaluate_scenarios(site), life))

table = yearly_table(result)
with st.expander("Yearly model"):
    st.dataframe(table, hide_index=True)
st.download_button("Download yearly model (CSV)", table.to_csv(index=False), "cpo-business-case.csv", "text/csv")

st.info(f"{DISCLAIMER} {ILLUSTRATIVE_NOTE}")
st.caption(f"Open source under Apache 2.0 · [Source code and formulas on GitHub]({REPO_URL}) · Built by [Kodeserv](https://kodeserv.com)")
