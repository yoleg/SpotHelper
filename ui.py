import dataclasses
import io
import logging

import streamlit as st

from Functions import get_winds_aloft_table
from SpotHelper import run_simulation
from plot import get_satellite_image, make_plot
from data_classes import LatLon, SimulationConfig

st.set_page_config(
    page_title="Spot Helper",
    page_icon="🪂",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    logging.getLogger('tornado.access').setLevel(logging.WARNING)

    st.sidebar.header('Configuration')

    default_config = SimulationConfig()
    with st.sidebar:
        if st.toggle("Auto Update", value=True):
            config = config_form(default_config)
        else:
            with st.form("config_form", clear_on_submit=False, enter_to_submit=True, border=False):
                submitted = st.form_submit_button("Update")
                config_value = config_form(default_config)
                config = config_value if submitted else default_config

    winds = get_winds_aloft_table(config.location)

    # Save the figure to a BytesIO object
    results = run_simulation(config)
    satellite_image = get_satellite_image(config.location, zoom=config.sat_img_zoom, size=config.sat_img_size)
    if not satellite_image:
        st.warning("Satellite image could not be retrieved. Plotting trajectory only.")

    fig = make_plot(results, map_image=satellite_image)

    img_buf = pyplot_to_image(fig)

    # Download button for the image
    st.download_button(
        label='Download Image',
        data=img_buf,
        file_name='skydiving_simulation.png',
        mime='image/png'
    )
    st.header('Simulation Output')
    st.pyplot(fig, use_container_width=True)

    st.text(f"Landing at: {results.final_latlon}")

    st.header('Winds Aloft')
    st.dataframe(winds)


def pyplot_to_image(plt) -> io.BytesIO:
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    return img_buf


def config_form(default: SimulationConfig) -> SimulationConfig:
    config = dataclasses.replace(default)

    with st.expander("Location", expanded=True):
        lat = st.number_input(
            'Dropzone Latitude', min_value=-90.0, max_value=90.0, value=config.location.lat, step=0.0001, format="%.6f"
        )
        lon = st.number_input(
            'Dropzone Longitude',
            min_value=-180.0,
            max_value=180.0,
            value=config.location.lon,
            step=0.0001,
            format="%.6f"
        )
        config.location = LatLon(lat, lon)
    with st.expander("Freefall", expanded=True):
        config.exit_altitude_ft = st.number_input(
            'Exit Altitude (ft)', min_value=1000, max_value=20000, value=config.exit_altitude_ft, step=500
        )
        config.mass_lb = st.number_input(
            'Skydiver Mass (lb)', min_value=10, max_value=1000, value=int(config.mass_lb), step=5,
        )
        config.CdA = st.number_input(
            'Drag Area (m^2)', min_value=0.1, max_value=1.0, value=config.CdA, step=0.01, format="%.2f"
        )
    with st.expander("Canopy", expanded=True):
        config.deploy_altitude_ft = st.number_input(
            'Canopy Deployment Altitude (ft)', min_value=500, max_value=15000, value=config.deploy_altitude_ft, step=500
        )
        config.canopy_v_vert_fps = st.number_input(
            'Canopy Vertical Descent Rate (ft/s)', min_value=1, max_value=20, value=config.canopy_v_vert_fps,
        )
        config.canopy_v_horiz_fps = st.number_input(
            'Canopy Horizontal Speed (ft/s)', min_value=1, max_value=50, value=config.canopy_v_horiz_fps, step=1,
        )
    with st.expander("Display", expanded=True):
        config.dt = st.number_input(
            'Time Step (s)', min_value=0.01, max_value=1.0, value=config.dt, step=0.01, format="%.2f"
        )
        config.sat_img_zoom = st.slider(
            'Satellite Image Zoom Level', min_value=10, max_value=20, value=config.sat_img_zoom, step=1, format="%d"
        )
        config.sat_img_size = st.slider(
            'Satellite Image Size (pixels)',
            min_value=200,
            max_value=1000,
            value=config.sat_img_size,
            step=50,
            format="%d"
        )
        config.circle_resolution = st.slider(
            'Glide Circle Resolution', min_value=50, max_value=500, value=config.circle_resolution, step=10, format="%d"
        )
    return config


if __name__ == "__main__":
    main()
