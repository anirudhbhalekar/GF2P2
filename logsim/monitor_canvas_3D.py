"""
This module contains custom classes for creating a graphical user interface
and handling OpenGL rendering within a wxPython application.

Classes:
--------
    - MyGLCanvasMonitor3D: A custom wx.glcanvas.GLCanvas class for handling
      OpenGL rendering, event handling, and drawing operations for 3D logic
      signals.
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


class MyGLCanvasMonitor3D(wxcanvas.GLCanvas):
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

    def __init__(self, parent, devices : Devices, monitors: Monitors):
        """Initialise canvas properties and useful variables."""

        gl_attribs = wx.glcanvas.GLContextAttrs()
        gl_attribs = gl_attribs.CoreProfile().OGLVersion(4, 5).Robust().ResetIsolation().EndList()

        super().__init__(parent, -1,
                         attribList=gl_attribs)
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
        self.monitor_vertex_loader = {} # {signal_type: vertices}
        self.face_loader = {}
        self.signal_renderer = None
        self.color_arr = []

        self.blank_signal = ["BLANK"] 

        self.max_view = self.parent.max_3D_view
        self.scroll_val = self.parent.scroll_val

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000
        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        self.signal_renderer = LogicDrawer3D(self.names, self.devices, self.monitors, self.monitor_vertex_loader, self.face_loader)
        self.initialise_monitor_plots()

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)

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
        GL.glTranslatef(25, 0.0, -self.depth_offset * 2)
        GL.glRotatef(-60, 1, 0, 0)

        # Modelling transformation - pan, zoom and rotate
        GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        GL.glMultMatrixf(self.scene_rotate)
        GL.glScalef(self.zoom, self.zoom, self.zoom)

    def initialise_monitor_plots(self): 

        self.plot_array = []
        self.name_array = []
        self.all_signals = []
        self.m_names = []

        count = 0
        blank_signal = self.blank_signal*self.parent.cycles_completed

        if not bool(self.monitors.monitors_dictionary): 
            return 
        for device_id, output_id in self.monitors.monitors_dictionary: 
        
            if count >= len(self.color_arr):
                self.color_arr.append((0.25 + np.random.uniform(0,0.7), 0.25 + np.random.uniform(0,0.7), 0.25 + np.random.uniform(0,0.7)))
            
            count += 1
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]

            one_d_signal = []
            for signal in signal_list: 
                if signal == self.devices.HIGH: 
                    s_name = "HIGH"

                if signal == self.devices.LOW: 
                    s_name = "LOW"

                if signal == self.devices.RISING: 
                    s_name = "RISING"

                if signal == self.devices.FALLING: 
                    s_name = "FALLING"

                if signal == self.devices.BLANK: 
                    s_name = "BLANK"
   
                one_d_signal.append(s_name)
            if len(one_d_signal) < self.parent.cycles_completed:
                one_d_signal = blank_signal + one_d_signal
                one_d_signal = one_d_signal[-self.parent.cycles_completed:]
            
            self.all_signals.append(one_d_signal)
            self.m_names.append(monitor_name)
    
    def render_monitor_plots(self): 

        x_dist = 2
        y_dist = 15
        y_offset = 0
        x_offset = 0

        GL.glColor3f(1.0,1.0,1.0)
        self.signal_renderer.render_text("Time Axis", -15, 15 , 10)
        for i, signal_list in enumerate(self.all_signals): 
            x_offset = 0
            color = self.color_arr[i]
            monitor_name = self.m_names[i]
            
            signal_list = signal_list[self.scroll_val: self.scroll_val + self.max_view]
            
            for j, s_name in enumerate(signal_list): 
                if (j + self.scroll_val) % 10 == 0: 
                    GL.glColor3f(1.0,1.0,1.0)
                    self.signal_renderer.render_text(str(int(j + self.scroll_val)), x_offset, +15, 0)

                self.signal_renderer.draw_signal(x_offset, y_offset, s_name, color)
                x_offset += x_dist

            self.signal_renderer.render_text(monitor_name, -15, y_offset, 10)
            y_offset -= y_dist

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.render_monitor_plots()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()
        
    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render()

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
