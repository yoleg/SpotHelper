from dataclasses import dataclass, field

import streamlit as st

from ui.dropzones import Dropzone, get_dropzones
from simulation.data_classes import Coordinates


@dataclass
class Location:
    coordinates: Coordinates = field(default_factory=lambda: Coordinates(0.0, 0.0))
    dropzone: Dropzone | None = None


def input_location(default: Location = None) -> Location:
    previous = st.session_state.get('location', default or Location())

    dropzone = dropzone_select(previous.dropzone)
    if dropzone and dropzone != previous.dropzone:
        st.session_state['location_latitude'] = dropzone.Latitude
        st.session_state['location_longitude'] = dropzone.Longitude

    coordinates = coordinates_select(dropzone.location if dropzone else previous.coordinates)

    location = Location(coordinates=coordinates, dropzone=dropzone)
    st.session_state['location'] = location

    return location


def dropzone_select(value: Dropzone | None = None) -> Dropzone | None:
    dropzones: list[Dropzone] = get_dropzones()
    display_name_to_dz = {dz.display_name: dz for dz in dropzones}
    options = [""] + list(display_name_to_dz)
    assert len(set(options)) == len(options), "Dropzone display names must be unique"
    value_index = next((i for i, x in enumerate(options) if x == value.display_name), 0) if value else 0
    dropzone_name: str = st.selectbox(
        'Dropzone',
        key='dropzone_select',
        options=options,
        index=value_index,
    )
    return display_name_to_dz.get(dropzone_name, None)


def coordinates_select(value: Coordinates) -> Coordinates:
    lat = st.number_input(
        'Location Latitude',
        key='location_latitude',
        min_value=-90.0,
        max_value=90.0,
        step=0.0001,
        format="%.6f",
        value=value.lat,
    )
    lon = st.number_input(
        'Location Longitude',
        key='location_longitude',
        min_value=-180.0,
        max_value=180.0,
        step=0.0001,
        format="%.6f",
        value=value.lon,
    )
    return Coordinates(lat, lon)

