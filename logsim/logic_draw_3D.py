import math
import numpy as np
from OpenGL.GL import GL_LINE_STRIP, GL_LINE_LOOP, GL_POLYGON, GL_ENABLE_BIT, GL_LINE_STIPPLE
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, glPushAttrib, glLineStipple, glPopAttrib, glEnable
from OpenGL import GL, GLUT
import os

class LogicDrawer3D: 
    
    def __init__(self, names, devices, monitors, vertex_loader) -> None:
        
        self.scale = 10
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

        self.vertex_loader = vertex_loader # Loads device_kind_pos_x_pos_y to the vertex of said file

        # Thankfully with the infinite possibilities that the 3rd dimension adds,
        # a domain list is not necessary, we add it here anyway

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

    def draw_with_id(self, device_id, x, y): 

        this_device = self.devices.get_device(device_id)
        device_name = self.names.get_name_string(this_device.device_id)
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
        self.render_text(device_name, self.scale * x, self.scale * y, 30)
        glColor3f(0.1, 0.1, 0.1)
        self.draw_mesh(x, y, frame_file_path, str(str(device_id) + "_frame"))

    def draw_mesh(self, x, y, file_name, device_id): 
        mesh = Mesh(file_name, device_id, x, y, self.names, self.devices, self.monitors, self.vertex_loader)
    
    def return_io_list(self, device_id, x, y): 
        """IO list of the object"""

        self.gate_coord_list = [(0, 0.15, 0.5), (0, -0.15, 0.5), 
                                (0, 0.45, 0.5), (0, -0.45, 0.5), 
                                (0, 0.75, 0.5), (0, -0.75, 0.5), 
                                (0, 1.05, 0.5), (0, -1.05, 0.5), 
                                (0, 0.15, -0.5), (0, -0.15, -0.5), 
                                (0, 0.45, -0.5), (0, -0.45, -0.5), 
                                (0, 0.75, -0.5), (0, -0.75, -0.5), 
                                (0, 1.05, -0.5), (0, -1.05, -0.5)]
        
        self.gate_coord_list = [(cx + x, cy + y, cz) for (cx,cy,cz) in self.gate_coord_list]

        this_device = self.devices.get_device(device_id)
        this_device_inputs = this_device.inputs
        this_device_outputs = this_device.outputs
        this_device_kind = self.names.get_name_string(this_device.device_kind)

        if this_device_kind in ["AND", "NAND", "OR", "XOR", "NOR"]: 
            # All these gates have the same make - we can add a max of 16 gates so just 
            # subdivide the space (instead of scaling the 3D model each time)
            for input_id in this_device_inputs.keys(): 
                coord = self.gate_coord_list.pop()
                self.inputs_dict[(device_id, input_id)] = coord
                print(coord)
            for output_id in this_device_outputs.keys(): 
                coord = (4 + x, y, 0)
                self.outputs_dict[(device_id, output_id)] = coord
            
        elif this_device_kind in ["CLOCK", "SWITCH"]: 
            for output_id in this_device_outputs.keys(): 
                self.outputs_dict[(device_id, output_id)] = (x, y, 0)
        
        elif this_device_kind == "RC": 
            for output_id in this_device_outputs.keys(): 
                self.outputs_dict[(device_id, output_id)] = (x + 3, y, 0)

        elif this_device_kind == "DTYPE": 
            for input_id in this_device_inputs.keys(): 
                if input_id == self.devices.CLK_ID: 
                    coord = (x - 2, y - 2, 0)
                elif input_id == self.devices.DATA_ID: 
                    coord = (x - 2, y + 2, 0)
                elif input_id == self.devices.SET_ID: 
                    coord = (x, y + 4, 0)
                else: 
                    coord = (x, y -4, 0)
            
                self.inputs_dict[(device_id, input_id)] = coord
            
            for output_id in this_device_outputs.keys():
                if output_id == self.devices.Q_ID: 
                    coord = (x + 2, y + 2, 0)
                else: 
                    coord = (x + 2, y - 2, 0)
                
                self.outputs_dict[(device_id, output_id)] = coord


""" MESH CLASS TO IMPORT OBJ FILES AND """
"""Courtesy of GetIntoGameDev - on YouTube, whose skeleton I used after reading 
    his tutorial on PyOpenGL and lighting, and made some modifications to"""

class Mesh(LogicDrawer3D): 

    def __init__(self, filename, device_id, pos_x, pos_y, names, devices, monitors, vertex_loader) -> None:
        
        super().__init__(names, devices, monitors, vertex_loader)
        
        self.x = pos_x
        self.y = pos_y
        self.filename = filename

        vertices = None

        try: 
            str_id = str(device_id)
            parent_dict = dict(self.vertex_loader)
            vertices = parent_dict[str_id]
        except Exception as ex: 
            pass

        if vertices is None: 
            vertices = self.load_mesh()
            str_id = str(device_id)
            self.vertex_loader[str_id] =  vertices

        vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = len(vertices)//8

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

