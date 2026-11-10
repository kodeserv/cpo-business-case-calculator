import pytest

from cpo_calc.presets import PRESETS


def test_three_presets_in_display_order():
    assert list(PRESETS) == ["highway_dc", "apartment_ac", "fleet_depot_dc"]


@pytest.mark.parametrize(
    ("key", "power_kw", "chargers"),
    [("highway_dc", 120, 2), ("apartment_ac", 29.6, 4), ("fleet_depot_dc", 120, 4)],
)
def test_preset_site_size(key, power_kw, chargers):
    site = PRESETS[key].inputs
    assert site.total_power_kw == pytest.approx(power_kw)
    assert site.charger_count == chargers


@pytest.mark.parametrize("key", list(PRESETS))
def test_contracted_load_covers_dc_chargers(key):
    site = PRESETS[key].inputs
    if site.energy.contracted_load_kva:
        assert site.energy.contracted_load_kva >= site.total_power_kw
