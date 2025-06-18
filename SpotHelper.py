import logging

import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame

from Functions import (
    get_winds_aloft_table, get_wind_component_interpolators, get_sat_image,
    meters_to_latlon, simulate_freefall_and_canopy
)
from data_classes import SimulationConfig, PlotDisplayParameters, MapImage, LatLon

LOGGER = logging.getLogger(__name__)


def meters_offset_to_latlon(north_offset, east_offset, lat0, lon0):
    dlat = north_offset / 111320
    dlon = east_offset / (111320 * np.cos(np.radians(lat0)))
    return lat0 + dlat, lon0 + dlon


def run_simulation(config: SimulationConfig, winds: DataFrame = None):
    # Pull Winds
    raw_winds = winds or get_winds_aloft_table(config.ip_lat, config.ip_long)
    north_interp, east_interp = get_wind_component_interpolators(raw_winds)

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

    exit_lat, exit_lon = meters_offset_to_latlon(
        required_north_offset, required_east_offset, config.ip_lat, config.ip_long
    )
    LOGGER.info(f"Exit at: {exit_lat}, {exit_lon}")

    # Rerun simulation from the new exit point
    alts, norths, easts, times, phases = simulate_freefall_and_canopy(
        config,
        north_interp=north_interp,
        east_interp=east_interp,
        north0=required_north_offset,
        east0=required_east_offset,
    )

    # Get satellite image and bounding box
    satellite_image = get_sat_image(config.ip_lat, config.ip_long, zoom=config.sat_img_zoom, size=config.sat_img_size)

    # Convert trajectory to lat/lon
    traj_lat, traj_lon = meters_to_latlon(norths, easts, config.ip_lat, config.ip_long)

    # Calculate canopy glide distance (in meters)
    canopy_v_vert_mps = config.canopy_v_vert_fps * 0.3048
    canopy_v_horiz_mps = config.canopy_v_horiz_fps * 0.3048
    deploy_alt_m = config.deploy_altitude_ft * 0.3048

    # Time under canopy (seconds)
    canopy_time = deploy_alt_m / canopy_v_vert_mps
    # Glide distance (meters)
    glide_distance = canopy_v_horiz_mps * canopy_time

    # Generate circle points around exit location
    theta = np.linspace(0, 2 * np.pi, config.circle_resolution)
    circle_north = glide_distance * np.cos(theta)
    circle_east = glide_distance * np.sin(theta)
    circle_lat, circle_lon = meters_to_latlon(
        circle_north + required_north_offset, circle_east + required_east_offset,
        config.ip_lat, config.ip_long
    )

    exit_latlon = LatLon(exit_lat, exit_lon)
    ip_latlon = LatLon(config.ip_lat, config.ip_long)
    plot_params = PlotDisplayParameters(
        ip=ip_latlon,
        exit=exit_latlon,
        circle_lat=circle_lat,
        circle_lon=circle_lon,
        phases=phases,
        traj_lat=traj_lat,
        traj_lon=traj_lon
    )
    make_plot(plot_params, map_image=satellite_image)

    final_latlon = LatLon(traj_lat[-1], traj_lon[-1])
    LOGGER.info(f"Landing at: {final_latlon}")

    return plt


def make_plot(params: PlotDisplayParameters, map_image: MapImage = None):
    plt.figure(figsize=(8, 8))
    if map_image is None:
        plt.title('Skydiver Trajectory (No Satellite Image, Phase Colored)')
        LOGGER.info("Satellite image could not be retrieved. Plotting trajectory only.")
    else:
        ax = plt.gca()
        ax.imshow(
            map_image.image,
            extent=(map_image.bounding_box[2], map_image.bounding_box[3], map_image.bounding_box[0], map_image.bounding_box[1]),
            aspect='auto',
            origin='upper',
            zorder=0
        )
        ax.set_xlim(map_image.bounding_box[2], map_image.bounding_box[3])
        ax.set_ylim(map_image.bounding_box[0], map_image.bounding_box[1])
        plt.title('Skydiver Trajectory over Yandex Satellite Image (Phase Colored)')
    freefall_mask = np.array(params.phases) == 0
    canopy_mask = np.array(params.phases) == 1
    plt.plot(
        np.array(params.traj_lon)[freefall_mask],
        np.array(params.traj_lat)[freefall_mask],
        color='red',
        linewidth=2,
        label='Freefall'
    )
    plt.plot(
        np.array(params.traj_lon)[canopy_mask],
        np.array(params.traj_lat)[canopy_mask],
        color='blue',
        linewidth=2,
        label='Canopy'
    )
    plt.plot(params.circle_lon, params.circle_lat, color='green', linestyle='--', label='Canopy Glide Circle')
    plt.scatter([params.exit.lon], [params.exit.lat], color='cyan', marker='o', label='Exit Point')
    plt.scatter([params.ip.lon], [params.ip.lat], color='yellow', marker='x', label='Dropzone')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()


if __name__ == "__main__":
    plt = run_simulation(SimulationConfig())
    plt.show()
