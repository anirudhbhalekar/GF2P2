"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
import numpy as np
import math
from OpenGL import GL, GLU, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

from logic_draw_3D import LogicDrawer3D
from connect_draw_3D import ConnectDrawer3D
import os

class MyGLCanvas3D(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos, z_pos): Handles text drawing
                                                  operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        #GLUT.glutInit()
        #GLUT.glutInitContextFlags(GLUT.GLUT_FORWARD_COMPATIBLE | GLUT.GLUT_DEBUG)
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.2]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [10.0, 10.0, 10.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.1, 0.1, 0.1, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, 'f')

        # Initialise variables for zooming
        self.zoom = 20

        self.names = parent.names
        self.network = parent.network
        self.monitors = monitors
        self.devices = devices

        self.parent = parent

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        self.devices_list = self.devices.devices_list
        self.obj_vertex_loader = {} # This will store the vertex data for all the objects!
        self.tube_vertices_list = []
        
        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        self.scene_renderer = LogicDrawer3D(self.names, self.devices, self.monitors, self.obj_vertex_loader)
        self.initialise_device_render()

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
   
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glViewport(0, 0, size.width, size.height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()  # lights positioned relative to the viewer
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.full_specular)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                        self.mat_diffuse)
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)

        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        GL.glEnable(GL.GL_NORMALIZE)

        # Viewing transformation - set the viewpoint back from the scene
        GL.glTranslatef(0.0, 0.0, -self.depth_offset)

        # Modelling transformation - pan, zoom and rotate
        GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        GL.glMultMatrixf(self.scene_rotate)
        GL.glScalef(self.zoom, self.zoom, self.zoom)
    
    def initialise_device_render(self): 

        """ The exact same as assemble devices - but its called only once 
            to initialise the input_output coords list"""
        x_start, y_start = 0, 30
        x_space, y_space = 20, 15

        curr_x, curr_y = x_start, y_start
        for device in self.devices_list: 
            # We render any object as it comes 
            device_id = device.device_id
            self.scene_renderer.return_io_list(device_id, curr_x, curr_y)
            curr_y -= y_space

            if curr_y < 0: 
                curr_y = y_start
                curr_x += x_space

        self.inputs_dict = self.scene_renderer.inputs_dict
        self.outputs_dict= self.scene_renderer.outputs_dict

        self.connect_render = ConnectDrawer3D(self.names, self.devices, self.monitors, self.network, 
                                              self.inputs_dict, self.outputs_dict)

        self.tube_vertices_list = self.connect_render.make_all_connections()

    def assemble_devices(self): 

        x_start, y_start = 0, 30
        x_space, y_space = 20, 15

        curr_x, curr_y = x_start, y_start
        for device in self.devices_list: 
            # We render any object as it comes 
            device_id = device.device_id
            self.scene_renderer.draw_with_id(device_id, curr_x, curr_y)

            curr_y -= y_space

            if curr_y < 0: 
                curr_y = y_start
                curr_x += x_space

    def assemble_connections(self): 
        self.connect_render.draw_connections(self.tube_vertices_list)

    def assemble_monitors(self): 
        monitors_dict = self.monitors.monitors_dictionary

        for key in monitors_dict.keys(): 
            dev_id = key[0]
            port_id = key[1]
            m_coord = self.outputs_dict[(dev_id, port_id)]
            self.scene_renderer.draw_monitor(m_coord[0], m_coord[1], dev_id, port_id)

    def render(self, text = None):
        """Handle all drawing operations."""
        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Draw a sample signal trace, make sure its centre of gravity
        # is at the scene origin
        self.assemble_devices()
        self.assemble_connections()
        self.assemble_monitors()
        #self.draw_cuboid(None, None, None, None, None)
        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()

    def on_paint(self, event):
        """Handle the paint event."""
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
    
        if not not hasattr(self, 'init'):
            # Configure the OpenGL rendering context
            self.init = True 
            self.init_gl()
               

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render()
        self.SwapBuffers()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        self.SetCurrent(self.context)

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y
            if event.LeftIsDown():
                GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
            if event.MiddleIsDown():
                GL.glRotatef((x + y), 0, 0, 1)
            if event.RightIsDown():
                self.pan_x += x
                self.pan_y -= y
            GL.glMultMatrixf(self.scene_rotate)
            GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, z_pos):
        """Handle text drawing operations."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_10

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)


