from pathlib import Path

import streamlit as st
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
CANOPY_CSV = DATA_DIR / "canopies.csv"
CREDIT_URL = "https://www.skydivemag.com/new/2017-03-10-dying-for-airspeed/"
CREDIT_TITLE = "Dying for Airspeed"


def get_canopies() -> pd.DataFrame:
    return pd.read_csv(CANOPY_CSV, index_col=0)
