from dataclasses import dataclass

from PIL import Image


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


# lat lon coordinates class that can be instantiated without keyword args, namedtuple style
@dataclass
class LatLon:
    lat: float
    lon: float

    def __post_init__(self):
        if not (-90 <= self.lat <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if not (-180 <= self.lon <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")


@dataclass
class PlotDisplayParameters:
    ip: LatLon
    exit: LatLon

    circle_lat: list
    circle_lon: list
    phases: list
    traj_lat: list
    traj_lon: list


@dataclass
class MapImage:
    image: Image
    bounding_box: tuple  # (lat_min, lat_max, lon_min, lon_max)



@dataclass
class SimulationResults:
    final: LatLon
