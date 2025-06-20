import numpy as np
from pandas import DataFrame

from simulation.data_classes import Coordinates, SimulationConfig, SimulationResults
from simulation.functions import get_wind_component_interpolators, meters_to_latlon, simulate_freefall_and_canopy


def run_simulation(config: SimulationConfig, winds: DataFrame) -> SimulationResults:
    # Pull Winds
    ip_latlon = config.coordinates
    north_interp, east_interp = get_wind_component_interpolators(winds)

    # First simulation: exit directly over target
    alts, norths, easts, times, phases = simulate_freefall_and_canopy(
        config,
        north_interp=north_interp,
        east_interp=east_interp,
    )

    # Calculate required exit offset to land at IPLat/IPLong
    final_north = norths[-1]
    final_east = easts[-1]
    required_north_offset = -final_north
    required_east_offset = -final_east

    exit_latlon = meters_offset_to_latlon(required_north_offset, required_east_offset, ip_latlon)

    # Rerun simulation from the new exit point
    alts, norths, easts, times, phases = simulate_freefall_and_canopy(
        config,
        north_interp=north_interp,
        east_interp=east_interp,
        north0=required_north_offset,
        east0=required_east_offset,
    )

    # Convert trajectory to lat/lon
    traj_lat, traj_lon = meters_to_latlon(norths, easts, ip_latlon)

    # Calculate canopy glide distance (in meters)
    canopy_v_vert_mps = config.canopy_vertical_descent_rate_mph * 0.44704  # Convert mph to m/s
    canopy_v_horiz_mps = config.canopy_horizontal_speed_mph * 0.44704  # Convert mph to m/s
    deploy_alt_m = config.canopy_deploy_altitude_ft * 0.3048

    # Time under canopy (seconds)
    canopy_time = deploy_alt_m / canopy_v_vert_mps
    # Glide distance (meters)
    glide_distance = canopy_v_horiz_mps * canopy_time

    # Generate circle points around exit location
    theta = np.linspace(0, 2 * np.pi, config.plot_circle_resolution)
    circle_north = glide_distance * np.cos(theta)
    circle_east = glide_distance * np.sin(theta)
    circle_lat, circle_lon = meters_to_latlon(
        circle_north + required_north_offset, circle_east + required_east_offset,
        config.coordinates
    )

    return SimulationResults(
        ip=ip_latlon,
        exit=exit_latlon,
        circle_latitudes=circle_lat,
        circle_longitudes=circle_lon,
        phases=phases,
        trajectory_latitudes=traj_lat,
        trajectory_longitudes=traj_lon
    )


def meters_offset_to_latlon(north_offset, east_offset, location: Coordinates):
    dlat = north_offset / 111320
    dlon = east_offset / (111320 * np.cos(np.radians(location.lat)))
    return Coordinates(location.lat + dlat, location.lon + dlon)