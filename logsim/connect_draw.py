from math import cos, sin, pi
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINE_STRIP, GL_LINE_LOOP
from logic_draw import LogicDrawer

""" Basic Premis of ConnectDrawer is to take a dictionary of connections and 
    draw out all the connections as poly-lines 


"""

class ConnectDrawer:
    """Handle all Connections drawings."""
    
    def __init__(self, connection_list: list):
        
        # We receive connection_list in the form (draw_obj, outgoing id, draw_obj, input_id)
        self.connection_list = connection_list
        

    def draw_all_connections(self): 

        for connection_def in self.connection_list: 

            inp_obj = connection_def[0] 
            out_obj = connection_def[2]

            inp_id = connection_def[1]
            out_id = connection_def[3]

            (start_x, start_y) = inp_obj.input_list[inp_id]
            (end_x, end_y) = out_obj.output_list[out_id]

            d

            



        