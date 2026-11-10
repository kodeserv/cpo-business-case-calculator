from cpo_calc.models import Capex, ChargerGroup, Energy, Finance, Operations, Revenue, SiteInputs


def simple_site(**ops) -> SiteInputs:
    """10 kW, 10% utilisation, full uptime, Rs 10/kWh after GST, Rs 5/kWh energy, no losses."""
    return SiteInputs(
        chargers=[ChargerGroup(power_kw=10, count=1, hardware_cost_each=100_000)],
        capex=Capex(),
        energy=Energy(energy_charge_per_kwh=5, losses_pct=0),
        revenue=Revenue(price_per_kwh_incl_gst=11.8, gst_pct=18),
        operations=Operations(utilisation_pct_year1=10, uptime_pct=100, om_per_charger_year=10_000, **ops),
        finance=Finance(project_life_years=3),
    )
