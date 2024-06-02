from math import cos, sin, pi
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINE_STRIP
from logic_draw import LogicDrawer
import numpy.random as rd
import numpy as np

""" Basic Premis of ConnectDrawer is to take a dictionary of connections and 
    draw out all the connections as poly-lines 

"""
# NB no translation needed here.

class ConnectDrawer:
    """Handle all Connections drawings."""
    
    def __init__(self, domain_dict, draw_dict, padding, coords_array, devices) -> None:
        
        # We receive connection_list in the form (draw_obj, input_port_id, draw_obj, output_port_id)
        # Stores dict of all min_max coords {LogicDraw obj: (bounding box tuple)} for all operators
        self.domain_dict = domain_dict
        # This is the padding when connection line tries to navigate around another bounding box
        self.padding = padding
        self.fraction = 0.5 # This is a randomized fraction for each device
        self.coords_array = coords_array
        self.devices = devices
        self.draw_dict = draw_dict
    
    def make_all_connections(self) -> None: 

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
        
        connection_def = connection
        
        inp_obj = connection_def[0] 
        out_obj = connection_def[2]

        inp_dev_id = inp_obj.id
        out_dev_id = out_obj.id 

        inp_port_id = connection_def[1]
        out_port_id = connection_def[3]
        
        inp_domain = self.domain_dict[inp_obj]
        out_domain = self.domain_dict[out_obj]

        inp_min_x, inp_max_x = inp_domain[0][0], inp_domain[1][0]
        inp_min_y, inp_max_y = inp_domain[0][1], inp_domain[1][1]

        (start_x, start_y) = inp_obj.input_dict[(inp_dev_id, inp_port_id)]
        (end_x, end_y) = out_obj.output_dict[(out_dev_id, out_port_id)]


        # First determine for inputs how we 'jut out' (i.e. which corner of bbox to go to)

        if np.abs(start_x - inp_min_x) < np.abs(start_x - inp_max_x): 
            # We are on the left side
            if np.abs(start_y - inp_min_y) - 5 < np.abs(start_y - inp_max_y): 
                # We are on the bottom side
                # We are on the bottom left
                curr_coord = (inp_min_x - self.padding * (1 - self.fraction), inp_min_y - self.padding * (1 - self.fraction))
            else: 
                # We are on the top left
                curr_coord = (inp_min_x - self.padding * (1 - self.fraction), inp_max_y + self.padding * (1 - self.fraction))
        else: 
            # We are on the right side
            if np.abs(start_y - inp_min_y) < np.abs(start_y - inp_max_y): 
                # We are on the bottom side
                # We are on the bottom right
                curr_coord = (inp_max_x + self.padding * (1 - self.fraction), inp_min_y - self.padding * (1 - self.fraction))
            else: 
                # We are on the top right
                curr_coord = (inp_max_x + self.padding * (1 - self.fraction), inp_max_y + self.padding * (1 - self.fraction))

        # Similarily choose which corner of bbox we should aim to get to of the output

        # randomize color
        
        if self.fraction <= 0.42: index = 0 
        elif self.fraction <= 0.59: index = 1
        else: index = 2

        color_arr = [self.fraction/4, self.fraction/4, self.fraction/4]
        color_arr[index] = self.fraction/2

        l1 = []
        l1.append((start_x, start_y))
        l1.append((curr_coord[0], start_y))
        l1.append((curr_coord[0], curr_coord[1]))
        
        self.coords_array.append(l1)
        
        le = []
        le.append((curr_coord[0], curr_coord[1]))
        le.append((end_x + 20, curr_coord[1]))
        le.append((end_x + 20, end_y))
        le.append((end_x, end_y))

        self.coords_array.append(le)
        # Should have reached destination element now

    def draw_all_connections(self, this_coords_array): 

        for coords_list in this_coords_array: 
            glBegin(GL_LINE_STRIP)
            glColor3f(0,0,0)
            for coords in coords_list: 
                glVertex2f(coords[0], coords[1])
            
            glVertex2f(coords[0], coords[1])
            glEnd()