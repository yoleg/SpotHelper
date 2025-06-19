import logging
from io import BytesIO
from threading import RLock

import numpy as np
import requests
import streamlit as st
from matplotlib import pyplot as plt
from PIL import Image

from const import MAP_CACHE_TTL_SECONDS
from data_classes import LatLon, MapImage, SimulationResults

LOGGER = logging.getLogger(__name__)

PLOT_LOCK = RLock()


def make_plot(params: SimulationResults, map_image: MapImage = None):
    with PLOT_LOCK:
        if not isinstance(params, SimulationResults):
            raise TypeError("params must be an instance of PlotDisplayParameters")
        if map_image is not None and not isinstance(map_image, MapImage):
            raise TypeError("map_image must be an instance of MapImage or None")
        return _make_plot(params, map_image)


def _make_plot(params: SimulationResults, map_image: MapImage = None):
    fig, ax = plt.subplots(figsize=(8, 8))
    if map_image is None:
        ax.set_title('Skydiver Trajectory (No Satellite Image, Phase Colored)')
    else:
        ax.imshow(
            map_image.image,
            extent=(map_image.bounding_box[2], map_image.bounding_box[3], map_image.bounding_box[0], map_image.bounding_box[1]),
            aspect='auto',
            origin='upper',
            zorder=0
        )
        ax.set_xlim(map_image.bounding_box[2], map_image.bounding_box[3])
        ax.set_ylim(map_image.bounding_box[0], map_image.bounding_box[1])
        ax.set_title('Skydiver Trajectory over Yandex Satellite Image (Phase Colored)')
    freefall_mask = np.array(params.phases) == 0
    canopy_mask = np.array(params.phases) == 1
    ax.plot(
        np.array(params.trajectory_longitudes)[freefall_mask],
        np.array(params.trajectory_latitudes)[freefall_mask],
        color='red',
        linewidth=2,
        label='Freefall'
    )
    ax.plot(
        np.array(params.trajectory_longitudes)[canopy_mask],
        np.array(params.trajectory_latitudes)[canopy_mask],
        color='blue',
        linewidth=2,
        label='Canopy'
    )
    ax.plot(params.circle_longitudes, params.circle_latitudes, color='green', linestyle='--', label='Canopy Glide Circle')
    ax.scatter([params.exit.lon], [params.exit.lat], color='cyan', marker='o', label='Exit Point')
    ax.scatter([params.ip.lon], [params.ip.lat], color='yellow', marker='x', label='Dropzone')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend()
    return fig


@st.cache_data(ttl=MAP_CACHE_TTL_SECONDS, show_spinner="Fetching satellite image")
def get_satellite_image(coordinates: LatLon, zoom=13, size=400) -> MapImage | None:
    """
    Downloads a satellite image centered at (latitude, longitude) using Yandex Static Maps.
    Returns a PIL Image and the bounding box (lat_min, lat_max, lon_min, lon_max).
    """
    latitude = coordinates.lat
    longitude = coordinates.lon
    url = (
        "https://static-maps.yandex.ru/1.x/"
        f"?ll={longitude},{latitude}"
        f"&z={zoom}"
        f"&l=sat"
        f"&size={size},{size}"
    )
    resp = requests.get(url)
    if 'image' not in resp.headers.get('Content-Type', ''):
        print("Yandex did not return an image. Response headers:", resp.headers)
        print("Response content (truncated):", resp.content[:200])
        return None
    img = Image.open(BytesIO(resp.content))

    meters_per_pixel = 156543.03392 * np.cos(np.radians(latitude)) / (2 ** zoom)
    half_side_m = (size / 2) * meters_per_pixel
    dlat = (half_side_m / 111320)
    dlon = half_side_m / (40075000 * np.cos(np.radians(latitude)) / 360)
    lat_min = latitude - dlat
    lat_max = latitude + dlat
    lon_min = longitude - dlon
    lon_max = longitude + dlon

    return MapImage(
        image=img,
        bounding_box=(lat_min, lat_max, lon_min, lon_max)
    )
