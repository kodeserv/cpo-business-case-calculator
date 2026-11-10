import streamlit as st
from pydantic import ValidationError

from cpo_calc.finance import evaluate
from cpo_calc.presets import ILLUSTRATIVE_NOTE, PRESETS
from form import GROUPS, FormField, from_state, to_state

STEP = {"count": 1, "kw": 1.0, "rupees": 1_000.0, "rate": 0.5, "pct": 0.5}
MAX = {"pct": 100.0}


def load_preset() -> None:
    st.session_state.update(to_state(PRESETS[st.session_state.preset].inputs))


def number_input(f: FormField) -> None:
    st.number_input(
        f.label,
        key=f.path,
        help=f.hint,
        min_value=1 if f.kind == "count" else 0.0,
        max_value=MAX.get(f.kind),
        step=STEP[f.kind],
    )


st.set_page_config(page_title="CPO Business Case Calculator", page_icon="⚡", layout="wide")

if "preset" not in st.session_state:
    st.session_state.preset = next(iter(PRESETS))
    load_preset()

st.title("CPO Business Case Calculator")
st.caption("Will an EV charging site in India pay back, and at what utilisation does it break even?")

st.selectbox(
    "Start from a preset",
    options=list(PRESETS),
    format_func=lambda key: PRESETS[key].title,
    key="preset",
    on_change=load_preset,
)
st.caption(f"{PRESETS[st.session_state.preset].summary} {ILLUSTRATIVE_NOTE}")

with st.sidebar:
    st.header("Your site")
    for title, fields in GROUPS:
        with st.expander(title, expanded=title == "Site"):
            for f in fields:
                number_input(f)

try:
    site = from_state(st.session_state)
except ValidationError as e:
    for err in e.errors():
        st.error(err["msg"].removeprefix("Value error, "))
    st.stop()

result = evaluate(site)
st.write(f"Net capex Rs {result.net_capex:,.0f}, payback {result.payback_years} years")
