import streamlit as st

from simulation.fetch import get_winds_aloft_table
from ui.common import common_page_initialization
from ui.input_location import input_location


common_page_initialization("Winds Aloft")

with st.sidebar:
    location = input_location()

winds = get_winds_aloft_table(location)

st.dataframe(winds)
