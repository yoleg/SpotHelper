import dataclasses
import io

import streamlit as st

from simulation.data_classes import SimulationConfig
from simulation.fetch import get_satellite_image, get_winds_aloft_table
from simulation.simulation import run_simulation
from simulation.plot import make_plot
from ui.common import common_page_config
from ui.inputs import input_location

common_page_config("Spot Helper Demo")


def main():
    with st.sidebar:
        config = form_simulation_config()

    winds = get_winds_aloft_table(config.location)
    simulation_results = run_simulation(config)
    satellite_image = get_satellite_image(config.location, zoom=config.sat_img_zoom, size=config.sat_img_size)
    if not satellite_image:
        st.warning("Satellite image could not be retrieved. Plotting trajectory only.")
    fig = make_plot(simulation_results, map_image=satellite_image)

    image_download_button(fig)

    st.pyplot(fig, use_container_width=True)

    st.markdown(f"*Landing at: {simulation_results.final_latlon}*")

    st.header('Winds Aloft')
    st.dataframe(winds)


def image_download_button(fig):
    img_buf = pyplot_to_image_buffer(fig)
    st.download_button(
        label='Download Image',
        data=img_buf,
        file_name='skydiving_simulation.png',
        mime='image/png'
    )


def pyplot_to_image_buffer(plt) -> io.BytesIO:
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    return img_buf


def form_simulation_config() -> SimulationConfig:
    default_config = SimulationConfig()
    st.header('Configuration')
    if st.toggle("Auto Update", value=True):
        return input_simulation_config(default_config)
    with st.form("config_form", clear_on_submit=False, enter_to_submit=True, border=False):
        submitted = st.form_submit_button("Update")
        config_value = input_simulation_config(default_config)
        return config_value if submitted else default_config


def input_simulation_config(default: SimulationConfig) -> SimulationConfig:
    config = dataclasses.replace(default)
    with st.expander("Location", expanded=True):
        config.location = input_location(default=default.location)
    with st.expander("Freefall", expanded=True):
        config.exit_altitude_ft = st.number_input(
            'Exit Altitude (ft)', min_value=1000, max_value=20000, value=default.exit_altitude_ft, step=500
        )
        config.mass_lb = st.number_input(
            'Skydiver Mass (lb)', min_value=10, max_value=1000, value=int(default.mass_lb), step=5,
        )
        config.CdA = st.number_input(
            'Drag Area (m^2)', min_value=0.1, max_value=1.0, value=default.CdA, step=0.01, format="%.2f"
        )
    with st.expander("Canopy", expanded=True):
        config.deploy_altitude_ft = st.number_input(
            'Canopy Deployment Altitude (ft)',
            min_value=500,
            max_value=15000,
            value=default.deploy_altitude_ft,
            step=500
        )
        config.canopy_v_vert_fps = st.number_input(
            'Canopy Vertical Descent Rate (ft/s)', min_value=1, max_value=20, value=default.canopy_v_vert_fps,
        )
        config.canopy_v_horiz_fps = st.number_input(
            'Canopy Horizontal Speed (ft/s)', min_value=1, max_value=50, value=default.canopy_v_horiz_fps, step=1,
        )
    with st.expander("Display", expanded=True):
        config.dt = st.number_input(
            'Time Step (s)', min_value=0.01, max_value=1.0, value=default.dt, step=0.01, format="%.2f"
        )
        config.sat_img_zoom = st.slider(
            'Satellite Image Zoom Level', min_value=10, max_value=20, value=default.sat_img_zoom, step=1, format="%d"
        )
        config.sat_img_size = st.slider(
            'Satellite Image Size (pixels)',
            min_value=200,
            max_value=1000,
            value=default.sat_img_size,
            step=50,
            format="%d"
        )
        config.circle_resolution = st.slider(
            'Glide Circle Resolution',
            min_value=50,
            max_value=500,
            value=default.circle_resolution,
            step=10,
            format="%d"
        )
    return config


main()
