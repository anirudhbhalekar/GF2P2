import math
import numpy as np
from OpenGL.GL import GL_LINE_STRIP, GL_LINE_LOOP, GL_POLYGON, GL_ENABLE_BIT, GL_LINE_STIPPLE
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, glPushAttrib, glLineStipple, glPopAttrib, glEnable
from OpenGL import GL, GLUT
import os

class ConnectDrawer3D: 

    def __init__(self, names, devices, monitors, network, inputs_dict, outputs_dict) -> None:

        self.names = names 
        self.devices = devices 
        self.network = network 
        self.monitors = monitors
        self.inputs_dict = inputs_dict
        self.outputs_dict = outputs_dict
        num_inputs = len(self.inputs_dict.keys())
        self.tube_width = 0.2    
        self.z_offsets = range(2, num_inputs + 3)
        self.scale = 1

    def return_tube_vertices(self, curr_coords, dest_coords) -> list: 

        half_width = self.tube_width / 2
        direction_vector = np.array(dest_coords) - np.array(curr_coords)
        # Someone find a smarter way to do this because idk 
        index = np.argmax(np.abs(direction_vector))

        if index == 0: 
            # We are moving along x direction
            if direction_vector[0] < 0: 
                dx = -1
            else: 
                dx = 1

            dest_face_coords = [(dest_coords[0], dest_coords[1] + half_width, dest_coords[2] - half_width), 
                                (dest_coords[0], dest_coords[1] - half_width, dest_coords[2] - half_width), 
                                (dest_coords[0], dest_coords[1] - half_width, dest_coords[2] + half_width),
                                (dest_coords[0], dest_coords[1] + half_width, dest_coords[2] + half_width)]

            src_face_coords  = [(curr_coords[0], curr_coords[1] + half_width, curr_coords[2] - half_width), 
                                (curr_coords[0], curr_coords[1] - half_width, curr_coords[2] - half_width), 
                                (curr_coords[0], curr_coords[1] - half_width, curr_coords[2] + half_width),
                                (curr_coords[0], curr_coords[1] + half_width, curr_coords[2] + half_width)]
            
            n1 = [dx, 0, 0]
            n2 = [-dx, 0, 0]
            n3 = [0,1, 0]
            n4 = [0,-1, 0]
            n5 = [0,0,1]
            n6 = [0,0,-1]
        
        elif index == 1: 
            # Moving in the y direction
            if direction_vector[1] < 0: 
                dy = -1
            else: 
                dy = 1
            dest_face_coords = [(dest_coords[0] + half_width, dest_coords[1], dest_coords[2] - half_width), 
                                (dest_coords[0] - half_width, dest_coords[1], dest_coords[2] - half_width), 
                                (dest_coords[0] - half_width, dest_coords[1], dest_coords[2] + half_width),
                                (dest_coords[0] + half_width, dest_coords[1], dest_coords[2] + half_width)]
 
            src_face_coords  = [(curr_coords[0] + half_width, curr_coords[1], curr_coords[2] - half_width), 
                                (curr_coords[0] - half_width, curr_coords[1], curr_coords[2] - half_width), 
                                (curr_coords[0] - half_width, curr_coords[1], curr_coords[2] + half_width),
                                (curr_coords[0] + half_width, curr_coords[1], curr_coords[2] + half_width)]

            n1 = [0, dy, 0]
            n2 = [0, -dy, 0]
            n3 = [1, 0, 0]
            n4 = [-1, 0, 0]
            n5 = [0, 0, 1]
            n6 = [0, 0, -1]

        else: 
            # Moving in the z direction 
            if direction_vector[2] < 0: 
                dz = -1
            else: 
                dz = 1
            dest_face_coords = [(dest_coords[0] + half_width, dest_coords[1] - half_width, dest_coords[2]), 
                                (dest_coords[0] - half_width, dest_coords[1] - half_width, dest_coords[2]), 
                                (dest_coords[0] - half_width, dest_coords[1] + half_width, dest_coords[2]),
                                (dest_coords[0] + half_width, dest_coords[1] + half_width, dest_coords[2])]

            src_face_coords  = [(curr_coords[0] + half_width, curr_coords[1] - half_width, curr_coords[2]), 
                                (curr_coords[0] - half_width, curr_coords[1] - half_width, curr_coords[2]), 
                                (curr_coords[0] - half_width, curr_coords[1] + half_width, curr_coords[2]),
                                (curr_coords[0] + half_width, curr_coords[1] + half_width, curr_coords[2])]

            n1 = [0,0,dz]
            n2 = [0,0,-dz]
            n3 = [1,0,0]
            n4 = [-1,0,0]
            n5 = [0,1,0]
            n6 = [0,-1,0]

        f1 = [0,1,2,3]
        f2 = [4,5,6,7]
        f3 = [1,5,6,2]
        f4 = [0,3,7,4]
        f5 = [2,6,7,3]
        f6 = [0,4,5,1]

        face_list = [f1, f2, f3, f4, f5, f6]
        normals_list = [n1, n2, n3, n4, n5, n6]
        vertex_list = list(dest_face_coords + src_face_coords)
        vertices = []

        # need to circle around the vertices and form face coords with normals

        for i, face in enumerate(face_list):
            face_normal = normals_list[i]
            for index in face: 
                vertex = vertex_list[index]
                vertices.append(vertex[0])
                vertices.append(vertex[1])
                vertices.append(vertex[2])
                vertices.append(0.5)
                vertices.append(0.5)
                vertices.append(face_normal[0])
                vertices.append(face_normal[1])
                vertices.append(face_normal[2])

        return list(vertices)
    
    def make_all_connections(self): 
        """Returns a list of vertices for ALL connections 
        (in the form (x, y, z, tex_coord tex_coord, n_x, n_y, n_z))
        * tex coord is irrelevant"""

        vertices = []
        count = 0
        for device in self.devices.devices_list: 
            device_id = device.device_id            
            for input_id in device.inputs.keys(): 
                
                this_vertices = []
                z_offset = self.z_offsets[count]
                is_top = False
                is_bot = False

                if input_id == self.devices.SET_ID: 
                    is_top = True
                elif input_id == self.devices.CLEAR_ID: 
                    is_bot = True
    
                con_tuple = device.inputs[input_id]

                try: 
                    output_dev_id = con_tuple[0]
                    output_port_id = con_tuple[1]
                except: 
                    continue

                input_coords = self.inputs_dict[(device_id, input_id)]
                output_coords = self.outputs_dict[(output_dev_id, output_port_id)]

                if output_coords is not None: 
                    this_vertices = self.make_single_connection(input_coords=input_coords, output_coords=output_coords, 
                                                            z_offset=z_offset, is_input_top=is_top, is_input_bot=is_bot)
                    count += 1
    
                vertices += this_vertices
                
        return vertices

    def make_single_connection(self, input_coords, output_coords, z_offset, is_input_top: bool = False, is_input_bot: bool = False): 

        """ 
            Will do connections in 6 stages: 

            1: Jut out of input either to the left (most inputs), or top/bottom (for reset and set)
            2: Go to the z offset (unique for each input)
            3: Travel to the x coord of the end point (with a slight offset to the right)
            4: Travel to the y coord of the end point
            5: Travel to z = 0 (back to where we started)
            6: Remove x offset by going left (to the end point)
            
        """

        if is_input_top: 
            # Input is at the top
            next_coord = (input_coords[0], input_coords[1] + 2, input_coords[2])
            pass
        elif is_input_bot: 
            # Input at the bottom 
            next_coord = (input_coords[0], input_coords[1] - 2, input_coords[2])
        else: 
            next_coord = (input_coords[0] - 2.5, input_coords[1], input_coords[2])

        if output_coords[2] < 0: 
            z_offset = - z_offset

        vertices = []
        vertices += self.return_tube_vertices(input_coords, next_coord)
        
        curr_coord = next_coord
        next_coord = (next_coord[0], next_coord[1], next_coord[2] + z_offset)

        vertices += self.return_tube_vertices(curr_coord, next_coord)

        curr_coord = next_coord
        next_coord = (output_coords[0] + 2.5, next_coord[1], next_coord[2])

        vertices += self.return_tube_vertices(curr_coord, next_coord)

        curr_coord = next_coord
        next_coord = (next_coord[0], output_coords[1], next_coord[2])

        vertices += self.return_tube_vertices(curr_coord, next_coord)

        curr_coord = next_coord
        next_coord = (next_coord[0], next_coord[1], output_coords[2])

        vertices += self.return_tube_vertices(curr_coord, next_coord)

        curr_coord = next_coord
        next_coord = (next_coord[0] - 2.5, next_coord[1], next_coord[2])

        vertices += self.return_tube_vertices(curr_coord, next_coord)

        return vertices

        # we have the input and output ids of two 

    
    def draw_connections(self, vertices : list):
        
        self.deprecated_draw(vertices)

        # REMOVED BECAUSE LINUX IS GARBAGE
        #vertices = np.array(vertices, dtype=np.float32)
        #vertex_count = len(vertices) // 8


        #self.vbo = GL.glGenBuffers(1)
        #GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        #GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)
        ##position
        #GL.glEnableVertexAttribArray(0)
        #GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 32, GL.ctypes.c_void_p(0))
        ##texture
        #GL.glEnableVertexAttribArray(1)
        #GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 32, GL.ctypes.c_void_p(12))

        #GL.glColor3f(0.7, 0.6, 0.1)
        #GL.glDrawArrays(GL.GL_QUADS, 0, vertex_count)

    def deprecated_draw(self, vertices : list) -> None: 
        
        quad_vertices = []
        quad_normals = []

        this_vertex = []
        this_normal = []
        GL.glColor3f(0.5, 0.5, 0.2)
        for index, element in enumerate(vertices): 
            # If the element is in ther 0, 1, 2 position read vertex
            # If the element is in the 5, 6, 7 position read as normal
            if index % 8 < 3: 
                this_vertex.append(element)
            elif index % 8 > 4: 
                this_normal.append(element)
            else: 
                continue
            
            if len(this_normal) == 3: 
                # X, Y, Z has been stored
                quad_vertices.append(tuple(this_vertex))
                quad_normals.append(tuple(this_normal))
                this_vertex.clear()
                this_normal.clear()
            
            #print(triangle_vertices)
            
            if len(quad_normals) == 4: 
                GL.glBegin(GL.GL_QUADS)
                GL.glNormal3f(quad_normals[0][0], quad_normals[0][1], quad_normals[0][2])
                GL.glVertex3f(quad_vertices[0][0], quad_vertices[0][1], quad_vertices[0][2])
                #GL.glNormal3f(triangle_normals[0][0], triangle_normals[0][1], triangle_normals[0][2])
                GL.glVertex3f(quad_vertices[1][0], quad_vertices[1][1], quad_vertices[1][2])
                #GL.glNormal3f(triangle_normals[1][0], triangle_normals[1][1], triangle_normals[1][2])
                GL.glVertex3f(quad_vertices[2][0], quad_vertices[2][1], quad_vertices[2][2])
                #GL.glNormal3f(triangle_normals[2][0], triangle_normals[2][1], triangle_normals[2][2])
                GL.glVertex3f(quad_vertices[3][0], quad_vertices[3][1], quad_vertices[3][2])
                GL.glEnd()
                quad_vertices.clear() 
                quad_normals.clear()