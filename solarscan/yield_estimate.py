import math

def calculate_orientation_derate(azimuth_deg, tilt_deg):
    """
    Derives an irradiance derating factor (0.0 to 1.0) based on tilt and azimuth deviation from South (180 deg).
    Optimal: South-facing (180 deg) at tilt matching latitude (~15-25 deg).
    """
    # South is 180 degrees. Absolute deviation from South:
    dev_from_south = abs(((azimuth_deg - 180 + 180) % 360) - 180)
    
    # Simple empirical PV derate model
    azimuth_factor = math.cos(math.radians(dev_from_south / 2))
    tilt_factor = math.cos(math.radians(abs(tilt_deg - 20) / 2))
    
    derate = max(0.5, azimuth_factor * tilt_factor)
    return round(derate, 4)


def estimate_annual_yield(dc_capacity_kw, tilt_deg=15, azimuth_deg=180, peak_sun_hours_per_day=5.5):
    """
    Estimates annual kWh output.
    Default peak sun hours: ~5.5 kWh/m^2/day (e.g. Middle East / Sunny regions).
    Derating factor accounts for system losses, tilt, and orientation.
    """
    derate = calculate_orientation_derate(azimuth_deg, tilt_deg)
    system_loss_factor = 0.85  # standard inverter/wiring loss
    
    annual_kwh = dc_capacity_kw * peak_sun_hours_per_day * 365 * derate * system_loss_factor
    return round(annual_kwh, 2)


def estimate_simple_payback(annual_kwh, rate_per_kwh, cost_per_kw=1000.0, dc_capacity_kw=10.0):
    """
    Estimates simple payback period in years.
    Total system cost = dc_capacity_kw * cost_per_kw
    Annual savings = annual_kwh * rate_per_kwh
    """
    annual_savings = annual_kwh * rate_per_kwh
    total_cost = dc_capacity_kw * cost_per_kw
    
    if annual_savings <= 0:
        return float('inf')
    
    payback_years = total_cost / annual_savings
    return round(payback_years, 2)
