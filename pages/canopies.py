import streamlit as st
import pandas as pd

from ui.canopies import CREDIT_TITLE, CREDIT_URL, get_canopies, Canopy
from ui.common import common_page_initialization

common_page_initialization("Canopies")

canopies: list[Canopy] = get_canopies()

# Convert the list of Canopy dataclasses to a DataFrame for display
canopies_df: pd.DataFrame = pd.DataFrame([vars(c) for c in canopies])

# Format the DataFrame columns to be more human-readable
canopies_df.columns = [Canopy.format_field_name(col) for col in canopies_df.columns]

st.markdown(f"Data source: [{CREDIT_TITLE}]({CREDIT_URL})")
st.dataframe(canopies_df, use_container_width=True, hide_index=True)