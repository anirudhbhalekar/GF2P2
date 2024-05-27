from math import cos, sin, pi
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINE_STRIP, GL_LINE_LOOP
from logic_draw import LogicDrawer


class ConnectDrawer:
    """Handle all Connections drawings."""
    
    def __init__(self, input_operator: LogicDrawer, output_operator: LogicDrawer):
        
        self.input_operator = input_operator
        self.output_operator = output_operator

    
    def draw_connections(self): 

        pass