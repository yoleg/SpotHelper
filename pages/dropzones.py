import streamlit as st

from ui.common import common_page_config
from ui.dropzones import fetch_dropzones

common_page_config("Dropzones")

dropzones = fetch_dropzones()
st.dataframe(dropzones)
