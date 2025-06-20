import streamlit as st

from simulation.data_classes import SimulationConfig
from simulation.fetch import get_winds_aloft_table
from ui.common import common_page_initialization
from ui.input_location import input_location, Location

common_page_initialization("Winds Aloft")

with st.sidebar:
    default = SimulationConfig()
    location = input_location(default=Location(coordinates=default.coordinates, dropzone_name=default.dropzone_name))

winds = get_winds_aloft_table(location.coordinates)
winds = winds.sort_values(by='Altitude (ft)', ascending=False).reset_index(drop=True)

st.dataframe(winds, use_container_width=True, hide_index=True)