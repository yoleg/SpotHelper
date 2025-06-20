import dataclasses
from dataclasses import dataclass
from pathlib import Path

import streamlit as st
import pandas as pd

from simulation.data_classes import Coordinates

DROPZONES_SOURCE_URL = "https://wingsuit.world/dropzones/"
DROPZONES_SOURCE_NAME = "Wingsuit World"
DATA_DIR = Path(__file__).parent.parent / "data"
DROPZONE_FALLBACK_CSV = DATA_DIR / "dropzones-wingsuit-world.csv"
DROPZONE_ADDITIONAL_CSV = DATA_DIR / "dropzones-extra.csv"  # additional dropzones not on Wingsuit World
WINGSUIT_WORLD_FIELD_MAP = {
    'Elevation (m)': 'ElevationMeters',  # spaces not allowed in field names
    'Location': 'Locality',  # for clarity
    'DZ': 'DZName',  # for clarity
}


@dataclass(frozen=True)
class Dropzone:  # dataclass for type hinting and validation, and immutability
    Latitude: float
    Longitude: float
    ElevationMeters: float
    DZName: str
    Locality: str
    Country: str
    Source: str = ""

    @property
    def display_name(self) -> str:
        if self.DZName:
            return self.DZName
        return f"{self.Locality}, {self.Country}"

    @property
    def location(self) -> Coordinates:
        return Coordinates(self.Latitude, self.Longitude)

    def __str__(self):
        return self.display_name


DROPZONE_FIELDS = {f.name for f in dataclasses.fields(Dropzone)}

def get_dropzones() -> list[Dropzone]:
    df = get_dropzones_df()
    dropzones = [Dropzone(**row) for row in df.to_dict(orient='records')]
    if duplicate_names := len(set(dz.display_name for dz in dropzones)) != len(dropzones):
        st.warning("Warning: Some dropzones have duplicate display names. This may cause confusion in the UI.")
        st.warning(f"Example duplicate names: {[x for x in duplicate_names[:10]]}")
    return dropzones


def get_dropzones_df() -> pd.DataFrame:
    """
    Fetches the dropzones from the Wingsuit World website or falls back to a local CSV file.
    """
    df = _scrape_dropzones_from_website()
    if df is None:
        st.warning(f"No valid dropzone table found at {DROPZONES_SOURCE_URL}. Reverting to CSV fallback.")
        df = pd.read_csv(DROPZONE_FALLBACK_CSV)
        df['Source'] = DROPZONE_FALLBACK_CSV.name

    # add extra dropzones from a local CSV file
    extra = pd.read_csv(DROPZONE_ADDITIONAL_CSV)
    extra['Source'] = DROPZONE_ADDITIONAL_CSV.name
    df = pd.concat([extra, df])

    # replace NaN values with empty strings for string columns
    df[df.select_dtypes(include=['object']).columns] = df.select_dtypes(include=['object']).fillna('')

    return df


@st.cache_data(ttl=3600, show_spinner="Fetching dropzones")
def _scrape_dropzones_from_website() -> pd.DataFrame | None:
    """
    Fetches the dropzones from the Wingsuit World website or falls back to a local CSV file.
    """
    tables = pd.read_html(DROPZONES_SOURCE_URL)
    for table in tables:
        columns = set(table.columns)
        if set(WINGSUIT_WORLD_FIELD_MAP).issubset(columns):
            table['Source'] = DROPZONES_SOURCE_NAME
            table = table.rename(columns=WINGSUIT_WORLD_FIELD_MAP)
            return table
    return None

