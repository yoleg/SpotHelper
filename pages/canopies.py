import streamlit as st

from ui.canopies import get_canopies, CREDIT_TITLE, CREDIT_URL
from ui.common import common_page_initialization


common_page_initialization("Canopies")

canopies = get_canopies()

st.markdown(f"Data source: [{CREDIT_TITLE}]({CREDIT_URL})")
st.dataframe(canopies, use_container_width=True)