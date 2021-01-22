import numpy as np
from pathlib import Path
import sys
import os
from skimage import io
import matplotlib.pyplot as plt

import napari


from itertools import product


# t = 5
# c = 3
# p = 2
# for index in product(range(nt), range(nc), range(np)):
#     print(f'nt = {index[0]}, cn = {index[1]}, np = {index[2]}')


import napari
import numpy as np
from napari.qt.threading import thread_worker


with napari.gui_qt():
    viewer = napari.Viewer()

    

    def update_layer(new_image):
        try:
            # if the layer exists, update the data
            viewer.layers['result'].data = new_image
        except KeyError:
            # otherwise add it to the viewer
            viewer.add_image(
                new_image, contrast_limits=(0.45, 0.55), name='result'
            )

    @thread_worker(connect={'yielded': update_layer})
    def large_random_images():
        cumsum = np.zeros((512, 512))
        for i in range(1024):
            cumsum += np.random.rand(512, 512)
            if i % 16 == 0:
                yield cumsum / (i + 1)

    large_random_images()  # call the function!