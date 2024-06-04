import numpy as np
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL 
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class OpenGLCanvas(wxcanvas.GLCanvas):
    def __init__(self, parent):
        super().__init__(parent, -1, attribList=[wxcanvas.WX_GL_RGBA, wxcanvas.WX_GL_DOUBLEBUFFER, wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.context = wxcanvas.GLContext(self)

    def init_gl(self):
        pass
    def display(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Define the vertices of the cube
        vertices = np.array([
            # Front face
            [-1.0, -1.0,  1.0],
            [ 1.0, -1.0,  1.0],
            [ 1.0,  1.0,  1.0],
            [-1.0,  1.0,  1.0],
            # Back face
            [-1.0, -1.0, -1.0],
            [-1.0,  1.0, -1.0],
            [ 1.0,  1.0, -1.0],
            [ 1.0, -1.0, -1.0]
        ], dtype=np.float32)

        # Define the indices for drawing triangles
        indices = np.array([
            0, 1, 2,  0, 2, 3,  # Front face
            4, 5, 6,  4, 6, 7,  # Back face
            3, 2, 6,  3, 6, 7,  # Top face
            0, 1, 5,  0, 5, 4,  # Bottom face
            0, 3, 7,  0, 7, 4,  # Left face
            1, 2, 6,  1, 6, 5   # Right face
        ], dtype=np.uint32)

        # Define and bind Vertex Array Object (VAO)
        vao_id = glGenVertexArrays(1)
        glBindVertexArray(vao_id)

        # Define and bind Vertex Buffer Object (VBO) for vertices
        vbo_id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_id)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Define and bind Element Buffer Object (EBO) for indices
        ebo_id = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_id)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        # Enable vertex attribute arrays
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Draw the cube
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

        # Clean up
        glDisableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def on_paint(self, event):
        self.SetCurrent(wxcanvas.GLContext(self))
        self.init_gl()
        self.display()
        self.SwapBuffers()

    def on_size(self, event):
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, size.width / size.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="OpenGL Cube in wxPython", size=(800, 600))
        canvas = OpenGLCanvas(self)
        self.Show()

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()