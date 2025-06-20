import logging
from pathlib import Path

import streamlit as st

pages_root = Path(__file__).parent
pages = [
    st.Page(pages_root / r"pages/spot_helper.py", title="Spot Helper Demo", icon="🪂"),
    st.Page(pages_root / r"pages/winds.py", title="Winds Aloft", icon="🌬️"),
    st.Page(pages_root / r"pages/dropzones.py", title="Dropzone List", icon="📃"),
    st.Page(pages_root / r"pages/canopies.py", title="Canopies List", icon="📃"),
    st.Page(pages_root / r"pages/debug.py", title="Debug", icon="🐞"),
]
nav = st.navigation(pages, position="sidebar", expanded=True)
nav.run()
