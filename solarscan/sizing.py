def calculate_dc_capacity(usable_area, module_efficiency=0.20):
    """
    Converts usable area into a standard-test-condition DC capacity estimate in Watts.
    Ref: README Section "Mathematical Foundations - 3. DC Array Capacity Sizing"
    Formula: C_array = A_usable * eta_module * 1000 W/m^2
    Returns capacity in kW DC.
    """
    capacity_watts = usable_area * module_efficiency * 1000.0
    return capacity_watts / 1000.0  # Return kW DC


def recommend_inverter_capacity(dc_capacity_kw, dc_ac_ratio=1.2):
    """
    Applies target DC/AC ratio to recommend an AC inverter capacity rating (in kW AC).
    """
    if dc_ac_ratio <= 0:
        return dc_capacity_kw
    ac_capacity_kw = dc_capacity_kw / dc_ac_ratio
    return round(ac_capacity_kw, 2)
