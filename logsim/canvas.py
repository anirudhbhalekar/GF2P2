import wx
import wx.grid as gridlib 
import wx.glcanvas as wxcanvas
import numpy as np
import os
from math import cos, sin, pi
from OpenGL import GL, GLUT
from OpenGL.GL import GL_LINE_STRIP, GL_LINE_LOOP, GL_POLYGON, GL_ENABLE_BIT, GL_LINE_STIPPLE
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINE_STRIP, GL_TRIANGLE_FAN, GL_LINE_LOOP
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, glPushAttrib, glLineStipple, glPopAttrib, glEnable
from OpenGL import GL, GLUT
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar2Wx

from logic_draw import LogicDrawer
from connect_draw import ConnectDrawer

import gettext
import sys
'''
# Initialize gettext translation
locale = "en"
if len(sys.argv) > 2:
    if sys.argv[2] == "el" or sys.argv[2] == "el_GR" or sys.argv[2] == "el_GR.utf8":
        locale = "el_GR.utf8"
        #print("Locale: Ελληνικα")
    elif sys.argv[2] == "en" or sys.argv[2] == "en_GB" or sys.argv[2] == "en_GB.utf8":
        #print("Locale: English")
        pass
    else:
        #print("Locale unknown, defaulting to English")
        pass
'''
if os.getenv("LANG") == "el_GR.UTF-8":
    locale = "el_GR.utf8"
    #print("Greek system language detected")
elif os.getenv("LANG") == "en_US.UTF-8" or os.getenv("LANG") == "en_GB.UTF-8":
    #print("Your system language is English.")
    locale = "en_GB.utf8"
else:
    #print("Attention - your system language is neither English nor Greek. Logsim will run in English.")
    locale = "en_GB.utf8"

lang = gettext.translation("logsim", localedir=os.path.join(os.path.dirname(__file__), 'locales'), languages=[locale], fallback=True)
lang.install()
_ = lang.gettext

