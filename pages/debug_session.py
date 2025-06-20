import dataclasses

import streamlit as st

from ui.input_simulation_config import form_simulation_config
from simulation.data_classes import SimulationConfig
from ui.common import common_page_initialization
from ui.input_location import input_location

common_page_initialization("Debug Session")


with st.sidebar:
    default = SimulationConfig()
    with st.expander("Location", expanded=True):
        location = input_location(default=default.location)
    config = form_simulation_config(default=dataclasses.replace(default, location=location))

st.write(st.session_state)
