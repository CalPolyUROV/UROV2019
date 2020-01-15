"""Command Line User Interface
Provides a visual interface for the terminal for the topside unit"""

import PySimpleGUI as sg
import settings
import _thread as thread
from snr.endpoint import Endpoint
from snr.node import Node
from snr.utils import debug


class start_GUI(Endpoint):
    def __init__(self, parent: Node, name: str, input_name: str):
        if not settings.USE_GUI:
            debug("GUI", "Not enabled in settings, not initializing GUI")
            return
        super().__init__(parent, name)
        self.terminate_flag = False
        self.parent = parent
        self.input_name = input_name
        self.datastore = self.parent.datastore
        self.name = name
        self.loop()

    def gui_print(self):
        layout = [[sg.Text('Telemetry Data', size=(40, 2), justification='center')],
                  [sg.Text('Stick Left X    Stick Right X    Left Trigger', size=(40, 2), justification='center')],
                  [sg.Text('', size=(40, 2), font=('Helvetica', 10), justification='center', key='_0-2_')],
                  [sg.Text('Stick Left Y    Stick Right Y    Right Trigger', size=(40, 2), justification='center')],
                  [sg.Text('', size=(40, 2), font=('Helvetica', 10), justification='center', key='_3-5_')],
                  [sg.Text("_" * 45)],
                  [sg.Text('Refresh Rate', size=(40, 2), justification='center')],
                  [sg.Text(' ' * 8), sg.Slider(range=(0, 50), default_value=47, size=(20, 20), orientation='horizontal',
                                               font=("Helvetica", 15)), sg.Text(' ' * 2)],
                  [sg.T(' ' * 32), sg.Quit()]]

        window = sg.Window('Top Side', layout)

        refresh_rate = 10
        telem = self.get_data()

        while not self.terminate_flag:  # Event Loop
            event, values = window.Read(
                timeout=refresh_rate)  # Please try and use as high of a timeout value as you can
            if event is None or event == 'Quit':  # if user closed the window using X or clicked Quit button
                self.terminate()
            if telem is not None and telem.get("stick_left_x") is not None:
                window.Element('_0-2_').Update(
                    '{}            {}            {}'.format((telem.get("stick_left_x") // 1), (telem.get("stick_right_x") // 1),
                                                  (telem.get("trigger_left") // 1)))
                window.Element('_3-5_').Update(
                    '{}            {}            {}'.format((telem["stick_left_y"] // 1), (telem["stick_right_y"] // 1),
                                                  (telem["trigger_right"] // 1)))
            refresh_rate = ((values[0] - 50) ** 2 + 1)
            telem = self.get_data()
            # print("My bs: ", telem)
            # print(refresh_rate)

    def loop(self):
        debug("framework", "Starting async endpoint {} thread", [self.name])
        thread.start_new_thread(self.gui_print(), ())

    def get_name(self):
        return self.name

    def set_terminate_flag(self):
        self.terminate_flag = True
        debug("framework", "Terminating endpoint {}", [self.name])

    def terminate(self):
        debug("clui", "Terminating CLUI")
        self.set_terminate_flag()

    def get_data(self):
        return self.parent.get_data(self.input_name)
