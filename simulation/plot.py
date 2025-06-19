import logging
from threading import RLock

import numpy as np
from matplotlib import pyplot as plt

from simulation.data_classes import MapImage, SimulationResults

LOGGER = logging.getLogger(__name__)

PLOT_LOCK = RLock()


def make_plot(params: SimulationResults, map_image: MapImage = None):
    if not isinstance(params, SimulationResults):
        raise TypeError("params must be an instance of PlotDisplayParameters")
    if map_image is not None and not isinstance(map_image, MapImage):
        raise TypeError("map_image must be an instance of MapImage or None")
    with PLOT_LOCK:
        return _make_plot(params, map_image)


def _make_plot(params: SimulationResults, map_image: MapImage = None):
    fig, ax = plt.subplots(figsize=(8, 8))
    if map_image is None:
        ax.set_title('Skydiver Trajectory (No Satellite Image, Phase Colored)')
    else:
        ax.imshow(
            map_image.image,
            extent=(map_image.bounding_box[2], map_image.bounding_box[3], map_image.bounding_box[0], map_image.bounding_box[1]),
            aspect='auto',
            origin='upper',
            zorder=0
        )
        ax.set_xlim(map_image.bounding_box[2], map_image.bounding_box[3])
        ax.set_ylim(map_image.bounding_box[0], map_image.bounding_box[1])
        ax.set_title('Skydiver Trajectory over Yandex Satellite Image (Phase Colored)')
    freefall_mask = np.array(params.phases) == 0
    canopy_mask = np.array(params.phases) == 1
    ax.plot(
        np.array(params.trajectory_longitudes)[freefall_mask],
        np.array(params.trajectory_latitudes)[freefall_mask],
        color='red',
        linewidth=2,
        label='Freefall'
    )
    ax.plot(
        np.array(params.trajectory_longitudes)[canopy_mask],
        np.array(params.trajectory_latitudes)[canopy_mask],
        color='blue',
        linewidth=2,
        label='Canopy'
    )
    ax.plot(params.circle_longitudes, params.circle_latitudes, color='green', linestyle='--', label='Canopy Glide Circle')
    ax.scatter([params.exit.lon], [params.exit.lat], color='cyan', marker='o', label='Exit Point')
    ax.scatter([params.ip.lon], [params.ip.lat], color='yellow', marker='x', label='Dropzone')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend()
    return fig
