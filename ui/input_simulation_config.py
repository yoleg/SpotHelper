import dataclasses

import streamlit as st

from simulation.data_classes import SimulationConfig
from ui.input_location import input_location, Location


def form_simulation_config() -> SimulationConfig:
    default = SimulationConfig()
    previous = st.session_state.get('simulation_config', default)
    with st.expander("Location", expanded=True):
        location = input_location(default=Location(coordinates=previous.location))
    config = _form_simulation_config(default=previous)
    config.location = location.coordinates
    st.session_state['simulation_config'] = config
    return config


def _form_simulation_config(default: SimulationConfig) -> SimulationConfig:
    config = dataclasses.replace(default)
    with st.expander("Freefall", expanded=True):
        config.exit_altitude_ft = st.number_input(
            'Exit Altitude (ft)',
            key='exit_altitude_ft',
            min_value=1000,
            max_value=20000,
            value=default.exit_altitude_ft,
            step=500
        )
        config.mass_lb = st.number_input(
            'Skydiver Mass (lb)',
            key='mass_lb',
            min_value=10,
            max_value=1000,
            value=int(default.mass_lb),
            step=5,
        )
        config.freefall_drag_area_m2 = st.number_input(
            'Freefall Drag Area (m^2)',
            key='freefall_drag_area_m2',
            min_value=0.1,
            max_value=1.0,
            value=default.freefall_drag_area_m2,
            step=0.01,
            format="%.2f"
        )
    with st.expander("Canopy", expanded=True):
        config.canopy_deploy_altitude_ft = st.number_input(
            'Canopy Deployment Altitude (ft)',
            key='canopy_deploy_altitude_ft',
            min_value=500,
            max_value=15000,
            value=default.canopy_deploy_altitude_ft,
            step=500
        )
        config.canopy_vertical_descent_rate_fps = st.number_input(
            'Canopy Vertical Descent Rate (ft/s)',
            key='canopy_vertical_descent_rate_fps',
            min_value=1,
            max_value=20,
            value=default.canopy_vertical_descent_rate_fps,
        )
        config.canopy_horizontal_speed_fps = st.number_input(
            'Canopy Horizontal Speed (ft/s)',
            key='canopy_horizontal_speed_fps',
            min_value=1,
            max_value=50,
            value=default.canopy_horizontal_speed_fps,
            step=1,
        )
    with st.expander("Plot", expanded=True):
        config.plot_time_step_s = st.number_input(
            'Plot Time Step (s)',
            key='plot_time_step_s',
            min_value=0.01,
            max_value=1.0,
            value=default.plot_time_step_s,
            step=0.01,
            format="%.2f"
        )
        config.satellite_image_zoom = st.slider(
            'Satellite Image Zoom Level',
            key='satellite_image_zoom',
            min_value=10,
            max_value=20,
            value=default.satellite_image_zoom,
            step=1,
            format="%d"
        )
        config.satellite_image_size = st.slider(
            'Satellite Image Size (pixels)',
            key='satellite_image_size',
            min_value=200,
            max_value=1000,
            value=default.satellite_image_size,
            step=50,
            format="%d"
        )
        config.plot_circle_resolution = st.slider(
            'Plot Circle Resolution',
            key='plot_circle_resolution',
            min_value=50,
            max_value=500,
            value=default.plot_circle_resolution,
            step=10,
            format="%d"
        )
    return config
