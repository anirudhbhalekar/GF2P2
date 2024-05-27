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
from math import cos, sin, pi
from OpenGL import GL, GLUT
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINE_STRIP, GL_TRIANGLE_FAN, GL_LINE_LOOP
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar2Wx

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from logicdraw import LogicDrawer, DrawConnections

class MyGLCanvas(wxcanvas.GLCanvas):
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

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
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

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

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
        #self.render_text(text, 10, 10)

        
        # Draw logic gates using the LogicDrawer class
        
        G1 = LogicDrawer("G1", x=50, y=200)
        G1.draw_and_gate()
        # Add the text label
        self.render_text(str(G1.name), G1.x + (G1.length / 2), G1.y + (G1.height / 2))

        G2 = LogicDrawer("G2", x=150, y=200)
        G2.draw_nand_gate()
        self.render_text(str(G2.name), G2.x + (G2.length / 2), G2.y + (G2.height / 2))

        G3 = LogicDrawer("G3", x=250, y = 200)
        G3.draw_or_gate()
        self.render_text(str(G3.name), G3.x + (G3.length / 2), G3.y + (G3.height / 2))

        G4 = LogicDrawer("G4", x=350, y = 200)
        G4.draw_nor_gate()
        self.render_text(str(G4.name), G4.x + (G4.length / 2), G4.y + (G4.height / 2))

        G5 = LogicDrawer("G5", x=450, y = 200)
        G5.draw_xor_gate()
        self.render_text(str(G5.name), G5.x + (G5.length / 2), G5.y + (G5.height / 2))
        
        SW1 = LogicDrawer("SW1", x=50, y=100)
        SW1.draw_switch()
        # For switches render text under the circle
        self.render_text(str(SW1.name), SW1.x - 10, SW1.y - 30)

        CLK1 = LogicDrawer("CLK1", x=150, y=100)
        CLK1.draw_clock()
        # For clocks render text under the square
        self.render_text(str(CLK1.name), CLK1.x, CLK1.y - 10)

        DTYPE1 = LogicDrawer("DTYPE1", x=250, y=50)
        DTYPE1.draw_dtype()
        # For dtypes render text under the object
        self.render_text(str(DTYPE1.name), DTYPE1.x + 10, DTYPE1.y - 10)
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
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

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
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
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

# class for dealing with text box
class PromptedTextCtrl(wx.TextCtrl):
    """Configure the text box located to the side of the window.
    
    DOCSTRING TO BE COMPLETED LATER"""
    def __init__(self, parent, id=wx.ID_ANY, *args, **kwargs):
            """Initialise the text box."""
            # Combine the necessary styles
            style = wx.TE_PROCESS_ENTER | wx.TE_MULTILINE | wx.TE_RICH2 | wx.VSCROLL
            # Remove 'style' from kwargs if it exists to avoid conflict
            kwargs['style'] = style
            # Initialize the wx.TextCtrl with the combined styles
            super().__init__(parent, id, *args, **kwargs)
            self.write_prompt()
            self.Bind(wx.EVT_TEXT_ENTER, self.on_text_entered)

    def write_prompt(self):
        """Write the prompt symbol '>' and move the cursor to the end."""
        self.AppendText("> ")
        self.SetInsertionPointEnd()

    def on_text_entered(self, event):
        """Handle the event when the user enters text."""
        #self.SetInsertionPointEnd()
        # Add a new prompt symbol and move the cursor to the end
        self.AppendText("\n> ")
        self.SetInsertionPointEnd()


class Gui(wx.Frame):
    """Configure the main window and all the widgets apart from the text box.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        menuBar = wx.MenuBar()

        # Define all the menu tabs
        fileMenu = wx.Menu()
        sourceMenu = wx.Menu()
        commandMenu = wx.Menu()

        # Add subtabs and titles to each tab
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        sourceMenu.Append(wx.ID_EDIT, "&Edit")
        commandMenu.Append(wx.ID_HELP_COMMANDS, "&Commands")
        
        # Populate the menu bar
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(sourceMenu, "&Source") # for source/definition file being parsed
        menuBar.Append(commandMenu, "&Command") # list of user commands

        self.SetMenuBar(menuBar)

        # Message display widget
        self.message_display = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Canvas for drawing
        self.canvas = MyGLCanvas(self, devices, monitors, self.message_display)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        ''' Spin is the up/down number widget. 
        For now, I set this to have a range of 1 to 10, with a default of 2
        This will have to be changed as the user can specify clock cycle
        (output changes every n cycles)'''
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, initial=2, min=1, max=10)
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.reset_view_button = wx.Button(self, wx.ID_ANY, "Reset View")
        self.text_box = PromptedTextCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self.clear_button = wx.Button(self, wx.ID_ANY, "Clear terminal") # button for clearing terminal output

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_button)
        self.reset_view_button.Bind(wx.EVT_BUTTON, self.on_reset_view_button)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        canvas_plot_sizer = wx.BoxSizer(wx.VERTICAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Initialise some empty matplotlib figure
        self.figure = Figure(figsize=(5,2))
        self.axes = self.figure.add_subplot(111)
        self.matplotlib_canvas = FigureCanvas(self, -1, self.figure)

        # Arrange sizers, all stemming from main sizer
        canvas_plot_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 1)
        canvas_plot_sizer.Add(self.matplotlib_canvas, 1, wx.EXPAND | wx.ALL, 1)

        main_sizer.Add(canvas_plot_sizer, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(button_sizer, 1, wx.EXPAND | wx.ALL, 5)
        side_sizer.Add(self.text_box, 15, wx.EXPAND | wx.ALL, 5) # expanding text box
        side_sizer.Add(self.clear_button, 1, wx.EXPAND | wx.ALL, 5)
        side_sizer.Add(self.message_display, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer.Add(self.reset_view_button, 1, wx.ALL, 5)
        button_sizer.Add(self.run_button, 1, wx.ALL, 5)
        
        # Initialise window size and make main_sizer parent sizer
        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def plot_monitors(self): 
        """Given some monitor outputs, draw the resulting plot on the matplotlib axes"""
        pass
    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_EDIT:
            wx.MessageBox("Coming soon!",
                          "Source Definition File", wx.CANCEL | wx.APPLY)
        if Id == wx.ID_HELP_COMMANDS:
            wx.MessageBox("List of user commands: "
                        "\nr N - run the simulation for N cycles"
                        "\nc N - continue simulation for N cycles"
                        "\ns X N - set switch X to N (0 or 1)"
                        "\nm X - set a monitor on signal X"
                        "\nz X - zap the monitor on signal X"
                        "\nq - quit the simulation")

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.canvas.render(text)

    def on_clear_button(self, event):
        """Handle the event when the user clicks the clear button."""
        text = "Clear button pressed."
        self.canvas.render(text)
        self.text_box.SetValue("> ")  # Clear the text box and add prompt

    def on_reset_view_button(self, event):
        """Handle the event when the user clicks the reset view button."""
        text = "Reset view button pressed"
        self.canvas.render(text)
        self.canvas.reset_view()

class RunApp(wx.App): 
    """Combines Canvas onto App with Matplotlib"""
    def __init__(self):
        wx.App.__init__(self, redirect=False)

    
'''
if __name__ == "__main___": 

    names = Names()
    scanner = Scanner("definition_files/test_ex_null.txt", names)
'''