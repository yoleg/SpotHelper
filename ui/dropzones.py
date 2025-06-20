import dataclasses
from dataclasses import dataclass
from pathlib import Path

import streamlit as st
import pandas as pd

from simulation.data_classes import Coordinates

EXPECTED_DROPZONE_COLUMNS = {'DZ', 'Latitude', 'Longitude'}  # subset of expected columns
DROPZONES_SOURCE_URL = "https://wingsuit.world/dropzones/"
DROPZONES_SOURCE_NAME = "Wingsuit World"
DATA_DIR = Path(__file__).parent.parent / "data"
DROPZONE_FALLBACK_CSV = DATA_DIR / "dropzones-wingsuit-world.csv"
DROPZONE_ADDITIONAL_CSV = DATA_DIR / "dropzones-extra.csv"  # additional dropzones not on Wingsuit World
DROPZONE_FIELD_REPLACEMENTS = {
    'Elevation (m)': 'ElevationMeters',  # spaces not allowed in field names
}
INDEX_COLS = ['DZ', 'Location', 'Country']


@dataclass(frozen=True)
class Dropzone:  # dataclass for type hinting and validation, and immutability
    DZ: str
    Latitude: float
    Longitude: float
    Location: str
    Country: str
    ElevationMeters: float
    Source: str = ""

    @property
    def location_display_name(self) -> str:
        if self.Location and self.Country:
            return f"{self.Location}, {self.Country}"
        if self.Location:
            return self.Location
        if self.Country:
            return self.Country
        return "unknown location"

    @property
    def display_name(self) -> str:
        if self.DZ:
            return f"{self.DZ} ({self.location_display_name})"
        return f"unknown name at {self.location_display_name}"

    @property
    def location(self) -> Coordinates:
        return Coordinates(self.Latitude, self.Longitude)

    def __str__(self):
        return self.display_name


DROPZONE_FIELDS = {f.name for f in dataclasses.fields(Dropzone)}

def get_dropzones() -> list[Dropzone]:
    df = get_dropzones_df()
    return df_to_dataclass_list(df)

def df_to_dataclass_list(df: pd.DataFrame) -> list[Dropzone]:
    df = df.rename(columns=DROPZONE_FIELD_REPLACEMENTS)

    if not DROPZONE_FIELDS.issubset(df.columns):
        raise ValueError(f"DataFrame must contain the following fields: {DROPZONE_FIELDS}")

    return [Dropzone(**row) for row in df.to_dict(orient='records')]


def get_dropzones_df() -> pd.DataFrame:
    """
    Fetches the dropzones from the Wingsuit World website or falls back to a local CSV file.
    """
    df = _fetch_dropzones()
    if df is None:
        st.warning(f"No valid dropzone table found at {DROPZONES_SOURCE_URL}. Reverting to CSV fallback.")
        df = pd.read_csv(DROPZONE_FALLBACK_CSV)
        df['Source'] = DROPZONE_FALLBACK_CSV.name

    # add extra dropzones from a local CSV file
    extra = pd.read_csv(DROPZONE_ADDITIONAL_CSV)
    extra['Source'] = DROPZONE_ADDITIONAL_CSV.name
    df = pd.concat([extra, df])

    df.index = pd.MultiIndex.from_frame(df[INDEX_COLS], names=INDEX_COLS)
    if not df.index.is_unique:
        st.warning("Dropzone DataFrame index must be unique. Check for duplicate entries.")

    # replace NaN values with empty strings for string columns
    df[df.select_dtypes(include='object').columns].fillna('', inplace=True)

    return df


@st.cache_data(ttl=3600, show_spinner="Fetching dropzones")
def _fetch_dropzones() -> pd.DataFrame | None:
    """
    Fetches the dropzones from the Wingsuit World website or falls back to a local CSV file.
    """
    tables = pd.read_html(DROPZONES_SOURCE_URL)
    for table in tables:
        columns = set(table.columns)
        if EXPECTED_DROPZONE_COLUMNS.issubset(columns):
            table['Source'] = DROPZONES_SOURCE_NAME
            return table
    return None

