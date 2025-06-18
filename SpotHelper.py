import numpy as np
import matplotlib.pyplot as plt
from Functions import (
    get_winds_aloft_table, get_wind_component_interpolators, get_sat_image,
    meters_to_latlon, simulate_freefall_and_canopy
)
from simulation_config import SimulationConfig


def meters_offset_to_latlon(north_offset, east_offset, lat0, lon0):
    dlat = north_offset / 111320
    dlon = east_offset / (111320 * np.cos(np.radians(lat0)))
    return lat0 + dlat, lon0 + dlon

def make_image(config: SimulationConfig):
    # -------------------- INITIAL CONDITIONS & CONSTANTS --------------------
    # Location (Dropzone)
    IPLat = 39.7065614
    IPLong = -75.0352181

    # Pull Winds
    RawWinds = get_winds_aloft_table(IPLat, IPLong)
    print(RawWinds)
    north_interp, east_interp = get_wind_component_interpolators(RawWinds)

    # First simulation: exit directly over target
    alts, norths, easts, times, phases = simulate_freefall_and_canopy(
        alt0_ft=config.exit_altitude_ft,
        mass_kg=config.mass_kg,
        CdA=config.CdA,
        north_interp=north_interp,
        east_interp=east_interp,
        deploy_alt_ft=config.deploy_altitude_ft,
        canopy_v_vert_fps=config.canopy_v_vert_fps,
        dt=config.dt
    )

    # Calculate required exit offset to land at IPLat/IPLong
    final_north = norths[-1]
    final_east = easts[-1]
    required_north_offset = -final_north
    required_east_offset = -final_east

    exit_lat, exit_lon = meters_offset_to_latlon(required_north_offset, required_east_offset, IPLat, IPLong)
    print(f"Exit at: {exit_lat}, {exit_lon}")

    # Rerun simulation from the new exit point
    alts, norths, easts, times, phases = simulate_freefall_and_canopy(
        alt0_ft=config.exit_altitude_ft,
        mass_kg=config.mass_kg,
        CdA=config.CdA,
        north_interp=north_interp,
        east_interp=east_interp,
        deploy_alt_ft=config.deploy_altitude_ft,
        canopy_v_vert_fps=config.canopy_v_vert_fps,
        dt=config.dt,
        north0=required_north_offset,
        east0=required_east_offset
    )

    # Get satellite image and bounding box
    img, (lat_min, lat_max, lon_min, lon_max) = get_sat_image(
        IPLat, IPLong, zoom=(
            config.sat_img_zoom), size=config.sat_img_size
    )

    # Convert trajectory to lat/lon
    traj_lat, traj_lon = meters_to_latlon(norths, easts, IPLat, IPLong)

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
    circle_lat, circle_lon = meters_to_latlon(circle_north + required_north_offset, circle_east + required_east_offset, IPLat, IPLong)

    # Plot trajectory over satellite image, coloring by phase
    plt.figure(figsize=(8, 8))
    if img is None:
        plt.title('Skydiver Trajectory (No Satellite Image, Phase Colored)')
        print("Satellite image could not be retrieved. Plotting trajectory only.")
    else:
        plt.imshow(img, extent=[lon_min, lon_max, lat_min, lat_max], origin='upper')
        plt.title('Skydiver Trajectory over Yandex Satellite Image (Phase Colored)')
    freefall_mask = np.array(phases) == 0
    canopy_mask = np.array(phases) == 1
    plt.plot(np.array(traj_lon)[freefall_mask], np.array(traj_lat)[freefall_mask], color='red', linewidth=2, label='Freefall')
    plt.plot(np.array(traj_lon)[canopy_mask], np.array(traj_lat)[canopy_mask], color='blue', linewidth=2, label='Canopy')
    plt.plot(circle_lon, circle_lat, color='green', linestyle='--', label='Canopy Glide Circle')
    plt.scatter([exit_lon], [exit_lat], color='cyan', marker='o', label='Exit Point')
    plt.scatter([IPLong], [IPLat], color='yellow', marker='x', label='Dropzone')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()

    final_lat, final_lon = traj_lat[-1], traj_lon[-1]
    print(f"Landing at: {final_lat}, {final_lon}")

    return plt


if __name__ == "__main__":
    plt = make_image(SimulationConfig())
    plt.show()
