import io
import logging
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from Functions import get_winds_aloft_table
from SpotHelper import run_simulation
from data_classes import SimulationConfig


def main():
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    logging.getLogger('tornado.access').setLevel(logging.WARNING)

    st.sidebar.header('Configuration')
    config = config_form()

    winds = get_winds_aloft_cached(config.ip_lat, config.ip_long)

    # Save the figure to a BytesIO object
    plt = run_simulation(config)
    img_buf = pyplot_to_image(plt)

    # Download button for the image
    st.download_button(
        label='Download Image',
        data=img_buf,
        file_name='skydiving_simulation.png',
        mime='image/png'
    )
    st.header('Simulation Output')
    st.pyplot(plt, use_container_width=True)

    st.header('Winds Aloft')
    st.dataframe(winds)


def pyplot_to_image(plt) -> io.BytesIO:
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    return img_buf


@st.cache_data
def get_winds_aloft_cached(ip_lat: float, ip_long: float):
    return get_winds_aloft_table(ip_lat, ip_long)


def config_form(location: DeltaGenerator = st.sidebar) -> SimulationConfig:
    config = SimulationConfig()
    config.ip_lat = location.number_input(
        'Dropzone Latitude', min_value=-90.0, max_value=90.0, value=config.ip_lat
    )
    config.ip_long = location.number_input(
        'Dropzone Longitude', min_value=-180.0, max_value=180.0, value=config.ip_long
    )
    config.exit_altitude_ft = location.number_input(
        'Exit Altitude (ft)', min_value=1000, max_value=20000, value=config.exit_altitude_ft
    )
    config.deploy_altitude_ft = location.number_input(
        'Canopy Deployment Altitude (ft)', min_value=500, max_value=15000, value=config.deploy_altitude_ft
    )
    config.mass_kg = location.number_input(
        'Skydiver Mass (kg)', min_value=50, max_value=150, value=config.mass_kg
    )
    config.CdA = location.number_input(
        'Drag Area (m^2)', min_value=0.1, max_value=1.0, value=config.CdA
    )
    config.canopy_v_vert_fps = location.number_input(
        'Canopy Vertical Descent Rate (ft/s)', min_value=1, max_value=20, value=config.canopy_v_vert_fps
    )
    config.canopy_v_horiz_fps = location.number_input(
        'Canopy Horizontal Speed (ft/s)', min_value=1, max_value=50, value=config.canopy_v_horiz_fps
    )
    config.dt = location.number_input(
        'Time Step (s)', min_value=0.01, max_value=1.0, value=config.dt
    )
    config.sat_img_zoom = location.slider(
        'Satellite Image Zoom Level', min_value=10, max_value=20, value=config.sat_img_zoom
    )
    config.sat_img_size = location.slider(
        'Satellite Image Size (pixels)', min_value=200, max_value=1000, value=config.sat_img_size
    )
    config.circle_resolution = location.slider(
        'Glide Circle Resolution', min_value=50, max_value=500, value=config.circle_resolution
    )
    return config


if __name__ == "__main__":
    main()