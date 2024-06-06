"""
This module defines the ConnectDrawer class, which handles drawing
connections as polylines using OpenGL in a wxPython application.
"""

from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINE_STRIP
from logic_draw import LogicDrawer
import numpy.random as rd
import numpy as np


class ConnectDrawer:
    """Handle all connections drawings."""

    def __init__(self, domain_dict, draw_dict, padding, coords_array, devices) -> None:
        """
        Initialize the ConnectDrawer.

        Parameters:
        domain_dict (dict): Stores dict of all min_max coords {LogicDraw obj: (bounding box tuple)} for all operators.
        draw_dict (dict): Dictionary of draw objects.
        padding (float): Padding when connection line tries to navigate around another bounding box.
        coords_array (list): List to store coordinates of connections.
        devices (Devices): Devices object containing the list of devices.
        """
        self.domain_dict = domain_dict
        self.padding = padding
        self.fraction = 0.5  # This is a randomized fraction for each device
        self.coords_array = coords_array
        self.devices = devices
        self.draw_dict = draw_dict

    def make_all_connections(self) -> None:
        """Create all connections."""
        for device in self.devices.devices_list:
            input_obj = self.draw_dict[device.device_id]

            for input_port_id in device.inputs.keys():
                con_tup = device.inputs[input_port_id]

                if con_tup is not None:
                    output_dev_id = con_tup[0]
                    output_port_id = con_tup[1]

                    output_obj = self.draw_dict[output_dev_id]
                    self.make_single_connection((input_obj, input_port_id, output_obj, output_port_id))

    def make_single_connection(self, connection) -> None:
        """
        Create a single connection.

        Parameters:
        connection (tuple): Tuple containing input object, input port ID, output object, and output port ID.
        """
        inp_obj = connection[0]
        out_obj = connection[2]

        inp_dev_id = inp_obj.id
        out_dev_id = out_obj.id

        inp_port_id = connection[1]
        out_port_id = connection[3]

        inp_domain = self.domain_dict[inp_obj]
        out_domain = self.domain_dict[out_obj]

        inp_min_x, inp_max_x = inp_domain[0][0], inp_domain[1][0]
        inp_min_y, inp_max_y = inp_domain[0][1], inp_domain[1][1]

        start_x, start_y = inp_obj.input_dict[(inp_dev_id, inp_port_id)]
        end_x, end_y = out_obj.output_dict[(out_dev_id, out_port_id)]

        # Determine how we 'jut out' for inputs (which corner of bbox to go to)
        if np.abs(start_x - inp_min_x) < np.abs(start_x - inp_max_x):
            # We are on the left side
            if np.abs(start_y - inp_min_y) - 5 < np.abs(start_y - inp_max_y):
                # We are on the bottom side (bottom left)
                curr_coord = (inp_min_x - self.padding * (1 - self.fraction), inp_min_y - self.padding * (1 - self.fraction))
            else:
                # We are on the top side (top left)
                curr_coord = (inp_min_x - self.padding * (1 - self.fraction), inp_max_y + self.padding * (1 - self.fraction))
        else:
            # We are on the right side
            if np.abs(start_y - inp_min_y) < np.abs(start_y - inp_max_y):
                # We are on the bottom side (bottom right)
                curr_coord = (inp_max_x + self.padding * (1 - self.fraction), inp_min_y - self.padding * (1 - self.fraction))
            else:
                # We are on the top side (top right)
                curr_coord = (inp_max_x + self.padding * (1 - self.fraction), inp_max_y + self.padding * (1 - self.fraction))

        # Randomize color
        if self.fraction <= 0.42:
            index = 0
        elif self.fraction <= 0.59:
            index = 1
        else:
            index = 2

        color_arr = [self.fraction / 4, self.fraction / 4, self.fraction / 4]
        color_arr[index] = self.fraction / 2

        l1 = [
            (start_x, start_y),
            (curr_coord[0], start_y),
            (curr_coord[0], curr_coord[1])
        ]
        self.coords_array.append(l1)

        le = [
            (curr_coord[0], curr_coord[1]),
            (end_x + 20, curr_coord[1]),
            (end_x + 20, end_y),
            (end_x, end_y)
        ]
        self.coords_array.append(le)

    def draw_all_connections(self, this_coords_array) -> None:
        """
        Draw all connections.

        Parameters:
        this_coords_array (list): List of coordinates for all connections.
        """
        for coords_list in this_coords_array:
            glBegin(GL_LINE_STRIP)
            glColor3f(0, 0, 0)
            for coords in coords_list:
                glVertex2f(coords[0], coords[1])
            glVertex2f(coords[0], coords[1])
            glEnd()
