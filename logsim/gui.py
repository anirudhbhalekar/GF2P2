"""
Implement the graphical user interface for the Logic Simulator.

This module provides a graphical user interface (GUI) for the Logic Simulator,
enabling the user to run the simulation, adjust network properties, and visualize
the circuit and its outputs.

Classes:
--------
MyGLCanvas - Handles all canvas drawing operations, including rendering devices,
connections, and monitors. Supports panning and zooming.

PromptedTextCtrl - Custom text control with a prompt symbol '>' that prevents
deletion of history and only allows modification of the current line.

Gui - Configures the main window and all the widgets, including menus, buttons,
canvas, and text controls. Manages the interaction between the user and the
simulation.

RunApp - Initializes and runs the application.
"""
import wx
import wx.glcanvas as wxcanvas
import numpy as np
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
from logic_draw import LogicDrawer
from connect_draw import ConnectDrawer
import userint

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


        self.draw_obj_dict = {}
        self.domain_dict = {}
        self.random_pertubation = []

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

        for device in devices_list: 
            dev_id = device.device_id
            render_obj = LogicDrawer(self.names, self.devices, self.monitors, dev_id) 

            self.draw_obj_dict[dev_id] = render_obj


    def render_circuit(self): 
        """Render all devices, connections, and monitors on screen."""
        devices_list = self.devices.devices_list
        
        y_start = 300

        xs, ys = 0,y_start
        count = 0
        dist = 100

        max_vertical = 4

        # First we find the CLOCK type - we typically want this to be rendered 
        # in the left most part of the canvas
        for device in devices_list:
            if device.device_kind == self.devices.CLOCK: 
                # Render the CLOCK device at (0,0)
                ys = ys - count*dist
                count += 1
                
                # Call from dict
                clk_render = self.draw_obj_dict[device.device_id]
                clk_render.draw_clock(xs, ys)
                self.domain_dict[clk_render] = clk_render.domain
               
        pos_x, pos_y = 150, y_start
        min_y = 0

        
        # Remove all clock objects (we reserve first col for clocks only)
        for i, acc_device in enumerate(devices_list): 
            
            if acc_device.device_kind == self.devices.CLOCK: 
                continue
            
            device_render = self.draw_obj_dict[acc_device.device_id]
            num_inputs = len(acc_device.inputs.keys())
            d_kind = self.names.get_name_string(acc_device.device_kind)
            d_name = self.names.get_name_string(acc_device.device_id)

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
            
            # Call from dict
            device_render.draw_with_string(d_kind, pos_x, pos_y)
            self.domain_dict[device_render] = device_render.domain
            pos_y -= dist_y
   
       
        # We will add connections here to reduce time complexity
        for device in devices_list: 
            self.assemble_connection(device)
        

    def assemble_connection(self, input_device): 
        """Render all wires (connections) on screen."""
        input_obj = self.draw_obj_dict[input_device.device_id]
            
        for input_port_id in input_device.inputs.keys(): 
            con_tup = input_device.inputs[input_port_id]
            
            if con_tup is not None: 
                output_dev_id = con_tup[0]
                output_port_id = con_tup[1]

                output_obj = self.draw_obj_dict[output_dev_id]
                con_draw = ConnectDrawer((input_obj, input_port_id, output_obj, output_port_id), 
                                            self.domain_dict, 5)
                # Don't put padding too high - will break code 
                con_draw.draw_connection()


    def assemble_monitors(self): 
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
        #self.render_text(text, 10, 10)

        self.render_circuit()
        self.assemble_monitors()

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
                            str(round(self.pan_x, 2)), ", ", str(round(self.pan_y, 2))])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(round(self.zoom, 2))])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
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

