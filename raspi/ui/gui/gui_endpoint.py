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
                 input_name: list):
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
        data = []
        for input in self.input_name:
            data += [self.datastore.get(input)]
        return data

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
        data = self.get_data()
        # Please try and use as high of a timeout value as you can
        event, values = self.window.Read(timeout=self.refresh_rate)
        # if user closed the window using X or clicked Quit button
        if event is None or event == 'Quit':
            self.terminate()
        if settings.GUI_channels["controller"]:
            debug("gui_control", "Got controler info: {}", [data[0]])
            if data[0] is not None and data[0].get("stick_left_x") is not None:
                self.window.Element('left').Update(
                    'Stick Left X: \n{}\nStick Left Y: \n{}\nLeft Trigger: \n{}\n'.format(
                        (data[0].get("stick_left_x") // 1),
                        (data[0].get("stick_left_y") // 1),
                        (data[0].get("trigger_left") // 1)))
                self.window.Element('right').Update(
                    'Stick Right X: \n{}\nStick Right Y: \n{}\nRight Trigger: \n{}\n'.format(
                        (data[0].get("stick_right_x") // 1),
                        (data[0].get("stick_right_y") // 1),
                        (data[0].get("trigger_right") // 1)))
        if settings.GUI_channels["telem"]:
            debug("gui_telem", "Got telem info: {}", [data[1]])
        # Update refresh rate from GUI
        debug("gui_verbose", "UI tick_rate value: {}", [values[0]])
        self.set_refresh_rate(values[0])

    def set_refresh_rate(self, rate):
        debug("gui_verbose",
              "Updating async_endpoint tick_rate_hz to {}",
              [rate])
        if rate == 0.0:
            super().set_delay(1/5)
        else:
            super().set_delay(rate)

    def get_layout(self, sg) -> List:
        layout = []
        if settings.GUI_channels["controller"]:
            layout += [[sg.Frame(layout=[[sg.Text('Stick Left X: \n0\nStick Left Y: \n0\nLeft Trigger: \n0\n', size=(20, 6),
                               justification='center', key='left'),
                       sg.Text('Stick Right X: \n0\nStick Right Y: \n0\nRight Trigger: \n0\n', size=(20, 6),
                               justification='center', key='right')]], title='Control Data', title_color='Black', relief=sg.RELIEF_SUNKEN)]]
        if settings.GUI_channels["telem"]:
            layout += [
                # [sg.Frame(layout=[[sg.Text('Stick Left X: \n0\nStick Left Y: \n0\nLeft Trigger: \n0\n', size=(20, 6),
                #                            justification='center', key='left'),
                #                    sg.Text('Stick Right X: \n0\nStick Right Y: \n0\nRight Trigger: \n0\n', size=(20, 6),
                #                            justification='center', key='right')]], title='Control Data',
                #           title_color='Black', relief=sg.RELIEF_SUNKEN)],
                # [sg.Text('Refresh Rate', size=(45, 2), justification='center')]
            ]
        layout += [[sg.Text(' ' * 13), sg.Slider(range=(0, 50), default_value=47, size=(20, 20), orientation='horizontal', font=("Helvetica", 15)), sg.Text(' ' * 2)],
                    [sg.T(' ' * 38), sg.Quit()]]
        return layout
