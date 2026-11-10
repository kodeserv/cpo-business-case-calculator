import pytest
from pydantic import ValidationError
from streamlit.testing.v1 import AppTest

from cpo_calc.presets import PRESETS
from form import ALL_FIELDS, error_message, from_state, to_state


@pytest.mark.parametrize("key", list(PRESETS))
def test_form_state_round_trips_every_preset(key):
    site = PRESETS[key].inputs
    assert from_state(to_state(site)) == site


def test_form_covers_every_input_field():
    assert len(ALL_FIELDS) == len(to_state(PRESETS["highway_dc"].inputs)) == 28


def test_invalid_form_state_raises():
    state = to_state(PRESETS["highway_dc"].inputs) | {"operations.rent_per_month": 10_000.0}
    with pytest.raises(ValidationError, match="not both"):
        from_state(state)


def test_page_runs_and_switching_preset_loads_its_values():
    at = AppTest.from_file("../app/streamlit_app.py").run()
    assert not at.exception
    at.selectbox(key="preset").select("apartment_ac").run()
    assert at.number_input(key="charger.power_kw").value == 7.4
    assert not at.exception


def test_page_shows_validation_errors_instead_of_crashing():
    at = AppTest.from_file("../app/streamlit_app.py").run()
    at.number_input(key="operations.rent_per_month").set_value(10_000.0).run()
    assert not at.exception
    assert "not both" in at.error[0].value


def test_page_shows_six_tiles_and_scenarios():
    at = AppTest.from_file("../app/streamlit_app.py").run()
    assert [m.label for m in at.metric] == [
        "Net capex", "Payback", "Breakeven utilisation", "Year-3 EBITDA", "NPV", "IRR",
    ]
    assert at.metric[0].value == "₹43.0 L"


def test_errors_name_the_field_they_belong_to():
    state = to_state(PRESETS["highway_dc"].inputs) | {"finance.project_life_years": 40, "charger.count": 0}
    with pytest.raises(ValidationError) as caught:
        from_state(state)
    messages = sorted(error_message(e["loc"], e["msg"]) for e in caught.value.errors())
    assert messages == [
        "Number of chargers: Input should be greater than or equal to 1",
        "Project life (years): Input should be less than or equal to 25",
    ]


def test_cross_field_errors_keep_their_own_message():
    assert error_message(("operations",), "Value error, use either fixed rent or revenue share, not both") == (
        "use either fixed rent or revenue share, not both"
    )
