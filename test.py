import numpy as np
from pathlib import Path
import sys
import os
from skimage import io
import matplotlib.pyplot as plt

import napari



def run_multi_d_acq_tpzcxy(self):

    @thread_worker(connect={"yielded": self.update_viewer})
    def run(self):

        dev_loaded = list(mmcore.getLoadedDevices())
        if len(dev_loaded) > 1:
            
            if self.channel_groupBox.isChecked() and self.channel_tableWidget.rowCount()>0:#can be removed
                
                self.list_ch.clear()
                for c in range(self.channel_tableWidget.rowCount()):
                    cnl = self.channel_tableWidget.cellWidget(c, 0).currentText()
                    self.list_ch.append(cnl)

                #timelapse settings
                if self.time_groupBox.isChecked():
                    timepoints = self.timepoints_spinBox.value()
                    timeinterval = self.interval_spinBox.value()
                    unit = self.time_comboBox.currentText() #min, sec, ms
                    if unit == 'min':
                        timeinterval_unit = timeinterval*60000
                    if unit == 'sec':
                        timeinterval_unit = timeinterval*1000
                    if unit == 'ms':
                        timeinterval_unit = timeinterval
                else:
                    timepoints = 1
                    timeinterval_unit = 0

                #position settings
                self.pos_list.clear()
                print(f'pos_list: {self.pos_list}')
                if self.stage_pos_groupBox.isChecked() and self.stage_tableWidget.rowCount()>0:
                    for row in range(self.stage_tableWidget.rowCount()):
                        x_pos = self.stage_tableWidget.item(row, 0).text()
                        y_pos = self.stage_tableWidget.item(row, 1).text()
                        z_pos = self.stage_tableWidget.item(row, 2).text()
                        self.pos_list.append((x_pos,y_pos,z_pos))
                    print(f'pos_list: {self.pos_list}')
                else:
                    xp = mmcore.getXPosition()
                    yp = mmcore.getYPosition()
                    zp = mmcore.getPosition("Z_Stage")
                    self.pos_list.append((xp,yp,zp))
                    print(f'pos_list: {self.pos_list}')
                
                #z-stack settings
                if self.stack_groupBox.isChecked():
                    n_steps = self.step_spinBox.value()
                    stepsize = self.step_size_doubleSpinBox.value()
                else:
                    n_steps = 1
                    stepsize = 0

                #create timepont stack array
                self.pos_stack_list.clear()
                self.acq_stack_list.clear()
                nC = self.channel_tableWidget.rowCount()
                
                for _ in range(len(self.pos_list)):
                    print("self.create_stack_array(timepoints, n_steps, nC) ", timepoints, n_steps, nC)
                    pos_stack = self.create_stack_array(timepoints, n_steps, nC) 
                    # pos_stack = self.create_stack_array(1, n_steps, nC)
                    print("appending a stack with shape", pos_stack.shape)
                    self.pos_stack_list.append(pos_stack)

                # print("adding to viewer empty stack with shape", pos_stack.shape)
                # layer = pos_stack
                # self.viewer.add_image(layer, name="MDA")

                #create main save folder in directory
                if self.save_groupBox.isChecked():
                    pl = format(len(self.pos_list), '04d')
                    tl = format(timepoints, '04d')
                    ns = format(n_steps, '04d')

                    save_folder_name = f'{self.fname_lineEdit.text()}_ps{pl}_ts{tl}_zs{ns}_{self.list_ch}'
                    save_folder = self.parent_path / save_folder_name
                    if save_folder.exists():
                        i = len(os.listdir(self.parent_path))
                        save_folder = Path(f'{save_folder_name}_{i-1}')
                        save_folder = self.parent_path / save_folder
                    os.makedirs(save_folder)
                    
                    for posxy in range(len(self.pos_list)):
                        i = format(posxy, '04d')
                        os.makedirs(save_folder/f'Pos_{i}')

                #start acquisition

                # header = self._mda_summary_string()
                # print(header)
                
                start_acq_timr = time.perf_counter()
                for t in range(timepoints):
                    print(f"\nt_point: {t}\n")

                    for position, (x, y, z) in enumerate(self.pos_list):
                        print(f"    XY_Pos_n: {position} XY_pos: {x, y} z_start: ({z})\n")
                        mmcore.setXYPosition(float(x), float(y))
                        mmcore.setPosition("Z_Stage",float(z))
            
                        Bottom_z = mmcore.getPosition("Z_Stage") - ((n_steps / 2) * stepsize)

                        for z_position in range(n_steps):
                            print(f"        Z_Pos_n: {z_position} Z: {Bottom_z}\n")
                            mmcore.setPosition("Z_Stage", Bottom_z)
                            
                            for c in range(self.channel_tableWidget.rowCount()):
                                ch = self.channel_tableWidget.cellWidget(c, 0).currentText()
                                exp = self.channel_tableWidget.cellWidget(c, 1).value()

                                print(f'            Channel: {ch}, exp time: {exp}')

                                start_snap = time.perf_counter()

                                mmcore.setExposure(exp)
                                mmcore.setConfig("Channel", ch)
                                # mmcore.waitForDevice('')

                                mmcore.snapImage()

                                stack = self.pos_stack_list[position]
                                stack[t,z_position,c,:,:] = mmcore.getImage()

                                layer_name = f'Position_{position}'

                                yield stack, layer_name

                                # self.update_viewer_mda(stack, layer_name)                                                     

                                end_snap = time.perf_counter()
                                print(f'            channel snap took: {round(end_snap-start_snap, 4)} seconds')

                            Bottom_z = Bottom_z + stepsize 

                        self.acq_stack_list.append(stack)# each is shape (1,nPositions,nChannels,x,y)


                        #save stack per position (n of file = n of timepoints)
                        #maybe use it to save temp files and remove them in the end
                        if self.save_groupBox.isChecked():
                            print('\n_______SAVING_______')
                            # position_format = format(position, '04d')
                            position_format = format(len(self.pos_list), '04d')
                            t_format = format(timepoints, '04d')
                            z_position_format = format(z_position, '04d')
                            save_folder_name = f'{self.fname_lineEdit.text()}_p{position_format}_t{t_format}_zs{z_position_format}_{self.list_ch}_TEMP'
                            pth = save_folder / f'Pos_{position_format}'/f'{save_folder_name}.tif'
                            io.imsave(str(pth), stack, imagej=True, check_contrast=False)

                    if timeinterval_unit > 0 and t < timepoints - 1:
                        print(f"\nIt was t_point: {t}")
                        print(f"Waiting...Time interval = {timeinterval_unit/1000} seconds\n")
                        #create a time indicator on the gui
                        # maybe use
                        # while True:
                        #   display the time changing
                        mmcore.sleep(timeinterval_unit)
                    # else:
                    #     mmcore.sleep(0.01)

                end_acq_timr = time.perf_counter()

                summary = """
                _________________________________________
                Acq_time: {} Seconds
                _________________________________________
                """.format(round(end_acq_timr-start_acq_timr, 4))
                summary = dedent(summary)
                print(summary)

            else:
                print('Select at lest one channel.')
        else:
            print('Load a cfg file first.')