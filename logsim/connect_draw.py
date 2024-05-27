from math import cos, sin, pi
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINE_STRIP, GL_LINE_LOOP
from logic_draw import LogicDrawer

""" Basic Premis of ConnectDrawer is to take a dictionary of connections and 
    draw out all the connections as poly-lines 


"""

class ConnectDrawer:
    """Handle all Connections drawings."""
    
    def __init__(self, connection_list: list, domain_dict: dict):
        
        # We receive connection_list in the form (draw_obj, outgoing id, draw_obj, input_id)
        self.connection_list = connection_list

        # Stores dict of all min_max coords (bounding box) for all operators
        self.domain_dict = domain_dict
        

    def draw_all_connections(self): 

        for connection_def in self.connection_list: 
            self.draw_one_connection(connection_def)
    
    def draw_one_connection(self, connection_def): 
        
        inp_obj = connection_def[0] 
        out_obj = connection_def[2]

        inp_id = connection_def[1]
        out_id = connection_def[3]

        inp_domain = self.domain_dict[inp_obj]
        out_domain = self.domain_dict[out_obj]

        num_inputs = len(inp_obj.input_list)
        num_outputs = len(out_obj.output_list) 

        (start_x, start_y) = inp_obj.input_list[inp_id]
        (end_x, end_y) = out_obj.output_list[out_id]

        if inp_id + 1 < num_inputs/2: 
            # We will go down and to the left
            d_coord = inp_domain[0]

        

        glBegin(GL_LINE_STRIP)
        glVertex2f(start_x, start_y)
        glVertex2f(d_coord[0], start_y)
        glVertex2f(d_coord[0], d_coord[1])

        MAX_Y = 500
        MIN_Y = -500


            



        