import math
import numpy as np
from OpenGL.GL import GL_LINE_STRIP, GL_LINE_LOOP, GL_POLYGON, GL_ENABLE_BIT, GL_LINE_STIPPLE
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, glPushAttrib, glLineStipple, glPopAttrib, glEnable
from OpenGL import GL, GLUT


class LogicDrawer3D: 
    
    def __init__(self, names, devices, monitors, id, n_iter=10) -> None:
        
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.id = id

        self.n_iter = n_iter


        self.operator_height = 30 # Z direction

        try: 
            self.device = self.devices.get_device(self.id) # This is the device obj 

            self.device_inputs = self.device.inputs
            self.device_outputs = self.device.outputs

            self.n_inputs = len(self.device_inputs.keys())
        
        except: 
            pass 


        self.input_dict = {}
        self.output_dict = {}
        self.monitor_dict = {}

        # Thankfully with the infinite possibilities that the 3rd dimension adds,
        # a domain list is not necessary, we add it here anyway

        # UPDATE - it was necessary my bad gang

        self.domain = []

        self.y_plane_coord = -6

    
    def draw_flat_surface(vertex_list : list): 

        # find normal of surface: 

        assert len(vertex_list) == 3

        # We only need 3 points to define a plane, define them going counter clockwise 


    def draw_cuboid(self, x_pos, z_pos, half_width, half_depth, height):

        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord, z_pos + half_depth)
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord + height, z_pos + half_depth)
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord + height, z_pos + half_depth)
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord, z_pos + half_depth)
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord, z_pos - half_depth)
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord + height, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, self.y_plane_coord, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, self.y_plane_coord + height, z_pos + half_depth)
        GL.glEnd()
    
    def draw_cylinder(self, center_x, center_z, radius, height, num_slices):
        r = radius
        h = height + 1
        n = float(num_slices)

        y = self.y_plane_coord -1

        circle_pts = []
        for i in range(int(n) + 1):
            angle = 2 * math.pi * (i/n)
            x = r * math.cos(angle) + center_x
            z = r * math.sin(angle) + center_z
            pt = (x, z)
            circle_pts.append(pt)

        glBegin(GL.GL_TRIANGLE_FAN)#drawing the back circle
        
        GL.glVertex(center_x, y, center_z)
        for (x, z) in circle_pts:
            GL.glVertex(x, y, z)
        glEnd()

        glBegin(GL.GL_TRIANGLE_STRIP)#draw the tube
        for (x, z) in circle_pts:
            GL.glVertex(x, y + height, z)
            GL.glVertex(x, y, z)
        glEnd()

        glBegin(GL.GL_TRIANGLE_FAN)#drawing the front circle
        GL.glVertex(center_x, y + height, center_z)
        for (x, z) in circle_pts:
            GL.glVertex(x, y + height, z)
        glEnd()


    def draw_and_gate(self, x_pos, z_pos): 
        # ALL DEVICES WILL BE DRAWN ON THE SAME Y = -6 plane

        self.x, self.z = x_pos, z_pos
        self.width = 40 
        self.height = 20

        half_depth = self.operator_height / 2
        half_width = self.width / 2

        self.draw_cuboid(self.x, self.z, half_width, half_depth, self.height)
        self.draw_cylinder(self.x + half_width,  self.z, half_depth, self.height, 25)

    def draw_mesh(self, x, z): 

        file_name = "C:/Users/Bhalekar's/Desktop/Part 2A/PROJECTS/DEVICES OBJ/AND.obj"
        mesh = Mesh(filename=file_name, pos_x=x, pos_z=z)

""" MESH CLASS TO IMPORT OBJ FILES AND """

class Mesh: 

    def __init__(self, filename, pos_x, pos_z) -> None:

        self.x = pos_x
        self.z = pos_z
        self.filename = filename

        vertices = self.load_mesh()
        self.vertex_count = len(vertices)//8
        vertices = np.array(vertices, dtype=np.float32)

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        #Vertices
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)
        #position
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 32, GL.ctypes.c_void_p(0))
        #texture
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 32, GL.ctypes.c_void_p(12))

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
                match words[0]:
                    case "v":
                        v.append(self.read_vertex_data(words))
                    case "vt":
                        vt.append(self.read_texcoord_data(words))
                    case "vn":
                        vn.append(self.read_normal_data(words))
                    case "f":
                        self.read_face_data(words, v, vt, vn, vertices)
                
                line = file.readline()

        return vertices

    def read_vertex_data(self, words : list[str]) -> list[float]: 

        return [
                100 * float(float(words[1]) + self.x), 
                100 * float(words[2]), 
                100 * float(float(words[3]) + self.z)
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