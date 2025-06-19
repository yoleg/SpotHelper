import logging

import streamlit as st

logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
logging.getLogger('tornado.access').setLevel(logging.WARNING)

spot_helper_page = st.Page("pages\spot_helper.py", title="Spot Helper Demo", icon="🪂")
dropzone_page = st.Page("pages\dropzones.py", title="Dropzones", icon="📍")
winds_aloft_page = st.Page("pages\winds.py", title="Winds Aloft", icon="🌬️")
pages = [
    spot_helper_page,
    winds_aloft_page,
    dropzone_page,
]
nav = st.navigation(pages, position="sidebar", expanded=True)
nav.run()
