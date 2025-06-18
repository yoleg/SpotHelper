import logging
import streamlit as st

from SpotHelper import make_image
from simulation_config import SimulationConfig


def main():
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
    logging.getLogger('tornado.access').setLevel(logging.WARNING)

    st.sidebar.header('Configuration')
    config = config_form()

    st.header('Simulation Output')
    try:
        plt = make_image(config)
        st.pyplot(plt, use_container_width=True)
    except Exception as e:
        st.error(f"Error during simulation: {e}")
        logging.error("Simulation failed", exc_info=True)


def config_form():
    config = SimulationConfig()
    config.exit_altitude_ft = st.sidebar.number_input(
        'Exit Altitude (ft)', min_value=1000, max_value=20000, value=config.exit_altitude_ft
    )
    config.deploy_altitude_ft = st.sidebar.number_input(
        'Canopy Deployment Altitude (ft)', min_value=500, max_value=15000, value=config.deploy_altitude_ft
    )
    config.mass_kg = st.sidebar.number_input(
        'Skydiver Mass (kg)', min_value=50, max_value=150, value=config.mass_kg
    )
    config.CdA = st.sidebar.number_input(
        'Drag Area (m^2)', min_value=0.1, max_value=1.0, value=config.CdA
    )
    config.canopy_v_vert_fps = st.sidebar.number_input(
        'Canopy Vertical Descent Rate (ft/s)', min_value=1, max_value=20, value=config.canopy_v_vert_fps
    )
    config.canopy_v_horiz_fps = st.sidebar.number_input(
        'Canopy Horizontal Speed (ft/s)', min_value=1, max_value=50, value=config.canopy_v_horiz_fps
    )
    config.dt = st.sidebar.number_input(
        'Time Step (s)', min_value=0.01, max_value=1.0, value=config.dt
    )
    config.sat_img_zoom = st.sidebar.slider(
        'Satellite Image Zoom Level', min_value=10, max_value=20, value=config.sat_img_zoom
    )
    config.sat_img_size = st.sidebar.slider(
        'Satellite Image Size (pixels)', min_value=200, max_value=1000, value=config.sat_img_size
    )
    config.circle_resolution = st.sidebar.slider(
        'Glide Circle Resolution', min_value=50, max_value=500, value=config.circle_resolution
    )
    return config


if __name__ == "__main__":
    main()