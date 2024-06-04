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
import wx.grid as gridlib 
import wx.glcanvas as wxcanvas
import numpy as np
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
from sys import platform
import os

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from logic_draw import LogicDrawer
from connect_draw import ConnectDrawer
from userint import UserInterface 
from device_canvas_3D import MyGLCanvas3D
from monitor_canvas_3D import MyGLCanvasMonitor3D

from canvas import MyGLCanvas
from textctrl import TextEditor, PromptedTextCtrl
import gettext
import sys
# Initialize gettext translation
locale = sys.argv[2] if len(sys.argv) > 2 else "en"
lang = gettext.translation("logsim", localedir=r'C:\Users\Shawn\Documents\Cambridge Part IIA\Project GF2\GF2P2\logsim\locales', languages=[locale], fallback=True)
lang.install()
_ = lang.gettext


class RunApp: 
    def __init__(self, path, names, devices, network, monitors):
        
        self.path = path
        self.names = names 
        self.devices = devices 
        self.network = network 
        self.monitors = monitors

        GLUT.glutInit()
        GLUT.glutInitDisplayMode(GLUT.GLUT_DOUBLE | GLUT.GLUT_RGBA)
        GLUT.glutCreateWindow(_("Logsim 2.0"))
        GLUT.glutDisplayFunc(self.show_frame)
        GLUT.glutMainLoop()
        return True
    
    def show_frame(self): 
        app = wx.App()
        gui = Gui(_("Logic Simulator"), self.path, self.names, self.devices, self.network,
                    self.monitors)
        gui.Show(True)
        app.MainLoop()


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

        self.language_code = 'en'  # Default to English on startup
        self.change_language(self.language_code)

        # Configure the file menu
        menuBar = wx.MenuBar()

        if "wayland" in os.getenv("XDG_SESSION_TYPE", "").lower() and not os.environ.get("PYOPENGL_PLATFORM", ""):
            os.environ["PYOPENGL_PLATFORM"] = "egl"

        # Define all the menu tabs
        fileMenu = wx.Menu()
        sourceMenu = wx.Menu()
        commandMenu = wx.Menu()
        view3DMenu = wx.Menu()
        languageMenu = wx.Menu()  # New menu for language selection
        GLUT.glutInit()
        GLUT.glutInitContextFlags(GLUT.GLUT_FORWARD_COMPATIBLE | GLUT.GLUT_DEBUG)

        try: 
            font = wx.Font(wx.FontInfo(9).FaceName("Consolas"))
            self.SetFont(font)
        except: 
            pass

        # Create an instance of the UserInterface class
        self.user_interface = UserInterface(names, devices, network, monitors)
        
        # Add subtabs and titles to each tab
        fileMenu.Append(wx.ID_ABOUT, _("&About"))
        fileMenu.Append(wx.ID_EXIT, _("&Exit"))
        sourceMenu.Append(wx.ID_OPEN, _("&Open"))
        sourceMenu.Append(wx.ID_EDIT, _("&Edit"))
        commandMenu.Append(wx.ID_HELP_COMMANDS, _("&Commands"))
        view3DMenu.Append(wx.ID_PREFERENCES,_("&Change 3D Signal Max"))
        view3DMenu.Append(wx.ID_APPLY,_("&Change 2D Signal Max"))
        # Add language options
        languageMenu.Append(101, "English")
        languageMenu.Append(102, "Ελληνικά")  # Greek in Greek

        # Populate the menu bar
        menuBar.Append(fileMenu, _("&File"))
        menuBar.Append(sourceMenu, _("&Source")) # for source/definition file being parsed
        menuBar.Append(commandMenu, _("&Command")) # list of user commands
        menuBar.Append(view3DMenu, _("&View Options"))
        menuBar.Append(languageMenu, ("&ABC/ΠΣΩ"))  # Language selection menu

        self.SetMenuBar(menuBar)

        self.path = path 
        self.names = names
        self.network = network
        self.monitors = monitors
        self.devices = devices

        self.is_zap_monitor = False
        self.is_add_monitor = False

        self.cycle_count = 10
        self.cycles_completed = 0

        # Message display widget
        self.message_display = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        # Canvas for drawing
        self.canvas = MyGLCanvas(self, devices, monitors, self.message_display)
        # Text editor for definition files window
        self.editor = None

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, _("Cycles")) 
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, initial=self.cycle_count, min=1, max=50)
        self.run_button = wx.Button(self, wx.ID_ANY, _("Run"))
        self.continue_button = wx.Button(self, wx.ID_ANY, _("Continue"))
        self.reset_plot_button = wx.Button(self, wx.ID_ANY, _("Reset Plot"))
        self.zap_monitor_button = wx.ToggleButton(self,wx.ID_ANY, _("Zap Monitor"))
        self.add_monitor_button = wx.ToggleButton(self, wx.ID_ANY, _("Add Monitor"))
        self.reset_view_button = wx.Button(self, wx.ID_ANY, _("Reset View"))
        self.text_box = PromptedTextCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self.clear_button = wx.Button(self, wx.ID_ANY, _("Clear terminal")) # button for clearing terminal output
        self.switch_to_3D_button = wx.ToggleButton(self, wx.ID_ANY, _("3D Mode")) # button to switch canvases out
        self.scroll_bar = wx.ScrollBar(self, wx.ID_ANY)
        self.scroll_bar.SetScrollbar(0, 10, 10, 9)
        
        self.is3D = False
        self.max_3D_view = 50
        self.max_2D_view = 100
        self.max_total = 2000
        self.scroll_val = 0
        self.plot_array = []
        self.name_array = []

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.reset_plot_button.Bind(wx.EVT_BUTTON, self.on_reset_plot_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_button)
        self.reset_view_button.Bind(wx.EVT_BUTTON, self.on_reset_view_button)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)
        self.zap_monitor_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_zap_button)
        self.add_monitor_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_add_button)
        self.switch_to_3D_button.Bind(wx.EVT_TOGGLEBUTTON, self.draw_canvas_to_3D)
        self.scroll_bar.Bind(wx.EVT_SCROLL, self.on_scroll)

        # Bind language selection events
        self.Bind(wx.EVT_MENU, self.on_language_selected, id=101)
        self.Bind(wx.EVT_MENU, self.on_language_selected, id=102)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        canvas_plot_sizer = wx.BoxSizer(wx.VERTICAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer0 = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        # Initialise some empty matplotlib figure
        self.configure_matplotlib_canvas()
        self.matplotlib_canvas = FigureCanvas(self, -1, self.figure)
        self.legend = None

        # Arrange sizers, all stemming from main sizer
        canvas_plot_sizer.Add(self.canvas, 40, wx.EXPAND | wx.ALL, 1)
        canvas_plot_sizer.Add(self.matplotlib_canvas, 20, wx.EXPAND | wx.ALL, 1)
        canvas_plot_sizer.Add(self.scroll_bar, 1, wx.EXPAND | wx.ALL, 1)

        main_sizer.Add(canvas_plot_sizer, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(button_sizer1, 1, wx.EXPAND | wx.ALL, 5)
        side_sizer.Add(button_sizer2, 1, wx.EXPAND | wx.ALL, 5)
        side_sizer.Add(button_sizer0, 1, wx.EXPAND | wx.ALL, 5)
        side_sizer.Add(self.text_box, 15, wx.EXPAND | wx.ALL, 5) # expanding text box
        side_sizer.Add(self.clear_button, 1, wx.EXPAND | wx.ALL, 5)
        side_sizer.Add(self.switch_to_3D_button, 1, wx.EXPAND | wx.ALL, 5)
        side_sizer.Add(self.message_display, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer0.Add(self.zap_monitor_button, 1, wx.ALL, 1) 
        button_sizer0.Add(self.add_monitor_button, 1, wx.ALL, 1)
        button_sizer2.Add(self.continue_button, 1, wx.ALL, 1)
        button_sizer2.Add(self.run_button, 1, wx.ALL, 1)
        button_sizer1.Add(self.reset_view_button, 1, wx.ALL, 1)
        button_sizer1.Add(self.reset_plot_button, 1, wx.ALL, 1)

        # Set minimum window size and make main_sizer parent sizer
        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)
    
    def draw_canvas_to_3D(self, event): 
        self.is3D = self.switch_to_3D_button.GetValue()
        
        if self.is3D:

            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            GL.glFlush()

            self.zap_monitor_button.SetValue(False)
            self.add_monitor_button.SetValue(False)
            self.zap_monitor_button.Disable()
            self.add_monitor_button.Disable()

            self.canvas.Destroy()
            self.matplotlib_canvas.Destroy()

            self.canvas = MyGLCanvas3D(self, self.devices, self.monitors)
            self.matplotlib_canvas = MyGLCanvasMonitor3D(self, self.devices, self.monitors)

            main_sizer = self.GetSizer()
            canvas_plot_sizer = main_sizer.GetChildren()[0].GetSizer()

            canvas_plot_sizer.Clear(delete_windows=False)
            canvas_plot_sizer.Add(self.canvas, 40, wx.EXPAND | wx.ALL, 1)
            canvas_plot_sizer.Add(self.matplotlib_canvas, 20, wx.EXPAND | wx.ALL, 1)
            canvas_plot_sizer.Add(self.scroll_bar, 1, wx.EXPAND | wx.ALL, 1)

            self.update_scroll()
            # Refresh the layout
            main_sizer.Layout()

        else: 
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            GL.glFlush()

            self.canvas.Destroy()
            self.matplotlib_canvas.Destroy()

            self.zap_monitor_button.Enable()
            self.add_monitor_button.Enable()
            self.zap_monitor_button.SetValue(False)
            self.add_monitor_button.SetValue(False)
            self.is_zap_monitor = False
            self.is_add_monitor = False

            self.canvas = MyGLCanvas(self, self.devices, self.monitors, self.message_display)
            self.matplotlib_canvas = FigureCanvas(self, -1, self.figure)

            main_sizer = self.GetSizer()
            canvas_plot_sizer = main_sizer.GetChildren()[0].GetSizer()

            canvas_plot_sizer.Clear(delete_windows=False)
            canvas_plot_sizer.Add(self.canvas, 40, wx.EXPAND | wx.ALL, 1)
            canvas_plot_sizer.Add(self.matplotlib_canvas, 20, wx.EXPAND | wx.ALL, 1)
            canvas_plot_sizer.Add(self.scroll_bar, 1, wx.EXPAND | wx.ALL, 1)

            self.update_scroll()
            # Refresh the layout
            main_sizer.Layout()

    def on_scroll(self, event): 

        if not self.is3D: 
        
            max_view = self.max_2D_view
            self.scroll_val = self.scroll_bar.GetThumbPosition()
            self.axes.set_xlim(self.scroll_val, self.scroll_val + max_view)
            self.matplotlib_canvas.draw()
        else: 
            self.scroll_val = self.scroll_bar.GetThumbPosition()
            self.matplotlib_canvas.scroll_val = self.scroll_val
            self.matplotlib_canvas.Refresh()

    def update_scroll(self): 
        if not self.is3D: 
            max_view = self.max_2D_view
            diff = self.cycles_completed - max_view
            if diff < 0: 
                self.scroll_bar.SetScrollbar(0, self.cycles_completed, self.cycles_completed, self.cycles_completed - 1) 
            else: 
                self.scroll_bar.SetScrollbar(diff, max_view, self.cycles_completed, self.cycles_completed - 1)
        else: 
            max_view = self.max_3D_view
            diff = self.cycles_completed - max_view
            if diff < 0: 
                self.scroll_bar.SetScrollbar(0, 10, 10, 9) 
            else: 
                self.scroll_bar.SetScrollbar(self.scroll_val, max_view, self.cycles_completed, self.cycles_completed - 1)

        

    def on_language_selected(self, event):
        language_id = event.GetId()
        if language_id == 101:  # English
            self.change_language('en')
        elif language_id == 102:  # Greek
            self.change_language('el')  # Change 'el' to the appropriate language code for Greek

    def change_language(self, language_code):
        '''Load translations from the compiled .mo file in the current directory'''
        localedir = os.path.join(os.path.dirname(__file__), 'locales')
        print("Changing language,", language_code, "located at", localedir)
        try:
            lang = gettext.translation('logsim', localedir=localedir, languages=[language_code])
            lang.install()
            print(f"Successfully changed language to: {language_code}")
            self.RefreshUI()
        except FileNotFoundError as e:
            if language_code == 'en':
                # English is the default language, no need to panic if it's not found
                print(f"English translations not found, using default language.")
            else:
                print(f"Error: {e}")
                print(f"Ensure that the .mo file exists at: {localedir}\{language_code}\LC_MESSAGES\logsim.mo")
        
    def RefreshUI(self):
        """Re-translate all translatable strings"""
        print("refreshui called")
        # Update labels for all widgets here
        self.text.SetLabel(_("Cycles"))
        self.run_button.SetLabel(_("Run"))
        self.continue_button.SetLabel(_("Continue"))
        self.reset_plot_button.SetLabel(_("Reset Plot"))
        self.zap_monitor_button.SetLabel(_("Zap Monitor"))
        self.add_monitor_button.SetLabel(_("Add Monitor"))
        self.reset_view_button.SetLabel(_("Reset View"))
        self.clear_button.SetLabel(_("Clear Terminal"))
        #self.SetMenuBar(self.GetMenuBar())  # Refresh menu bar
        self.Layout()  # Refresh layout
    
    def configure_matplotlib_canvas(self): 
        """ Sets the config params of the matplotlib canvas"""
        hfont = {'fontname':'Consolas'}
        self.figure = Figure(figsize=(5,2))
        self.axes = self.figure.add_subplot(111)
        self.axes.set_title("Monitor Plots", **hfont)
        self.axes.tick_params(axis = 'both', bottom = True, left = False, right = False, labelright = False, labelleft = False, labelbottom = True)

    def execute_circuit(self, cycles): 
        """Simulates the circuit for N cycles"""
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                wx.LogError(_("Error! Network oscillating."))
                return False
        return True
    
    def run_circuit(self, cycles): 
        self.cycles_completed = 0
        self.monitors.reset_monitors()
        self.devices.cold_startup()

        self.update_scroll()

        if self.execute_circuit(cycles): 
            self.cycles_completed += cycles
            return True
        return False 
    
    def continue_circuit(self, cycles):
        """Continues the simulation for N cycles"""
        if self.cycles_completed == 0: 
            wx.LogError(_("Nothing to continue - run the simulation first"))
            return False 
        elif self.execute_circuit(cycles): 
            self.cycles_completed += cycles
            self.update_scroll()
            return True 
        return False

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(
            _(f"Logic Simulator for GF2P2\n"
            f"Created by Mojisola Agboola, 2017\n"
            f"Modified by Anirudh Bhalekar, Moses Liew, Shawn Li, 2024"),
            _("About Logsim"),
            wx.ICON_INFORMATION | wx.OK
            )
        if Id == wx.ID_EDIT:
            
            if self.editor and self.editor.IsShown():
                # If the editor is already open and visible, just bring it to front
                self.editor.Raise()
            else:
                # Otherwise, open and create the editor
                self.open_text_editor()
                #self.editor = TextEditor(self, "Text Editor")
                #self.editor.Bind(wx.EVT_CLOSE, self.on_editor_close)
                #self.editor.Show()
            
        if Id == wx.ID_HELP_COMMANDS:
            wx.MessageBox(_("List of user commands: "
                        "\nr N - run the simulation for N cycles"
                        "\nc N - continue simulation for N cycles"
                        "\ns X N - set switch X to N (0 or 1)"
                        "\nm X - set a monitor on signal X"
                        "\nz X - zap the monitor on signal X"
                        "\nh - print a list of available commands on the terminal"
                        "\nq - quit the simulation"))
        if Id == wx.ID_OPEN:
            with wx.FileDialog(self,  _("Open New Source File"),
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
                        self.on_reset_plot_button(None)
                        self.canvas.Destroy()  # Destroy the old canvas
                        
                        if self.is3D: 
                            self.canvas = MyGLCanvas3D(self, self.devices, self.monitors)
                            self.matplotlib_canvas = MyGLCanvasMonitor3D(self, self.devices, self.monitors)
                        else: 
                            self.canvas = MyGLCanvas(self, self.devices, self.monitors, self.message_display)
                            self.matplotlib_canvas = FigureCanvas(self, -1, self.figure)

                        # Update the layout to replace the old canvas with the new one
                        main_sizer = self.GetSizer()
                        canvas_plot_sizer = main_sizer.GetChildren()[0].GetSizer()

                        # Remove the old canvas and add the new one
                        canvas_plot_sizer.Clear(delete_windows=False)
                        canvas_plot_sizer.Add(self.canvas, 40, wx.EXPAND | wx.ALL, 1)
                        canvas_plot_sizer.Add(self.matplotlib_canvas, 20, wx.EXPAND | wx.ALL, 1)
                        canvas_plot_sizer.Add(self.scroll_bar, 1, wx.EXPAND | wx.ALL, 1)

                        # Refresh the layout
                        main_sizer.Layout()

                        # Print the name of the file opened to the terminal (text box) window
                        wx.MessageBox(_(" Opened file:"), pathname)
                    else: 
                        #print(self.parser.parse_network())
                        num_errors = self.parser.error_count + 1

                        wx.MessageBox(_("Error! Faulty definition file!") + "\n\n" +
                        _("{num_errors} errors caught").format(num_errors=num_errors))

                except Exception as ex:
                    wx.LogError(_("Cannot open file: {exception}").format(exception=ex))

        if Id == wx.ID_PREFERENCES: 
            with wx.TextEntryDialog(self, "Change Value of 3D max view", value = str(self.max_3D_view)) as text_dialog: 
                if text_dialog.ShowModal() == wx.ID_OK: 
                    try:
                        val = int(str(text_dialog.GetValue()))
                        if val > 20: 
                            self.max_3D_view = val
                        else: 
                            wx.LogError("Value must be greater than 20")
                    except: 
                        wx.LogError("Incorrect data type! Not saved")
        if Id == wx.ID_APPLY: 
            with wx.TextEntryDialog(self, "Change Value of 2D max view", value = str(self.max_2D_view)) as text_dialog: 
                if text_dialog.ShowModal() == wx.ID_OK: 
                    try:
                        val = int(str(text_dialog.GetValue()))
                        if val > 20: 
                            self.max_3D_view = val
                        else: 
                            wx.LogError("Value must be greater than 20")
                    except: 
                        wx.LogError("Incorrect data type! Not saved")


    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        self.cycle_count = spin_value
        
        text = "".join([_("New spin control value: "), str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""

        text = _("Run button pressed, {cycle_count} cycles.").format(cycle_count=self.cycle_count)
        
        if not self.is3D: 
            if self.cycles_completed > self.max_total: 
                wx.LogError("Max cycle count exceeded! Refresh the plot or edit the source data")
                return 
            self.run_circuit(self.cycle_count)
            self.canvas.render(text)

            try: 
                self.monitor_plot()
            except Exception: 
                self.on_reset_plot_button(None)
                wx.LogError(_("Run failed - cannot plot monitors"))
        
        else: 
            if self.cycles_completed > self.max_total: 
                wx.LogError("Max cycle count exceeded! Refresh the plot or edit the source data")
                return 
            self.run_circuit(self.cycle_count)
            self.matplotlib_canvas.initialise_monitor_plots()
            self.matplotlib_canvas.Refresh()

    
    def on_reset_plot_button(self, event): 
        """Clears the matplotlib plot"""
        
        self.monitors.reset_monitors()
        
        if not self.is3D: 
            hfont = {'fontname':'Consolas'}
            
            self.axes.clear()
            self.axes.set_title(_("Monitor Plots"), **hfont)
            
            try: 
                self.legend.remove()
            except: 
                pass

            self.matplotlib_canvas.draw()
            self.plot_array = []
            self.name_array = []

            self.cycles_completed = 0
            self.update_scroll()
            
            text = _("Reset plot button pressed.")
            self.canvas.render(text)
        
        else: 
            self.plot_array = []
            self.name_array = []
            self.cycles_completed = 0
            self.update_scroll()
            self.matplotlib_canvas.initialise_monitor_plots()
            self.matplotlib_canvas.Refresh()


    def on_zap_button(self, event): 
        """Starts zap procedure"""
        if self.add_monitor_button.GetValue(): 
            self.add_monitor_button.SetValue(False) 

        self.is_add_monitor = self.add_monitor_button.GetValue()
        self.is_zap_monitor = self.zap_monitor_button.GetValue()

    def on_add_button(self, event): 
        """Start add procedure"""
        if self.zap_monitor_button.GetValue(): 
            self.zap_monitor_button.SetValue(False)

        self.is_add_monitor = self.add_monitor_button.GetValue()
        self.is_zap_monitor = self.zap_monitor_button.GetValue()

    def on_continue_button(self, event): 
        """Handle continue button event"""
        text = _("Continue button pressed, {cycle_count} cycles.").format(cycle_count=self.cycle_count)

        if self.cycles_completed > self.max_total: 
            wx.LogError("Max cycle count exceeded! Refresh the plot or edit the source data")
            return 
        
        if not self.is3D: 
            self.continue_circuit(self.cycle_count)
            self.canvas.render(text)

            if self.cycles_completed == 0: 
                wx.LogError(_("Nothing to Continue - try running the simulation first"))
                return
            try: 
                self.monitor_plot()
            except Exception: 
                self.on_reset_plot_button(None)
                wx.LogError(_("Run failed - cannot plot monitors"))
        else: 
            if self.cycles_completed == 0: 
                wx.LogError(_("Nothing to Continue - try running the simulation first"))
                return
            self.continue_circuit(self.cycle_count)
            self.matplotlib_canvas.initialise_monitor_plots()
            self.matplotlib_canvas.Refresh()
    
    def change_switch_state(self, switch_name, switch_id, value): 
        
        bool_switch = False
        if switch_id is None: 
            # literally the first time I've ever used query from names -_-
            switch_id = self.names.query(switch_name)
        switch_device = self.devices.get_device(switch_id)
        
        if switch_device is not None and switch_device.device_kind == self.devices.SWITCH: 
            bool_switch = self.devices.set_switch(switch_id, value)
            self.Refresh()
        else: 
            wx.LogError(_("Invalid Device Type"))
        
        if not bool_switch: 
            wx.LogError(_("Invalid Device Type"))

        return bool_switch
    
    def add_monitor_with_name(self, m_string: str):
        
        bool_add_mon = False
        string_array = m_string.split('.')

        dev_name = string_array[0]
        dev_id = self.names.query(dev_name)

        port_id = None

        if len(string_array) > 1: 
            port_name = string_array[1]
            port_id = self.names.query(port_name)
        
        try: 
            bool_add_mon = self.monitors.make_monitor(dev_id, port_id, self.cycles_completed)
            self.Refresh()
        except: 
            wx.LogError(_("Monitor addition error"))
        
        return bool_add_mon
    
    def del_monitor_with_name(self, m_string: str):
        string_array = m_string.split('.')

        dev_name = string_array[0]
        dev_id = self.names.query(dev_name)

        port_id = None

        if len(string_array) > 1: 
            port_name = string_array[1]
            port_id = self.names.query(port_name)
        
        try: 
            bool_del_mon = self.monitors.remove_monitor(dev_id, port_id)
            self.Refresh()
        except: 
            wx.LogError(_("Monitor addition error"))
        
        return bool_del_mon

    def monitor_plot(self):
        
        hfont = {'fontname':'Consolas'}
        self.axes.clear()
        self.axes.set_title(_("Monitor Plots"), **hfont)
        try: self.legend.remove()
        except: pass
        self.matplotlib_canvas.draw()
        
        self.plot_array = []
        self.name_array = []

        for device_id, output_id in self.monitors.monitors_dictionary: 

            one_d_signal = []
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            for signal in signal_list: 
                if signal == self.devices.HIGH: 
                    one_d_signal.append(1)
                if signal == self.devices.LOW: 
                    one_d_signal.append(0)
                if signal == self.devices.RISING: 
                    one_d_signal.append(0.5)
                if signal == self.devices.FALLING: 
                    one_d_signal.append(0.5)
                if signal == self.devices.BLANK: 
                    one_d_signal.append(np.nan)
            
            self.plot_array.append(one_d_signal)
            self.name_array.append(monitor_name)
        
        for i, int_signal in enumerate(self.plot_array): 

            name = self.name_array[i]
            tick_array = list(np.linspace(0, self.cycles_completed, self.cycles_completed))
            int_signal = np.array(int_signal) + 2*i

            if len(int_signal) < self.cycles_completed:
                temp_signal = np.empty(self.cycles_completed)
                temp_signal[:] = np.nan
                temp_signal[self.cycles_completed - len(int_signal):] = int_signal
                int_signal = temp_signal
            
            zero_signal = np.zeros_like(int_signal) + 2*i
            sig_plot = self.axes.plot(tick_array, int_signal, label = name)
            sig_base = self.axes.plot(tick_array, zero_signal, color = 'black', linestyle = "dashed") 
        
        self.axes.set_ylim(0, 2*i + 2)
        self.axes.set_xlim(max(self.cycles_completed - self.max_2D_view, 0), self.cycles_completed - 1)
        prop={'family':'Consolas', 'size':8}
        self.legend = self.figure.legend(fontsize="8", loc ="upper left", prop = prop)

        self.matplotlib_canvas.draw()

    def on_clear_button(self, event):
        """Handle the event when the user clicks the clear button."""
        text = _("Clear button pressed.")
        self.canvas.render(text)
        self.text_box.SetValue("> ")  # Clear the text box and add prompt

    def on_reset_view_button(self, event):
        """Handle the event when the user clicks the reset view button."""
        text = _("Reset view button pressed")
        self.canvas.render(text)
        self.canvas.reset_view()

    def open_text_editor(self):
        """Handle the event when the text editor is opened."""
        self.editor = TextEditor(self, "Text Editor", self.path)
        self.editor.Bind(wx.EVT_CLOSE, self.on_editor_close)
        self.editor.Show()

    def on_editor_close(self, event):
        """Handle the event when the text editor is closed."""
        self.editor.Destroy()
        self.editor = None

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        
        # Get the entered text, current line only
        text = self.text_box.GetValue().strip()
        lines = text.split('\n')
        #print(lines)
        # Get the most recent line of input, excluding the > at the bottom, hence index is -2 in win and -1 else
        if len(lines) == 1:
            current_line = lines[0].strip()
        else:
            if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                current_line = lines[-1].strip()
            else:
                current_line = lines[-2].strip()
        #print(lines)
        #print(current_line)
        if current_line[0] == '>':
            current_line = current_line[1:].strip()
        text = current_line # should be without the initial >
        #print(text, "is current line")

        # The problem is after the first enter, text will still start with '> '. And it cannot be removed for some reason. Probs because  of the way promptedtextctrl is defined.
        # Parse the user's input and call the corresponding functions from UserInterface
        if text.startswith('r ') or text.startswith('run '):
            # Run simulation for N cycles
            try:
                N = int(text[2:].strip())
                self.run_circuit(N)
                
                try: 
                    self.monitor_plot()
                except Exception: 
                    self.on_reset_plot_button(None)
                    wx.LogError(_("Run failed - cannot plot monitors"))
                
                if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                    self.text_box.AppendText("\n")
                self.text_box.AppendText(_("Running simulation for {cycles} cycles.\n").format(cycles=N))
                
            except ValueError:
                if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                    self.text_box.AppendText("\n")
                self.text_box.AppendText(_("Invalid command. Please provide a valid number of cycles.\n"))
        elif text.startswith('c ') or text.startswith('continue '):
            # Continue the simulation for N cycles
            try:
                N = int(text[2:].strip())
                bool_cont = self.continue_circuit(N)
                # If True (continuing circuit doesn't give error)
                if bool_cont:
                    try: 
                        self.monitor_plot()
                    except Exception: 
                        self.on_reset_plot_button(None)
                        wx.LogError(_("Run failed - cannot plot monitors"))

                    if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                        self.text_box.AppendText("\n")
                    self.text_box.AppendText(_("Continuing simulation for {cycles} cycles.\n").format(cycles=N))
                else:
                    if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                        self.text_box.AppendText("\n")
                    self.text_box.AppendText(_(f"Nothing to continue - run the simulation first.\n"))
            except ValueError:
                if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                    self.text_box.AppendText("\n")
                self.text_box.AppendText(_("Invalid command. Please provide a valid number of cycles.\n"))
        elif text.startswith('s '):
            # Set switch X to N (0 or 1)
            try:
                switch_name, value = text[2:].strip().split()
                value = int(value)
                
                if type(value) != int or value not in [0, 1]:
                    if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                        self.text_box.AppendText("\n")
                    self.text_box.AppendText(_("Switch value must be 0 or 1\n"))
                    raise ValueError(_("Switch value must be 0 or 1"))
                
                bool_switch = self.change_switch_state(switch_name, None, value)
                if not bool_switch: 
                    wx.LogError(_("Switch set failed"))
                if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                        self.text_box.AppendText("\n")
                self.text_box.AppendText(_("Setting switch {switch_name} to {value}.\n").format(switch_name=switch_name, value=value))
            except ValueError:
                if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                        self.text_box.AppendText("\n")
                self.text_box.AppendText(_("Invalid command format. Please provide switch ID and value.\n"))
        elif text.startswith('m ') or text.startswith('monitor '):
            # Add a monitor on signal X
            signal = text[2:].strip()

            bool_add_mon = self.add_monitor_with_name(signal) 
            if bool_add_mon:
                if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                    self.text_box.AppendText("\n")
                self.text_box.AppendText(_("Adding monitor on signal {signal}.\n").format(signal=signal))
            else: 
                if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                    self.text_box.AppendText("\n")
                self.text_box.AppendText(_("Monitor addition failed for signal {signal}.\n").format(signal=signal))

        elif text.startswith('z ') or text.startswith('zap '):
            # Zap the monitor on signal X
            signal = text[2:].strip()

            bool_del_mon = self.del_monitor_with_name(signal) 

            if bool_del_mon:
                if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                    self.text_box.AppendText("\n")
                self.text_box.AppendText(_("Zapping monitor on signal {signal}.\n").format(signal=signal))
            else: 
                if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                    self.text_box.AppendText("\n")
                self.text_box.AppendText(_("Monitor zap failed for signal {signal}.\n").format(signal=signal))
        elif text == 'h' or text == 'help':
            # Print a list of available commands to console
            if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                self.text_box.AppendText("\n")
            self.text_box.AppendText(_(
                "List of available commands:\n"
                "r N       - run the simulation for N cycles\n"
                "c N       - continue the simulation for N cycles\n"
                "s X N     - set switch X to N (0 or 1)\n"
                "m X       - add a monitor on signal X\n"
                "z X       - zap the monitor on signal X\n"
                "h         - print a list of available commands\n"
                "q         - quit the program\n"
            ))
        elif text == 'q' or text == 'quit':
            # Quit the program
            self.Close()
        else:
            # Invalid command
            if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                self.text_box.AppendText("\n")
            self.text_box.AppendText(_("<{text}> is an invalid command. A list of available commands can be obtained by entering 'h', or navigating to 'Commands' in the Menu.\n").format(text=text))

"""class RunApp(wx.App): 
    # Combines Canvas onto App with Matplotlib
    def __init__(self):
        
        GLUT.glutInit()
        GLUT.glutInitDisplayMode(GLUT.GLUT_DOUBLE | GLUT.GLUT_RGBA)
        GLUT.glutCreateWindow("Logsim 2.0")
        GLUT.glutOverlayDisplayFunc(self.show_frame)
        GLUT.glutMainLoop()
        
        return True
    
    def show_frame(self): 
        print("IRHBIERUJBVIEJBVIERJB")
        frame = wx.Frame(None, -1, 'OpenGL App', size=(400, 400))
        canvas = MyGLCanvas(frame)
        frame.Show(True)"""

        