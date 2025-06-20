from dataclasses import dataclass

from PIL import Image


# lat lon coordinates class that can be instantiated without keyword args, namedtuple style
@dataclass(frozen=True)
class Coordinates:
    lat: float
    lon: float

    def __post_init__(self):
        if not (-90 <= self.lat <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if not (-180 <= self.lon <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")

    def __str__(self):
        return f"({self.lat}, {self.lon})"

    def __iter__(self):
        return iter((self.lat, self.lon))


@dataclass
class SimulationConfig:
    dropzone_name: str = "Skydive Cross Keys"
    coordinates: Coordinates = Coordinates(39.7065614, -75.0352181)
    exit_altitude_ft: float = 13000  # Exit altitude (ft)
    canopy_deploy_altitude_ft: float = 3000  # Canopy deployment altitude (ft)
    mass_kg: float = 90  # Skydiver mass (kg)
    freefall_drag_area_m2: float = 0.505  # Drag area (m^2)
    canopy_name: str = "Student (280-200)"
    canopy_vertical_descent_rate_mph: float = 8.5  # Canopy vertical descent rate (ft/s)
    canopy_horizontal_speed_mph: float = 25.0  # Canopy horizontal speed (ft/s) for glide circle
    plot_time_step_s: float = 0.1  # Time step (s)
    satellite_image_zoom: int = 13  # Satellite image zoom level
    satellite_image_size: int = 400  # Satellite image size (pixels)
    plot_circle_resolution: int = 200  # Number of points for glide circle

    @property
    def mass_lb(self):
        return self.mass_kg * 2.20462

    @mass_lb.setter
    def mass_lb(self, value):
        self.mass_kg = value / 2.20462


@dataclass(frozen=True)
class SimulationResults:
    ip: Coordinates
    exit: Coordinates

    circle_latitudes: list
    circle_longitudes: list
    phases: list
    trajectory_latitudes: list
    trajectory_longitudes: list

    @property
    def final_latlon(self) -> Coordinates:
        return Coordinates(self.trajectory_latitudes[-1], self.trajectory_longitudes[-1])


@dataclass(frozen=True)
class MapImage:
    image: Image
    bounding_box: tuple  # (lat_min, lat_max, lon_min, lon_max)
