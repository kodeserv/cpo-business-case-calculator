"""Top-of-page introduction for visitors who are new to EV charging."""

import streamlit as st

_CSS = """
<style>
.hero {
  background: linear-gradient(135deg, #0d3b73 0%, #1f6fd1 100%);
  color: #ffffff;
  border-radius: 16px;
  padding: 2rem 2rem 1.75rem;
  margin-bottom: 1.25rem;
}
.hero .eyebrow { font-size: 0.85rem; letter-spacing: 0.04em; opacity: 0.85; margin: 0 0 0.5rem; }
.hero .eyebrow a { color: #ffffff; }
.hero h1 { color: #ffffff; font-size: 2.2rem; line-height: 1.2; margin: 0 0 0.75rem; padding: 0; }
.hero p { font-size: 1.05rem; line-height: 1.55; margin: 0; max-width: 46rem; }
.hero .hook { margin-top: 0.9rem; font-weight: 600; }
@media (max-width: 640px) {
  .hero { padding: 1.25rem 1.1rem; }
  .hero h1 { font-size: 1.6rem; }
}
</style>
"""

_HERO = """
<div class="hero">
  <p class="eyebrow">CHARGING OPS TOOLKIT · OPEN SOURCE · BY <a href="https://kodeserv.com" target="_blank">KODESERV</a></p>
  <h1>Will this EV charging station make money?</h1>
  <p>A charging station is a small business. It buys electricity from the grid, sells it to
  drivers at a markup, and pays rent, staff and upkeep. This free calculator shows whether
  that business earns back what it cost to build, and how long it takes.</p>
  <p class="hook">India now has more than 29,000 public charging stations, and most are in use
  only a few percent of the time. A few points of usage separate a good site from a loss-maker.</p>
</div>
"""

STEPS = [
    ("1. Pick a site", "Start from a highway fast charger, an apartment society or a fleet depot."),
    ("2. Move the sliders", "Change how busy the site is, what you charge and what electricity costs."),
    ("3. Read the verdict", "See payback, profit and the usage you need to break even, updated instantly."),
]


def render() -> None:
    st.markdown(_CSS + _HERO, unsafe_allow_html=True)
    for col, (title, text) in zip(st.columns(3), STEPS):
        with col.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(text)
