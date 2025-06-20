import numpy as np
from scipy.interpolate import interp1d

from simulation.data_classes import Coordinates, SimulationConfig


def get_wind_component_interpolators(wind_df):
    """
    Given a DataFrame with 'Altitude (ft)', 'Wind Speed (m/s)', and 'Wind Direction (deg)',
    returns two interpolation functions: north_wind(altitude_ft), east_wind(altitude_ft).
    """
    altitudes = wind_df["Altitude (ft)"].values
    wind_speeds = wind_df["Wind Speed (m/s)"].values
    wind_dirs = wind_df["Wind Direction (deg)"].values

    # Calculate components
    north_winds = wind_speeds * np.cos(np.radians(wind_dirs)) * -1
    east_winds = wind_speeds * np.sin(np.radians(wind_dirs)) * -1

    # Create interpolation functions
    north_interp = interp1d(altitudes, north_winds, kind='linear', fill_value="extrapolate")
    east_interp = interp1d(altitudes, east_winds, kind='linear', fill_value="extrapolate")

    return north_interp, east_interp


def meters_to_latlon(north, east, location: Coordinates):
    """
    Converts north/east meters to latitude/longitude offsets from (lat0, lon0).
    Returns arrays of latitudes and longitudes.
    """
    dlat = north / 111320  # meters per degree latitude
    dlon = east / (40075000 * np.cos(np.radians(location.lat)) / 360)
    return location.lat + dlat, location.lon + dlon


def air_pressure(alt_m):
    """
    Returns air pressure in Pascals at altitude alt_m (meters) using the barometric formula.
    """
    P0 = 101325  # Sea level standard atmospheric pressure, Pa
    L = 0.0065  # Temperature lapse rate, K/m
    T0 = 288.15  # Sea level standard temperature, K
    g = 9.80665  # Gravity, m/s^2
    M = 0.0289644  # Molar mass of dry air, kg/mol
    R = 8.3144598  # Universal gas constant, J/(mol·K)
    return P0 * (1 - L * alt_m / T0) ** (g * M / (R * L))


def simulate_freefall(
        alt0_ft,
        mass_kg,
        CdA,
        north_interp,
        east_interp,
        dt=0.1,
        v_vert0=0.0,
        north0=0.0,
        east0=0.0
):
    """
    Simulate a skydiver's freefall with altitude-dependent air pressure/density and wind drift.
    Returns arrays: alts_ft, norths_m, easts_m, times_s
    """
    alt = alt0_ft * 0.3048  # initial altitude in meters
    v_vert = v_vert0  # initial vertical velocity (down, m/s)
    north = north0  # initial north position (meters)
    east = east0  # initial east position (meters)
    g = 9.81  # gravity (m/s^2)

    alts = []
    norths = []
    easts = []
    times = []

    t = 0.0
    while alt > 0:
        alt_ft = alt / 0.3048
        wind_north = north_interp(alt_ft)
        wind_east = east_interp(alt_ft)

        # Air pressure and temperature at this altitude
        pressure = air_pressure(alt)
        temp = 288.15 - 0.0065 * alt

        # Air density
        R_specific = 287.058
        rho = pressure / (R_specific * temp)

        # Drag force
        drag = 0.5 * rho * v_vert ** 2 * CdA * np.sign(v_vert)
        F_net = mass_kg * g - drag
        a = F_net / mass_kg

        v_vert += a * dt
        alt -= v_vert * dt

        north += wind_north * dt
        east += wind_east * dt

        alts.append(alt / 0.3048)
        norths.append(north)
        easts.append(east)
        times.append(t)
        t += dt

    return np.array(alts), np.array(norths), np.array(easts), np.array(times)


def simulate_freefall_and_canopy(
        config: SimulationConfig,
        north_interp: callable,
        east_interp: callable,
        v_vert0: float = 0.0,
        north0: float = 0.0,
        east0: float = 0.0,
):
    """
    Simulate freefall to deploy_alt_ft, then non-gliding canopy descent at canopy_v_vert_fps.
    Returns arrays: alts_ft, norths_m, easts_m, times_s, phases (0=freefall, 1=canopy)
    """
    alt = config.exit_altitude_ft * 0.3048
    deploy_alt_m = config.canopy_deploy_altitude_ft * 0.3048
    v_vert = v_vert0
    north = north0
    east = east0
    g = 9.81

    canopy_v_vert_mps = config.canopy_vertical_descent_rate_mph * 0.44704  # Convert mph to m/s

    alts = []
    norths = []
    easts = []
    times = []
    phases = []

    t = 0.0
    # phase: 0 = freefall, 1 = canopy

    while alt > 0:
        alt_ft = alt / 0.3048
        wind_north = north_interp(alt_ft)
        wind_east = east_interp(alt_ft)

        if alt > deploy_alt_m:
            # Freefall phase
            pressure = air_pressure(alt)
            temp = 288.15 - 0.0065 * alt
            R_specific = 287.058
            rho = pressure / (R_specific * temp)
            drag = 0.5 * rho * v_vert ** 2 * config.freefall_drag_area_m2 * np.sign(v_vert)
            F_net = config.mass_lb * g - drag
            a = F_net / config.mass_lb
            v_vert += a * config.plot_time_step_s
            alt -= v_vert * config.plot_time_step_s
            north += wind_north * config.plot_time_step_s
            east += wind_east * config.plot_time_step_s
            phase = 0
        else:
            # Non-gliding canopy: only wind drift, constant vertical descent
            v_vert = canopy_v_vert_mps
            north += wind_north * config.plot_time_step_s
            east += wind_east * config.plot_time_step_s
            alt -= v_vert * config.plot_time_step_s
            phase = 1

        alts.append(alt / 0.3048)
        norths.append(north)
        easts.append(east)
        times.append(t)
        phases.append(phase)
        t += config.plot_time_step_s

    return np.array(alts), np.array(norths), np.array(easts), np.array(times), np.array(phases)
