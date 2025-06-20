from dataclasses import dataclass

import pandas as pd
import streamlit as st

from simulation.data_classes import SimulationConfig
from ui.dropzones import df_to_dataclass_list, fetch_dropzones, Dropzone
from simulation.data_classes import LatLon

LATITUDE_KEY = 'location_latitude'
LONGITUDE_KEY = 'location_longitude'


@dataclass(frozen=True)
class Location(LatLon):
    dropzone_index: int = None


def input_location(default: LatLon = None) -> LatLon:
    dropzone_df: pd.DataFrame = fetch_dropzones()
    dropzones: list[Dropzone] = df_to_dataclass_list(dropzone_df)
    dropzone: Dropzone | None = st.selectbox(
        'Dropzone',
        key='dropzone',
        options=[None] + [dz for dz in dropzones],
        format_func=lambda dz: dz.display_name if dz else "",
    )
    default = dropzone.location if dropzone else (default or SimulationConfig().location)

    lat = st.number_input(
        'Location Latitude',
        key=LATITUDE_KEY,
        value=default.lat,
        min_value=-90.0,
        max_value=90.0,
        step=0.0001,
        format="%.6f",
    )
    lon = st.number_input(
        'Location Longitude',
        key=LONGITUDE_KEY,
        value=default.lat,
        min_value=-180.0,
        max_value=180.0,
        step=0.0001,
        format="%.6f",
    )
    return LatLon(lat, lon)
