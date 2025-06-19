from pathlib import Path

import streamlit as st
import pandas as pd


EXPECTED_DROPZONE_COLUMNS = {'DZ', 'Latitude', 'Longitude'}  # subset of expected columns
DROPZONE_URL = "https://wingsuit.world/dropzones/"
DATA_DIR = Path(__file__).parent.parent / "data"
DROPZONE_FALLBACK_CSV = DATA_DIR / "dropzones.csv"


@st.cache_data(ttl=3600, show_spinner="Fetching dropzones")
def fetch_dropzones():
    tables = pd.read_html(DROPZONE_URL)
    for table in tables:
        columns = set(table.columns)
        if EXPECTED_DROPZONE_COLUMNS.issubset(columns):
            table.index.name = "Index"
            return table

    st.warning(f"No valid dropzone table found at {DROPZONE_URL}. Reverting to CSV source.")
    try:
        # NOTE: you can update this CSV by viewing the Dropzones page and downloading from the dataframe view
        return pd.read_csv(DROPZONE_FALLBACK_CSV, index_col=0)
    except FileNotFoundError:
        st.error(f"Fallback CSV file not found at {DROPZONE_FALLBACK_CSV}.")
        return pd.DataFrame()
