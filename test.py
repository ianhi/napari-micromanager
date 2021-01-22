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





#update viewer
def update_viewer_mda(self, result):
   stack, layer_name = result
   try:
     self.viewer.layers[layer_name].data = stack
   except KeyError:
     self.viewer.add_image(stack, name=layer_name)

...

#multi-D acquisition
def capture_multid(self):
    #here there are:
        #channel settings
        #timelapse settings
        #position settings
        #z-stack settings
        #saving settings
        #create array to save the data
    @thread_worker(connect={'yielded': self.update_viewer_mda})
    def run_multi_d_acq_tpzcyx():
        for t in range(timepoints):

            xy_position

                z_position

                    for c in range(self.channel_tableWidget.rowCount()):
                        ch = self.channel_tableWidget.cellWidget(c, 0).currentText()
                        exp = self.channel_tableWidget.cellWidget(c, 1).value()

                        mmcore.setExposure(exp)
                        mmcore.setConfig("Channel", ch)

                        mmcore.snapImage()

                        stack = self.pos_stack_list[position]
                        image = mmcore.getImage()
                        stack[t,z_position,c,:,:] = image

                        yield (stack, layer_name)

                    Bottom_z = Bottom_z + stepsize

            if self.save_groupBox.isChecked():
                for i in range(len(self.pos_stack_list)):

                    file_to_save = self.pos_stack_list[i]

                    position_format = format(i, '04d')
                    t_format = format(timepoints, '04d')
                    n_steps_format = format(n_steps, '04d')

                    save_folder_name = f'{self.fname_lineEdit.text()}_p{position_format}_{t_format}t_{n_steps_format}z_{self.list_ch}_TEMP'
                    pth = save_folder / f'Pos_{position_format}'/f'{save_folder_name}.tif'
                    io.imsave(str(pth), file_to_save, imagej=True, check_contrast=False)


            if timeinterval_unit > 0 and t < timepoints - 1:
                mmcore.sleep(timeinterval_unit)

        summary = """
        _________________________________________
        Acq_time: {} Seconds
        _________________________________________
        """.format(round(end_acq_timr-start_acq_timr, 4))
        summary = dedent(summary)
        print(summary)

    run_multi_d_acq_tpzcyx()


    




