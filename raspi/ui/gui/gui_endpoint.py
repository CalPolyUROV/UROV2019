"""Simple GUI
Provides a visual interface for the topside unit"""

from typing import List

import settings
from snr.async_endpoint import AsyncEndpoint
from snr.node import Node
from snr.utils import debug
from snr.task import SomeTasks, Task


class SimpleGUI(AsyncEndpoint):
    def __init__(self, parent: Node, name: str,
                 input_name: str):
        self.refresh_rate = 10
        super().__init__(parent, name,
                         self.init_gui, self.update_gui,
                         self.refresh_rate)
        self.input_name = input_name
        self.datastore = self.parent.datastore

        self.start_loop()

    def get_new_tasks(self) -> SomeTasks:
        pass

    def task_handler(self, t: Task) -> SomeTasks:
        pass

    def terminate(self):
        debug("gui_event", "GUI endpoint terminating")
        self.set_terminate_flag()

    def __repr__(self) -> str:
        return self.name

    def get_data(self):
        return self.datastore.get(self.input_name)

    def init_gui(self):
        import PySimpleGUI as sg

        # TODO: Move GUI layout code out of init method for configuration,
        # maybe another file?
        self.layout = self.get_layout(sg)

        self.window = sg.Window('Top Side', self.layout)

        self.update_gui()

    def update_gui(self):
        # Get updated telemetry data
        # TODO: Use page freshness abstraction to check if data is unchanged
        telem = self.get_data()
        debug("gui_telem_verbose", "Got telemetry info: {}", [telem])

        # Please try and use as high of a timeout value as you can
        event, values = self.window.Read(timeout=self.refresh_rate)
        # if user closed the window using X or clicked Quit button
        if event is None or event == 'Quit':
            self.terminate()
        if telem is not None and telem.get("stick_left_x") is not None:
            self.window.Element('left').Update(
                'Stick Left X: \n{}\nStick Left Y: \n{}\nLeft Trigger: \n{}\n'.format((telem.get("stick_left_x") // 1),
                                                                                      (telem.get("stick_left_y") // 1),
                                                                                      (telem.get("trigger_left") // 1)))
            self.window.Element('right').Update(
                'Stick Right X: \n{}\nStick Right Y: \n{}\nRight Trigger: \n{}\n'.format(
                    (telem.get("stick_right_x") // 1),
                    (telem.get("stick_right_y") // 1),
                    (telem.get("trigger_right") // 1)))
        # Update refresh rate from GUI
        debug("gui_verbose", "UI tick_rate value: {}", [values[0]])
        self.set_refresh_rate(values[0])

    def set_refresh_rate(self, rate):
        debug("gui_verbose",
              "Updating async_endpoint tick_rate_hz to {}",
              [rate])
        super().set_delay(rate)

    def get_layout(self, sg) -> List:
        layout = [[sg.Frame(layout=[[sg.Text('Stick Left X: \n0\nStick Left Y: \n0\nLeft Trigger: \n0\n', size=(20, 6),
                           justification='center', key='left'),
                   sg.Text('Stick Right X: \n0\nStick Right Y: \n0\nRight Trigger: \n0\n', size=(20, 6),
                           justification='center', key='right')]], title='Telem Data', title_color='Black', relief=sg.RELIEF_SUNKEN)],
                  [sg.Text('Refresh Rate', size=(45, 2), justification='center')],
                  [sg.Text(' ' * 13), sg.Slider(range=(0, 50), default_value=47, size=(20, 20), orientation='horizontal',
                                               font=("Helvetica", 15)), sg.Text(' ' * 2)],
                  [sg.T(' ' * 38), sg.Quit()]]
        return layout
