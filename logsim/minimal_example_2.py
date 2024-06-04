import numpy as np
from OpenGL import GLU
from OpenGL.GL import *
from OpenGL.GLUT import *

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

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
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
    
    glutSwapBuffers()

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    GLU.gluPerspective(45.0, width / height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5.0)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"OpenGL Cube Example")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    init()
    glutMainLoop()

if __name__ == "__main__":
    main() 