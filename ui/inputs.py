import streamlit as st

from simulation.data_classes import LatLon, SimulationConfig


def input_location(default: LatLon = None) -> LatLon:
    default = default or SimulationConfig().location
    lat = st.number_input(
        'Dropzone Latitude', min_value=-90.0, max_value=90.0, value=default.lat, step=0.0001, format="%.6f"
    )
    lon = st.number_input(
        'Dropzone Longitude',
        min_value=-180.0,
        max_value=180.0,
        value=default.lon,
        step=0.0001,
        format="%.6f"
    )
    return LatLon(lat, lon)