class PromptedTextCtrl(wx.TextCtrl):
    """
    PromptedTextCtrl - Custom text control with a prompt symbol '>' that prevents
    deletion of history and only allows modification of the current line.

    This class extends wx.TextCtrl to create a command-line style text box where each
    line starts with a '>' prompt. Users can only edit the current line, preventing
    deletion or modification of previous lines.

    Methods
    -------
    __init__(parent, id=wx.ID_ANY, *args, **kwargs)
        Initializes the text control with the specified parent and parameters.
    write_prompt()
        Appends a prompt symbol '>' to the text control and moves the cursor to the end.
    on_text_entered(event)
        Handles the event when the user presses Enter, adding a new prompt symbol and
        moving the cursor to the end.
    on_key_down(event)
        Handles key down events to prevent deletion of previous lines. Allows deletion
        within the current line and ensures the prompt symbol remains at the beginning.
    on_text(event)
        Handle text change events to ensure the prompt symbol is not deleted.
    """
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
            self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
            self.Bind(wx.EVT_TEXT, self.on_text)

    def write_prompt(self):
        """Write the prompt symbol '>' and move the cursor to the end."""
        self.AppendText("> ")
        self.SetInsertionPointEnd()

    def on_text_entered(self, event):
        """Handle the event when the user enters text."""
        # Move the cursor to the end, then append the prompt
        self.AppendText("") # I have no idea why this works but don't delete it
        self.SetInsertionPointEnd()

    def on_key_down(self, event):
        """Handle key down events to prevent deletion of previous lines."""
        keycode = event.GetKeyCode()
        current_position = self.GetInsertionPoint()
        last_line_start = self.GetLastPosition() - self.GetLineLength(self.GetNumberOfLines() - 1)

        if keycode == wx.WXK_BACK:
            # Prevent deletion of the prompt symbol '>'
            if current_position > last_line_start + 2:
                event.Skip()
        elif keycode == wx.WXK_DELETE:
            # Prevent deletion of the prompt symbol '>'
            if current_position >= last_line_start + 2:
                event.Skip()
        elif keycode in (wx.WXK_UP, wx.WXK_DOWN):
            # Prevent moving the cursor to other lines
            return
        else:
            event.Skip()
    
    def on_text(self, event):
        """Handle text change events to ensure the prompt symbol is not deleted."""
        last_line = self.GetNumberOfLines() - 1
        line_text = self.GetLineText(last_line)
        
        if not line_text.startswith("> "):
            self.ChangeValue(self.GetValue()[:self.GetLastPosition() - len(line_text)] + "> " + line_text[2:])
            self.SetInsertionPointEnd()