class MyGLCanvas(wxcanvas.GLCanvas):
    """MyGLCanvas(wxcanvas.GLCanvas) - Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.
    message_display: message display widget.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing operations.

    reset_view(self): Resets the view to the default state.   
    """
    def __init__(self, parent, devices, monitors, message_display):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variable for message display widget
        self.message_display = message_display

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # get devices and monitors 
        self.devices = devices
        self.monitors = monitors
        self.names = parent.names

        self.parent = parent


        self.output_dicts = {}
        self.device_postions = {} # {dev_id : (x,y)}
        self.draw_obj_dict = {}
        self.domain_dict = {}
        
        self.coords_array = []
        
        

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        self.construct_dicts()

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def construct_dicts(self): 
        """Construct required dictionaries."""
        devices_list = self.devices.devices_list
        y_start = 300
        xs, ys = 0,y_start
        count = 0
        dist = 100
        min_y = 0

        # First we find the CLOCK type - we typically want this to be rendered 
        # in the left most part of the canvas
        for device in devices_list:
            if device.device_kind == self.devices.CLOCK: 
                # Render the CLOCK device at (0,0)
                ys = ys - count*dist
                count += 1
                self.device_postions[device.device_id] = (xs, ys)

        pos_x, pos_y = xs + 150, y_start
        
        # Remove all clock objects (we reserve first col for clocks only)
        for i, acc_device in enumerate(devices_list): 
            
            if acc_device.device_kind == self.devices.CLOCK: 
                continue
            
            num_inputs = len(acc_device.inputs.keys())
            d_kind = self.names.get_name_string(acc_device.device_kind)

            if d_kind in ["AND", "NAND", "NOR", "OR", "XOR"]: 
                dist_y = 100 
                if num_inputs > 2: 
                    dist_y += (num_inputs - 2) * 20 
            elif d_kind == "SWITCH": 
                dist_y = 100 
            else: 
                dist_y = 175

            if pos_y < min_y: 
                pos_y = y_start 
                pos_x += 175
            
            self.device_postions[acc_device.device_id] = (pos_x, pos_y)

            pos_y -= dist_y

        for device in devices_list: 
            dev_id = device.device_id

            render_obj = LogicDrawer(self.names, self.devices, self.monitors, dev_id) 
            render_obj.get_domain(self.device_postions[dev_id][0], self.device_postions[dev_id][1])
            
            for port, coord in render_obj.output_dict.items(): 
                self.output_dicts[port] = coord
            
            self.draw_obj_dict[dev_id] = render_obj
            self.domain_dict[render_obj] = render_obj.domain
        
        self.con_drawer_class = ConnectDrawer(self.domain_dict, self.draw_obj_dict, 1, self.coords_array, self.devices)
        self.con_drawer_class.make_all_connections()

    def render_circuit(self): 
        """Render all devices, connections, and monitors on screen."""
        devices_list = self.devices.devices_list

        for device in devices_list: 
            dev_id = device.device_id
            device_kind = self.names.get_name_string(device.device_kind)
            coords = self.device_postions[dev_id]

            render_obj = self.draw_obj_dict[dev_id]
            render_obj.draw_with_string(device_kind, coords[0], coords[1])
       
        # We will add connections here to reduce time complexity
        self.con_drawer_class.draw_all_connections(self.coords_array)

    def render_monitors(self): 
        """Assemble all monitors on screen."""
        monitors_dict = self.monitors.monitors_dictionary

        for key in monitors_dict.keys(): 
            dev_id = key[0]
            port_id = key[1]
            render_obj = self.draw_obj_dict[dev_id]
            output_dict = render_obj.output_dict
            m_coord = output_dict[(dev_id, port_id)]
            device_name = self.names.get_name_string(dev_id)

            if port_id is None: 
                name_string = str(device_name)
            else: 
                port_name = self.names.get_name_string(port_id)
                name_string = str(device_name + "." + port_name)

            monitor_obj = LogicDrawer(self.names, self.devices, self.monitors, dev_id)
            monitor_obj.draw_monitor(m_coord[0], m_coord[1], name_string)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        # Draw specified text at position (10, 10)
        self.render_circuit()
        self.render_monitors()
        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()
         # Update the message display widget
        self.message_display.SetValue(text)

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join([_("Canvas redrawn on paint event, size is "),
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def calc_distance(self, point1, point2): 
        """Calculate the Euclidean distance between two points, coord1 and coord2."""    
        (x1, y1) = point1
        (x2, y2) = point2

        return np.sqrt((x1-x2)**2 + (y1-y2)**2)
    

    def return_closest_output_id(self, mouse_coords, tol = 20): 
        """Return output id within tolerance of mouse click"""
        for port_tuple, coords in self.output_dicts.items():
            this_dist = self.calc_distance(coords, mouse_coords)
            if this_dist < tol: 
                return port_tuple

        return None

    def return_switch_id(self, mouse_coords, tol =40):
        """Returns closest switch id (in tolerance) to mouse coords"""
        for device in self.devices.devices_list: 
            if device.device_kind != self.devices.SWITCH: 
                continue
            dev_id = device.device_id
            draw_obj = self.draw_obj_dict[dev_id]
            d_x, d_y = draw_obj.x, draw_obj.y

            dist = self.calc_distance((d_x, d_y), mouse_coords)
            if dist < tol: 
                return dev_id

        return None
    
    def flip_switch(self, switch_id): 
        """Flips switch"""

        if switch_id is not None: 
            try: 
                switch_device = self.devices.get_device(switch_id) 
                curr_state = switch_device.switch_state
                self.devices.set_switch(switch_id, int(abs(curr_state - 1)))
            except: 
                return False
        
            return True
        else: 
            return False

    def do_zap_monitor(self, port_tuple): 
        """Remove a monitor when the user clicks on a monitor point after selecting 'Zap'."""
        if port_tuple is not None: 
            (dev_id, port_id) = port_tuple
            remove_mon = self.monitors.remove_monitor(dev_id, port_id)
            if remove_mon: 
                wx.MessageBox(_("Monitor Removed\n"))
            else: 
                wx.LogError(_("Error! Monitor not found!"))
        else: 
            pass
    
    def do_add_monitor(self, port_tuple): 
        """Add a monitor when the user clicks on a monitor point after selecting 'Add'."""
        if port_tuple is not None: 
            (dev_id, port_id) = port_tuple
            add_mon = self.monitors.make_monitor(dev_id, port_id)
            if add_mon: 
                wx.MessageBox(_("Monitor Added\n"))
            else: 
                wx.LogError(_("Error! Monitor already added!"))
        else: 
            pass
    
    def on_mouse(self, event):
        """Handle mouse events."""    
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

            text = "".join([_("Mouse button pressed at: "), str(event.GetX()),
                            ", ", str(event.GetY())])

            if self.parent.is_zap_monitor: 
                GL.glFlush()
                port_tuple = self.return_closest_output_id((ox, oy))
                self.do_zap_monitor(port_tuple)
            elif self.parent.is_add_monitor:
                GL.glFlush()
                port_tuple = self.return_closest_output_id((ox, oy))
                self.do_add_monitor(port_tuple)
            
            else: 
                switch_id = self.return_switch_id((ox, oy))
                self.flip_switch(switch_id)

        if event.ButtonUp():
            text = "".join([_("Mouse button released at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join([_("Mouse left canvas at: "), str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join([_("Mouse dragged to: "), str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(round(self.pan_x, 2)), ", ", str(round(self.pan_y, 2))])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join([_("Negative mouse wheel rotation. Zoom is now: "),
                            str(round(self.zoom, 2))])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join([_("Positive mouse wheel rotation. Zoom is now: "),
                            str(round(self.zoom,2))])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))
    
    def reset_view(self):
        """Resets the view to the default state."""
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1
        self.init = False
        self.Refresh()  # triggers the paint event
