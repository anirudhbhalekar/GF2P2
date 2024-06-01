import math
import numpy as np
from OpenGL.GL import GL_LINE_STRIP, GL_LINE_LOOP, GL_POLYGON, GL_ENABLE_BIT, GL_LINE_STIPPLE
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, glPushAttrib, glLineStipple, glPopAttrib, glEnable
from OpenGL import GL, GLUT
import os

class ConnectDrawer3D: 

    def __init__(self, names, devices, monitors, network, vertex_loader) -> None:

        self.names = names 
        self.devices = devices 
        self.network = network 
        self.monitors = monitors
        self.vertex_loader = vertex_loader
    
    def draw_all_connections(self): 

        pass 

    def draw_single_connection(self): 
        pass 
        
        # we have the input and output ids of two 