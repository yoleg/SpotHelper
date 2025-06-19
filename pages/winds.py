import streamlit as st

from simulation.fetch import get_winds_aloft_table
from ui.common import common_page_config
from ui.inputs import input_location


common_page_config("Winds Aloft")

with st.sidebar:
    location = input_location()

winds = get_winds_aloft_table(location)

st.dataframe(winds)
