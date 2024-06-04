
import wx
import wx.glcanvas as wxcanvas
from OpenGL import platform
import numpy as np
import math
from OpenGL import GL, GLU, GLUT


class TESTGUI(wx.Frame):
    """Configure the main window and all the widgets.

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

    def __init__(self, title):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        self.canvas = TestCanvas(self)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        side_sizer.Add(self.text_box, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        self.canvas.render()

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        self.canvas.render()

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        self.canvas.render()


class TestCanvas(wxcanvas.GLCanvas):
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

    def __init__(self, parent):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
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
        self.parent = parent

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000
        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        self.vertex_loader = {}

    def init_gl(self):
        """Configure and initialise the OpenGL context."""

        if not self.init:
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
            GL.glTranslatef(0.0, 0.0, -self.depth_offset)

            # Modelling transformation - pan, zoom and rotate
            GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
            GL.glMultMatrixf(self.scene_rotate)
            GL.glScalef(self.zoom, self.zoom, self.zoom)
       
            self.init = True
       
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.test_render()
        GL.glFlush()
        self.SwapBuffers()
   
    def test_render(self):
        TestMesh("device_objs/AND.obj", self.vertex_loader, 1)

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        self.init_gl()

        # Clear everything
       
       
    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        self.init_gl()

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
       

class TestMesh():

    def __init__(self, filename, vertex_loader, device_id) -> None:
       
        self.x = 0
        self.y = 0
        self.filename = filename
        self.scale = 1
        self.vertex_loader = vertex_loader
       
        vertices = None

        try:
            str_id = str(device_id)
            parent_dict = self.vertex_loader
            if str_id not in parent_dict: 
                pass
            else: 
                vertices = parent_dict[str_id]
        except KeyError:
            pass

        if vertices is None:
            vertices = self.load_mesh()
            str_id = str(device_id)
            self.vertex_loader[str_id] =  vertices

        vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = len(vertices)//8

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        #Vertices
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)
        #position
        GL.GL_CONTEXT_FLAG_NO_ERROR_BIT = True
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 32, GL.ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)
        #self.brute_force(vertices)
        self.draw()

    def load_mesh(self) -> list[float]:
   
        v = []
        vt = []
        vn = []
        vertices = []

        with open(self.filename, "r") as file:
            line = file.readline()
            while line:
                words = line.split(" ")
                if words[0] == "v":
                    v.append(self.read_vertex_data(words))
                elif words[0] == "vt":
                    vt.append(self.read_texcoord_data(words))
                elif words[0] == "vn":
                    vn.append(self.read_normal_data(words))
                elif words[0] == "f":
                    self.read_face_data(words, v, vt, vn, vertices)
               
                line = file.readline()

        return vertices

    def read_vertex_data(self, words : list[str]) -> list[float]:

        return [
                self.scale * float(float(words[1]) + self.x),
                self.scale * float(float(words[2]) + self.y),
                self.scale * float(float(words[3]))
        ]

    def read_texcoord_data(self, words: list[str]) -> list[float]:
         return [
                float(words[1]),
                float(words[2])
        ]
   
    def read_normal_data(self, words: list[str]) -> list[float]:
         return [
                float(words[1]),
                float(words[2]),
                float(words[3])
        ]
   
    def read_face_data(self, words: list[float],
                        v  : list[list[float]],
                        vt : list[list[float]],
                        vn : list[list[float]],
                        vertices : list[float]) -> None:

        triangle_count = len(words) - 3

        for i in range(triangle_count):

            self.make_corner(words[1], v, vt, vn, vertices)
            self.make_corner(words[2 + i], v, vt, vn, vertices)
            self.make_corner(words[3 + i], v, vt, vn, vertices)


    def make_corner(self, corner_description: str,
                        v  : list[list[float]],
                        vt : list[list[float]],
                        vn : list[list[float]],
                        vertices : list[float]) -> None:
       
        v_vt_vn = corner_description.split("/") # OBJ splits corners this way

        for element in v[int(v_vt_vn[0]) - 1]:
            vertices.append(element)
        for element in vt[int(v_vt_vn[1]) - 1]:
            vertices.append(element)
        for element in vn[int(v_vt_vn[2]) - 1]:
            vertices.append(element)
       
        # OBJ files store faces in the format a/b/c a'/b'/c' ...
        # for the first element for example, a corresponds to vertex, b to texture coord,
        # c to normal (all are in indices)
   
    def destroy(self):
        GL.glDeleteVertexArrays(1, (self.vao,))
        GL.glDeleteBuffers(1, (self.vbo,))

    def draw(self) -> None:
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.vertex_count)

    def brute_force(self, vertices):

        normal = []
        vertex = []

        all_vertices = []
        all_normals = []
   
        for index, element in enumerate(vertices):
            pos = index % 8
           
            if pos < 3:
                vertex.append(element)
            elif 4 < pos < 8:
                normal.append(element)
            else:
                pass

            all_vertices.append(vertex)
            all_normals.append(normal)
        GL.glBegin(GL.GL_TRIANGLES)
        for vertex, normal in zip(all_vertices, all_normals):
            GL.glVertex3f(vertex[0], vertex[1], vertex[2])
        GL.glEnd()


if __name__ == "__main__":

    app = wx.App()
    gui = TESTGUI("Logic Simulator")
    gui.Show(True)
    app.MainLoop()