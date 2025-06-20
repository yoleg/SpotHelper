import logging

import streamlit as st


def common_setup():
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    logging.getLogger('tornado.access').setLevel(logging.WARNING)

    # a hack to prevent Streamlit from clearing session state between page reloads
    for key in st.session_state:
        st.session_state[key] = st.session_state[key]


def common_page_initialization(name: str):
    st.set_page_config(
        page_title=name,
        page_icon="🪂",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    common_setup()

    st.title(name)

