import dataclasses

import streamlit as st

from simulation.data_classes import SimulationConfig
from ui.canopies import get_canopies
from ui.input_location import input_location, Location


def form_simulation_config() -> SimulationConfig:
    default = SimulationConfig()
    previous = st.session_state.get('simulation_config', default)
    with st.expander("Location", expanded=True):
        default_location = Location(coordinates=previous.coordinates, dropzone_name=previous.dropzone_name)
        location = input_location(default_location)
    config = _form_simulation_config(default=previous)
    # TODO: this needs some redesign, as it's getting messy
    config.dropzone_display_name = location.dropzone_name
    config.coordinates = location.coordinates
    st.session_state['simulation_config'] = config
    return config


def _form_simulation_config(default: SimulationConfig) -> SimulationConfig:
    config = dataclasses.replace(default)
    with st.expander("Altitudes", expanded=True):
        config.exit_altitude_ft = st.number_input(
            'Exit Altitude (ft)',
            key='exit_altitude_ft',
            min_value=1000,
            max_value=20000,
            value=default.exit_altitude_ft,
            step=500
        )
        config.canopy_deploy_altitude_ft = st.number_input(
            'Canopy Deployment Altitude (ft)',
            key='canopy_deploy_altitude_ft',
            min_value=500,
            max_value=15000,
            value=default.canopy_deploy_altitude_ft,
            step=500
        )
    with st.expander("Canopy", expanded=True):
        canopies = get_canopies()

        def _update_canopy_speeds():
            if canopy := st.session_state.get('canopy_select', None):
                st.session_state['canopy_horizontal_speed_mph'] = float(canopy.horizontal_mph)
                st.session_state['canopy_vertical_descent_rate_mph'] = float(canopy.vertical_mph)

        def _update_canopy_name():
            horizontal_mph = st.session_state['canopy_horizontal_speed_mph']
            vertical_mph = st.session_state['canopy_vertical_descent_rate_mph']
            matching_canopy = next((
                c for c in canopies
                if c.horizontal_mph == horizontal_mph and c.vertical_mph == vertical_mph
            ), None)
            st.session_state['canopy_select'] = matching_canopy

        options = [""] + [c for c in canopies]
        st.selectbox(
            'Canopy',
            key='canopy_select',
            options=options,
            format_func=lambda x: x.display_name if x else "",
            index=next((i for i, c in enumerate(options) if c and c.display_name == default.canopy_name), 0),
            on_change=_update_canopy_speeds,
        )
        config.canopy_vertical_descent_rate_mph = st.number_input(
            'Canopy Vertical Descent Rate (mph)',
            key='canopy_vertical_descent_rate_mph',
            min_value=1.0,
            max_value=200.0,
            step=1.0,
            value=float(default.canopy_vertical_descent_rate_mph),
            on_change=_update_canopy_name,
        )
        config.canopy_horizontal_speed_mph = st.number_input(
            'Canopy Horizontal Speed (mph)',
            key='canopy_horizontal_speed_mph',
            min_value=1.0,
            max_value=200.0,
            step=1.0,
            value=float(default.canopy_horizontal_speed_mph),
            on_change=_update_canopy_name,
        )

    with st.expander("Freefall", expanded=False):
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
    with st.expander("Satellite", expanded=True):
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
            max_value=500,
            value=default.satellite_image_size,
            step=50,
            format="%d"
        )
    with st.expander("Plot", expanded=False):
        config.plot_time_step_s = st.number_input(
            'Plot Time Step (s)',
            key='plot_time_step_s',
            min_value=0.01,
            max_value=1.0,
            value=default.plot_time_step_s,
            step=0.01,
            format="%.2f"
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
