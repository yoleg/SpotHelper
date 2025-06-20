import streamlit as st

from ui.input_simulation_config import form_simulation_config
from simulation.data_classes import SimulationConfig
from ui.common import common_page_initialization

common_page_initialization("Debug Page")


with st.sidebar:
    default = SimulationConfig()
    config = form_simulation_config()

st.header("Session State")
st.write(st.session_state)

st.header("Active Configuration")
st.write(config)
