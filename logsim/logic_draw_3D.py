import math
import numpy as np
from OpenGL.GL import GL_LINE_STRIP, GL_LINE_LOOP, GL_POLYGON, GL_ENABLE_BIT, GL_LINE_STIPPLE
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, glPushAttrib, glLineStipple, glPopAttrib, glEnable
from OpenGL import GL, GLUT
import os

class LogicDrawer3D: 
    
    def __init__(self, names, devices, monitors) -> None:
        
        self.names = names
        self.devices = devices
        self.monitors = monitors

        self.master_obj_folder = "device_objs/"
        self.vertex_folder = "vertices/"


        self.operator_height = 30 # Z direction

        try: 
            self.device = self.devices.get_device(self.id) # This is the device obj 

            self.device_inputs = self.device.inputs
            self.device_outputs = self.device.outputs

            self.n_inputs = len(self.device_inputs.keys())
        
        except: 
            pass 


        self.inputs_dict = {}
        self.outputs_dict = {}
        self.monitors_dict = {}

        self.vertex_loader = {} # Loads device_kind_pos_x_pos_y to the vertex of said file

        # Thankfully with the infinite possibilities that the 3rd dimension adds,
        # a domain list is not necessary, we add it here anyway

        # UPDATE - it was necessary my bad gang

        self.domain = []

        self.y_plane_coord = -6

    def draw_with_id(self, device_id, x, y): 

        this_device = self.devices.get_device(device_id)
        device_kind = self.names.get_name_string(this_device.device_kind)

        obj_file_path = self.master_obj_folder + str(device_kind) + ".obj"
        frame_file_path =  self.master_obj_folder + str(device_kind) + "_frame.obj"
        
        if not os.path.exists(obj_file_path) and not os.path.exists(frame_file_path): 

            raise FileNotFoundError
        
        if device_kind in ["AND", "NAND", "OR", "XOR", "NOR"]:
            glColor3f(0.8, 0.5, 0.1) 
        elif device_kind in ["SWICTH", "CLOCK"]: 
            glColor3f(0.1, 0.8, 0.5)
        else: 
            glColor3f(0.1, 0.5, 0.9)
        
        self.draw_mesh(x, y, obj_file_path, device_id)
        glColor3f(0.1, 0.1, 0.1)
        self.draw_mesh(x, y, frame_file_path, str(str(device_id) + "_frame"))

    def draw_mesh(self, x, y, file_name, device_id): 

        mesh = Mesh(file_name, device_id, x, y, self.names, self.devices, self.monitors)

""" MESH CLASS TO IMPORT OBJ FILES AND """
"""Courtesy of GetIntoGameDev - on YouTube, whose skeleton I used after reading 
    his tutorial on PyOpenGL and lighting, and made some modifications to"""

class Mesh(LogicDrawer3D): 

    def __init__(self, filename, device_id, pos_x, pos_y, names, devices, monitors) -> None:
        
        super().__init__(names, devices, monitors)
        self.scale = 10
        self.x = pos_x
        self.y = pos_y
        self.filename = filename

        vertices = None

        try: 
            str_id = str(device_id)
            vertices = self.vertex_loader[str_id]
        except: 
            pass

        if vertices is None: 
            vertices = self.load_mesh()

        vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = len(vertices)//8
        
        str_id = str(device_id)
        self.vertex_loader[str_id] = vertices

        self.vao = GL.glGenVertexArrays(1)
        #GL.glColor3f(0.7, 0.5, 0.1)
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

