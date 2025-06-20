import streamlit as st

from ui.common import common_page_initialization
from ui.dropzones import fetch_dropzones, DROPZONES_SOURCE_URL, DROPZONES_SOURCE_NAME

common_page_initialization("Dropzones")


st.markdown(f"Data source: [{DROPZONES_SOURCE_NAME}]({DROPZONES_SOURCE_URL})")
dropzones = fetch_dropzones()
st.dataframe(dropzones)
