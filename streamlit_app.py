import logging

import streamlit as st

logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
logging.getLogger('tornado.access').setLevel(logging.WARNING)

pages = [
    st.Page(r"pages\spot_helper.py", title="Spot Helper Demo", icon="🪂"),
    st.Page(r"pages\winds.py", title="Winds Aloft", icon="🌬️"),
    st.Page(r"pages\dropzones.py", title="Dropzone List", icon="📃"),
    st.Page(r"pages\canopies.py", title="Canopies List", icon="📃"),
    st.Page(r"pages\debug_session.py", title="Debug: Session State", icon="🐞"),
]
nav = st.navigation(pages, position="sidebar", expanded=True)
nav.run()
