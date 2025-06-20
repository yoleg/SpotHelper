from datetime import datetime, timezone
from io import BytesIO

import numpy as np
import pandas as pd
import requests
import streamlit as st
from pandas import DataFrame
from PIL import Image

from simulation.const import MAP_CACHE_TTL_SECONDS, WINDS_ALOFT_CACHE_TTL_SECONDS
from simulation.data_classes import Coordinates, MapImage


@st.cache_data(ttl=WINDS_ALOFT_CACHE_TTL_SECONDS, show_spinner="Fetching winds aloft")
def get_winds_aloft_table(coordinates: Coordinates) -> DataFrame:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={coordinates.lat}&longitude={coordinates.lon}"
        "&hourly=wind_speed_10m,wind_direction_10m,"
        "wind_speed_80m,wind_direction_80m,"
        "wind_speed_100m,wind_direction_100m,"
        "wind_speed_1000hPa,wind_direction_1000hPa,"
        "wind_speed_925hPa,wind_direction_925hPa,"
        "wind_speed_850hPa,wind_direction_850hPa,"
        "wind_speed_700hPa,wind_direction_700hPa,"
        "wind_speed_500hPa,wind_direction_500hPa,"
        "wind_speed_400hPa,wind_direction_400hPa,"
        "wind_speed_300hPa,wind_direction_300hPa"
        "&windspeed_unit=ms"
    )

    response = requests.get(url)
    data = response.json()
    # print("Raw Open-Meteo response:", data)

    level_to_altitude = {
        "10m": 33,
        "80m": 262,
        "100m": 328,
        "1000hPa": 364,
        "925hPa": 2500,
        "850hPa": 4800,
        "700hPa": 9900,
        "500hPa": 18000,
        "400hPa": 23000,
        "300hPa": 30000,
    }

    levels = [
        "10m", "80m", "100m",
        "1000hPa", "925hPa", "850hPa", "700hPa", "500hPa", "400hPa", "300hPa"
    ]

    times = data['hourly']['time']
    now = datetime.now(timezone.utc)
    current_index = min(
        range(len(times)),
        key=lambda i: abs(
            datetime.fromisoformat(times[i].replace('Z', '+00:00')).astimezone(timezone.utc) - now
        )
    )

    winds = []
    for level in levels:
        speed = data['hourly'][f'wind_speed_{level}'][current_index]
        direction = data['hourly'][f'wind_direction_{level}'][current_index]
        winds.append(
            {
                'Altitude (ft)': level_to_altitude[level],
                'Wind Speed (m/s)': speed,
                'Wind Direction (deg)': direction,
                'Level': level
            }
        )

    df = pd.DataFrame(winds)
    return df


@st.cache_data(ttl=MAP_CACHE_TTL_SECONDS, show_spinner="Fetching satellite image")
def get_satellite_image(coordinates: Coordinates, zoom=13, size=400) -> MapImage | None:
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
