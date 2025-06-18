from dataclasses import dataclass


@dataclass
class SimulationConfig:
    ip_lat: float = 39.7065614
    ip_long: float = -75.0352181

    exit_altitude_ft: float = 13000  # Exit altitude (ft)
    deploy_altitude_ft: float = 3000  # Canopy deployment altitude (ft)
    mass_kg: float = 90  # Skydiver mass (kg)
    CdA: float = 0.505  # Drag area (m^2)
    canopy_v_vert_fps: float = 8  # Canopy vertical descent rate (ft/s)
    canopy_v_horiz_fps: float = 24  # Canopy horizontal speed (ft/s) for glide circle
    dt: float = 0.1  # Time step (s)
    sat_img_zoom: int = 13  # Satellite image zoom level
    sat_img_size: int = 400  # Satellite image size (pixels)
    circle_resolution: int = 200  # Number of points for glide circle
