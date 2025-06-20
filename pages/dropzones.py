import streamlit as st

from ui.common import common_page_initialization
from ui.dropzones import DROPZONES_SOURCE_NAME, DROPZONES_SOURCE_URL, get_dropzones

common_page_initialization("Dropzones")


st.markdown(f"Data source: [{DROPZONES_SOURCE_NAME}]({DROPZONES_SOURCE_URL})")
dropzones = get_dropzones()
st.dataframe(dropzones, use_container_width=True, hide_index=True)
