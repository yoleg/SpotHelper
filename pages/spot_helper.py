import io

import streamlit as st

from simulation.data_classes import SimulationConfig
from simulation.fetch import get_satellite_image, get_winds_aloft_table
from simulation.simulation import run_simulation
from simulation.plot import make_plot
from ui.common import common_page_initialization
from ui.input_simulation_config import form_simulation_config

common_page_initialization("Spot Helper Demo")


def main():
    with st.sidebar:
        config = form_simulation_config()

    winds = get_winds_aloft_table(config.location)
    simulation_results = run_simulation(config, winds=winds)
    satellite_image = get_satellite_image(config.location, zoom=config.satellite_image_zoom, size=config.satellite_image_size)
    if not satellite_image:
        st.warning("Satellite image could not be retrieved. Plotting trajectory only.")
    fig = make_plot(simulation_results, map_image=satellite_image)

    image_download_button(fig)

    st.pyplot(fig, use_container_width=True)

    st.markdown(f"*Landing at: {simulation_results.final_latlon}*")


def image_download_button(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img_buf = buf
    st.download_button(
        label='Download Image',
        data=img_buf,
        file_name='skydiving_simulation.png',
        mime='image/png'
    )


main()
