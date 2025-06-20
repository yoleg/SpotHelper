import dataclasses
from dataclasses import dataclass
from pathlib import Path

import streamlit as st
import pandas as pd

from simulation.data_classes import LatLon

EXPECTED_DROPZONE_COLUMNS = {'DZ', 'Latitude', 'Longitude'}  # subset of expected columns
DROPZONES_SOURCE_URL = "https://wingsuit.world/dropzones/"
DROPZONES_SOURCE_NAME = "Wingsuit World"
DATA_DIR = Path(__file__).parent.parent / "data"
DROPZONE_FALLBACK_CSV = DATA_DIR / "dropzones.csv"
DROPZONE_FIELD_REPLACEMENTS = {
    'Elevation (m)': 'ElevationMeters',  # spaces not allowed in field names
}


@dataclass(frozen=True)
class Dropzone:  # dataclass for type hinting and validation, and immutability
    DZ: str
    Latitude: float
    Longitude: float
    Location: str
    Country: str
    ElevationMeters: float

    @property
    def display_name(self) -> str:
        location_name = f"{self.Location or 'unknown locality'}, {self.Country or 'unknown country'}"
        return f"{self.DZ or 'unknown name'} ({location_name})"

    @property
    def location(self) -> LatLon:
        return LatLon(self.Latitude, self.Longitude)


DROPZONE_FIELDS = {f.name for f in dataclasses.fields(Dropzone)}


def df_to_dataclass_list(df: pd.DataFrame) -> list[Dropzone]:
    df = df.rename(columns=DROPZONE_FIELD_REPLACEMENTS)

    # replace NaN with empty strings for string columns
    df[df.select_dtypes(include='object').columns].fillna('', inplace=True)

    if not DROPZONE_FIELDS.issubset(df.columns):
        raise ValueError(f"DataFrame must contain the following fields: {DROPZONE_FIELDS}")

    return [Dropzone(**row) for row in df.to_dict(orient='records')]


@st.cache_data(ttl=3600, show_spinner="Fetching dropzones")
def fetch_dropzones() -> pd.DataFrame:
    """
    Fetches the dropzones from the Wingsuit World website or falls back to a local CSV file.
    """
    tables = pd.read_html(DROPZONES_SOURCE_URL)
    for table in tables:
        columns = set(table.columns)
        if EXPECTED_DROPZONE_COLUMNS.issubset(columns):
            table.index.name = "Index"
            return table

    st.warning(f"No valid dropzone table found at {DROPZONES_SOURCE_URL}. Reverting to CSV source.")
    try:
        # NOTE: you can update this CSV by viewing the Dropzones page and downloading from the dataframe view
        return pd.read_csv(DROPZONE_FALLBACK_CSV, index_col=0)
    except FileNotFoundError:
        st.error(f"Fallback CSV file not found at {DROPZONE_FALLBACK_CSV}.")
        return pd.DataFrame()