class TextEditor(wx.Frame):
    """Text editor window for editing source files."""
    def __init__(self, parent, title, initial_text=""):
        super().__init__(parent, title=title, size=(400, 600))
        
        # Use default text control format wx.TextCtrl
        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.text_ctrl.SetValue(initial_text)

        # Add a Save button
        self.save_button = wx.Button(self, label='Save')
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

        # Use a sizer for layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.save_button, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)

        # Set minimum window size and make "sizer" the sizer
        self.SetSizeHints(200, 400)
        self.SetSizer(sizer)

    def get_text(self):
        """Get text content of the text editor."""
        return self.text_ctrl.GetValue()

    def on_save(self, event):
        """Handle save button click."""
        # Open a file dialog for the user to choose a file location
        with wx.FileDialog(self, "Save File", wildcard="Text files (*.txt)|*.txt",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                # If the user cancels, return without saving
                return
            
            # Get the selected file path
            filepath = file_dialog.GetPath()
            
            try:
                # Open the file in write mode and write the text from the editor
                with open(filepath, 'w') as file:
                    text = self.text_ctrl.GetValue()
                    file.write(text)
            except IOError:
                # Handle any errors that occur during file saving
                wx.LogError("Cannot save current data to file.")

class Gui(wx.Frame):
    """Configure the main window and all the widgets apart from the text box.

    This class provides a graphical user interface for the Logic Simulator and enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title : str
        Title of the window.
    path : str
        Path to the source file.
    names : Names
        Instance of the Names class.
    devices : Devices
        Instance of the Devices class.
    network : Network
        Instance of the Network class.
    monitors : Monitors
        Instance of the Monitors class.

    Public methods
    --------------
    on_menu(self, event)
        Event handler for the file menu.
    on_spin(self, event)
        Event handler for when the user changes the spin control value.
    on_run_button(self, event)
        Event handler for when the user clicks the run button.
    on_text_box(self, event)
        Event handler for when the user enters text.
    """
    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise main window, widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        menuBar = wx.MenuBar()

        # Define all the menu tabs
        fileMenu = wx.Menu()
        sourceMenu = wx.Menu()
        commandMenu = wx.Menu()
        
        try: 
            font = wx.Font(wx.FontInfo(9).FaceName("Consolas"))
            self.SetFont(font)
        except: 
            pass
        
        # Add subtabs and titles to each tab
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        sourceMenu.Append(wx.ID_OPEN, "&Open")
        sourceMenu.Append(wx.ID_EDIT, "&Edit")
        commandMenu.Append(wx.ID_HELP_COMMANDS, "&Commands")
        
        # Populate the menu bar
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(sourceMenu, "&Source") # for source/definition file being parsed
        menuBar.Append(commandMenu, "&Command") # list of user commands

        self.SetMenuBar(menuBar)

        self.path = path 
        self.names = names
        self.network = network
        self.monitors = monitors
        self.devices = devices

        self.cycle_count = 10
        self.cycles_completed = 0

        # Message display widget
        self.message_display = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Canvas for drawing
        self.canvas = MyGLCanvas(self, devices, monitors, self.message_display)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, initial=self.cycle_count, min=1, max=50)
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
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        canvas_plot_sizer = wx.BoxSizer(wx.VERTICAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Initialise some empty matplotlib figure
        self.configure_matplotlib_canvas()
        self.matplotlib_canvas = FigureCanvas(self, -1, self.figure)

        # Arrange sizers, all stemming from main sizer
        canvas_plot_sizer.Add(self.canvas, 2, wx.EXPAND | wx.ALL, 1)
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

        # Set minimum window size and make main_sizer parent sizer
        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)
    
    def execute_circuit(self, cycles): 
        """Simulates the circuit for N cycles"""
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                wx.LogError("Error! Network oscillating.")
                return False
        self.monitors.display_signals()
        return True
    
    def run_circuit(self, cycles): 
        self.cycles_completed = 0
        self.monitors.reset_monitors()
        self.devices.cold_startup()

        if self.execute_circuit(cycles): 
            self.cycles_completed += cycles
    

    def continue_circuit(self, cycles):
        """Continues the simulation for N cycles"""
        if self.cycles_completed == 0: 
            wx.LogError("Nothing to continue - run the simulation first")
        elif self.execute_circuit(cycles): 
            self.cycles_completed += cycles

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
            if hasattr(self, 'editor') and self.editor.IsShown():
                # If the editor is already open and visible, just bring it to front
                self.editor.Raise()
            else:
                # Otherwise, open and create the editor
                self.editor = TextEditor(self, "Text Editor", initial_text="Hello world")
                self.editor.Show()
        if Id == wx.ID_HELP_COMMANDS:
            wx.MessageBox("List of user commands: "
                        "\nr N - run the simulation for N cycles"
                        "\nc N - continue simulation for N cycles"
                        "\ns X N - set switch X to N (0 or 1)"
                        "\nm X - set a monitor on signal X"
                        "\nz X - zap the monitor on signal X"
                        "\nh - print a list of available commands on the terminal"
                        "\nq - quit the simulation")
        if Id == wx.ID_OPEN:
            with wx.FileDialog(self, "Open New Source File",
                            wildcard="TXT files (*.txt)|*.txt",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:

                if file_dialog.ShowModal() == wx.ID_CANCEL:
                    return

                pathname = file_dialog.GetPath()

                try:
                    # Reinitialize the names, devices, network, and monitors
                    self.names = Names()
                    self.devices = Devices(self.names)
                    self.network = Network(self.names, self.devices)
                    self.monitors = Monitors(self.names, self.devices, self.network)

                    # Reinitialize the scanner and parser with the new file
                    self.scanner = Scanner(pathname, self.names)
                    self.parser = Parser(self.names, self.devices, self.network, self.monitors, self.scanner)
                    
                    # Parse the new network file
                    if self.parser.parse_network(): 

                        # Reinitialize the canvas with the new devices and monitors
                        self.canvas.Destroy()  # Destroy the old canvas
                        self.canvas = MyGLCanvas(self, self.devices, self.monitors, self.message_display)

                        # Update the layout to replace the old canvas with the new one
                        main_sizer = self.GetSizer()
                        canvas_plot_sizer = main_sizer.GetChildren()[0].GetSizer()

                        # Clear matplotlib canvas
                        self.configure_matplotlib_canvas()
                        self.matplotlib_canvas = FigureCanvas(self, -1, self.figure)

                        # Remove the old canvas and add the new one
                        canvas_plot_sizer.Clear(delete_windows=False)
                        canvas_plot_sizer.Add(self.canvas, 2, wx.EXPAND | wx.ALL, 1)
                        canvas_plot_sizer.Add(self.matplotlib_canvas, 1, wx.EXPAND | wx.ALL, 1)

                        # Refresh the layout
                        main_sizer.Layout()

                        # Print the name of the file opened to the terminal (text box) window
                        self.text_box.AppendText(f" Opened file: {pathname}\n>")
                    else: 
                        num_errors = self.parser.error_count
                      
                        wx.MessageBox(f"Error! Faulty definition file! \n"
                                      "\n"
                                      f"{num_errors} errors caught")

                except Exception as ex:
                    wx.LogError(f"Cannot open file: {ex}")


    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        self.cycle_count = spin_value
        
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.run_circuit(self.cycle_count)
        self.canvas.render(text)

        try: 
            self.monitor_plot()
        except Exception: 
            wx.LogError("Run failed - cannot plot monitors")
        
    def on_continue_button(self, event): 
        """Handle continue button event"""
        text = "Continue button pressed."
        self.continue_circuit(self.cycle_count)
        self.canvas.render(text)

        try: 
            self.monitor_plot()
        except Exception: 
            wx.LogError("Run failed - cannot plot monitors")

    def configure_matplotlib_canvas(self): 
        """ Sets the config params of the matplotlib canvas"""
        
        hfont = {'fontname':'Consolas'}
        self.figure = Figure(figsize=(5,2))
        self.axes = self.figure.add_subplot(111)
        self.axes.set_title("Monitor Plots", **hfont)
        self.axes.tick_params(axis = 'both', left = False, right = False, labelright = False, labelleft = False, labelbottom = False)

    def on_continue_button(self, event): 
        pass
    
    def monitor_plot(self):
        
        plot_array = []
        name_array = []

        for device_id, output_id in self.monitors.monitors_dictionary: 

            one_d_signal = []
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]

            for signal in signal_list: 
                if signal == self.devices.HIGH: 
                    one_d_signal.append(1)
                    one_d_signal.append(1)
                if signal == self.devices.LOW: 
                    one_d_signal.append(0)
                    one_d_signal.append(0)
                if signal == self.devices.RISING: 
                    one_d_signal.append(0)
                    one_d_signal.append(1)
                if signal == self.devices.FALLING: 
                    one_d_signal.append(1)
                    one_d_signal.append(0)
                if signal == self.devices.BLANK: 
                    one_d_signal.append(np.nan)
                    one_d_signal.append(np.nan)
            
            plot_array.append(one_d_signal)
            name_array.append(monitor_name)
        
        self.configure_matplotlib_canvas()

        for i, int_signal in enumerate(plot_array): 
            name = name_array[i]
            print(int_signal)
            int_signal = np.array(int_signal) + 2*i
            self.axes.plot(int_signal, label = name) 
        
        self.axes.set_ylim(0, 2*i + 2)
        prop={'family':'Consolas', 'size':8}
        self.figure.legend(fontsize="8", loc ="upper left", prop = prop)
        self.matplotlib_canvas = FigureCanvas(self, -1, self.figure)
        
        main_sizer = self.GetSizer()
        canvas_plot_sizer = main_sizer.GetChildren()[0].GetSizer()

        # Remove the old canvas and add the new one
        canvas_plot_sizer.Clear(delete_windows=False)
        canvas_plot_sizer.Add(self.canvas, 2, wx.EXPAND | wx.ALL, 1)
        canvas_plot_sizer.Add(self.matplotlib_canvas, 1, wx.EXPAND | wx.ALL, 1)

        # Refresh the layout
        main_sizer.Layout()


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

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text = self.text_box.GetValue()# Get the user's input and remove leading/trailing spaces
        text = str(text) 
        print(text)
        print(text[2:].strip())
        print('h')
        print(text == 'h')
        # Parse the user's input and call the corresponding functions from userint
        if text.startswith('r '):
            # Run simulation for N cycles
            try:
                N = int(text[2:])
                print(N)
                userint.run_command(N)
                self.text_box.AppendText(f"Running simulation for {N} cycles.\n")
            except ValueError:
                self.text_box.AppendText("Invalid command. Please provide a valid number of cycles.\n")
        elif text.startswith('c '):
            # Continue the simulation for N cycles
            try:
                N = int(text[2:])
                print(N)
                userint.continue_command(N)
                self.text_box.AppendText(f"Continuing simulation for {N} cycles.\n")
            except ValueError:
                self.text_box.AppendText("Invalid command. Please provide a valid number of cycles.\n")
        elif text.startswith('s '):
            # Set switch X to N (0 or 1)
            try:
                switch_id, value = text[2:].split()
                switch_id = int(switch_id)
                value = int(value)
                userint.switch_command(switch_id, value)
                self.text_box.AppendText(f"Setting switch {switch_id} to {value}.\n")
            except ValueError:
                self.text_box.AppendText("Invalid command format. Please provide switch ID and value.\n")
        elif text.startswith('m '):
            # Add a monitor on signal X
            signal = text[2:]
            userint.monitor_command(signal)
            self.text_box.AppendText(f"Adding monitor on signal {signal}.\n")
        elif text.startswith('z '):
            # Zap the monitor on signal X
            signal = text[2:]
            userint.zap_command(signal)
            self.text_box.AppendText(f"Zapping monitor on signal {signal}.\n")
        elif text == 'h':
            # Print a list of available commands
            self.text_box.AppendText(
                "List of available commands:\n"
                "r N       - run the simulation for N cycles\n"
                "c N       - continue the simulation for N cycles\n"
                "s X N     - set switch X to N (0 or 1)\n"
                "m X       - add a monitor on signal X\n"
                "z X       - zap the monitor on signal X\n"
                "h         - print a list of available commands\n"
                "q         - quit the program\n"
            )
        elif text == 'q':
            self.close(True)
        else:
            #self.text_box.AppendText("Invalid command. A list of available commands can be obtained by entering 'h', or opening the 'Commands' tab.\n")
            wx.LogError("Invalid command. A list of available commands can be obtained by entering 'h', or opening the 'Commands' tab.\n")
class RunApp(wx.App): 
    """Combines Canvas onto App with Matplotlib"""
    def __init__(self):
        wx.App.__init__(self, redirect=False)

