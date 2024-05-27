from math import cos, sin, pi
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINE_STRIP, GL_LINE_LOOP, GL_POLYGON


""" DOC STRING TO BE COMPLETED """


class LogicDrawer:
    """Handle all logic gate drawings."""
    
    def __init__(self, name, x, y, n_iter=10, n_inputs=2, ):
            """Initialize logic drawer with the number of inputs for 
            certain gates and also the number of iterations used to
            draw circles for certain gates."""
            
            # Initialize variables
            self.name = name
            self.x = x
            self.y = y
            self.n_iter = n_iter
            self.n_inputs = n_inputs

            # 2 input gate is 40 high, and every additional input gate adds 5 units of height
            # n_inputs is between 1 and 16, but ONLY 2 for XOR gate. This is checked as a semantic error before.

            self.operator_height = 40 
            self.operator_length = 35
            self.inc_height = 5


            self.height = self.operator_height + (n_inputs - 2) * self.inc_height
            # we can maybe add self.length later to make the length scale with gates
            self.length = self.operator_length


            self.input_list = []
            self.output_list = [] # These store input and output xy coords for drawing connections

    def draw_with_string(self, op_string): 

        if op_string == "AND": 
            self.draw_and_gate()
        elif op_string == "NAND": 
            self.draw_nand_gate()
        elif op_string == "OR": 
            self.draw_or_gate()
        elif op_string == "NOR": 
            self.draw_nor_gate()
        elif op_string == "XOR": 
            self.draw_xor_gate()
        elif op_string == "CLOCK": 
            self.draw_clock()
        elif op_string == "DTYPE": 
            self.draw_dtype()
        elif op_string == "SWITCH": 
            self.draw_switch()
        else: 
            pass
    
    def make_circle(self, x, y): 
        posx, posy = x, y    
        sides = 10    
        radius = 2
        
        glBegin(GL_POLYGON)    

        for i in range(20):    
            cosine= radius * cos(i*2*pi/sides) + posx    
            sine  = radius * sin(i*2*pi/sides) + posy    
            glVertex2f(cosine,sine)

        glEnd()

    def draw_and_gate(self):
        """Render and draw an AND gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""
        
        

        glColor3f(1.0, 0.0, 0.0)  # Red color
        glBegin(GL_LINE_STRIP)
        # Draw the straight body
        glVertex2f(self.x, self.y)
        glVertex2f(self.x, self.y + self.height)
        glVertex2f(self.x + self.length, self.y + self.height)      
        
        # Draw the curve part
        for i in range(self.n_iter + 1):
            angle = (pi/2) - (i / float(self.n_iter)) * (pi)
            R = (self.height / 2)
            x1 = R * cos(angle) + self.x + self.length 
            y1 = R * sin(angle) + self.y + (self.height / 2)
            glVertex2f(x1, y1)
        
        # Close the shape
        glVertex2f(self.x + self.length, self.y)
        glVertex2f(self.x, self.y)
                         
        glEnd()

        inp_space = self.height - 2 * self.inc_height
        div_space = inp_space/(self.n_inputs + 1)

        for i in range(self.n_inputs): 
            y_coord = self.y + self.inc_height + (i+1)*div_space
            x_coord = self.x

            self.make_circle(x_coord, y_coord)
            self.input_list.append((x_coord, y_coord))
        
        self.output_list.append((self.x + self.length + self.height/2, self.y + self.height/2 ))
        self.make_circle(self.x + self.length + self.height/2, self.y + self.height/2)
    
    def draw_nand_gate(self):
        """Render and draw an NAND gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # Start with the AND gate
        LogicDrawer.draw_and_gate(self)

        # Draw the circle for the NOT part, radius 5
        glColor3f(1.0, 0.0, 0.0)  # Red color
        glBegin(GL_LINE_LOOP)
        for i in range(self.n_iter + 1):
            angle = 2 * pi * i / float(self.n_iter)
            # Must add radius to x length for x1 argument
            r = 5
            # Note self.height / 2 = R as defined in the AND gate
            x1 = r * cos(angle) + self.x + self.length + (self.height / 2) + r
            y1 = r * sin(angle) + self.y + (self.height / 2)
            glVertex2f(x1, y1)
        glEnd()

        inp_space = self.height - 2 * self.inc_height
        div_space = inp_space/(self.n_inputs + 1)

        for i in range(self.n_inputs): 
            y_coord = self.y + self.inc_height + (i+1)*div_space
            x_coord = self.x

            self.make_circle(x_coord, y_coord)
            self.input_list.append((x_coord, y_coord))
        
        self.output_list.append((self.x + self.length + self.height/2, self.y + self.height/2 ))
        self.make_circle(self.x + self.length + self.height/2, self.y + self.height/2)
    
    def draw_or_gate(self):
        """Render and draw an OR gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # Note that x,y is defined from the bottom left of the vertical line on the left
        glColor3f(1.0, 0.0, 0.0)  # Red color
        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x, self.y + self.height)
        # top left corner 
        glVertex2f(self.x - 10, self.y + self.height + 10)
        # top straight line
        glVertex2f(self.x - 10 + self.length, self.y + self.height + 10)

        # point right mid 
        glVertex2f((self.x + self.length + (self.height / 2)), (self.y + (self.height / 2)))
        '''
        # right body curve
        for i in range(self.n_iter + 1):
            angle = (pi/2) - (i / float(self.n_iter)) * (pi)
            R = ((self.height / 2) + 10) # radius is half of height + 1 top edge
            x1 = R * cos(angle) + self.x + self.length 
            y1 = R * sin(angle) + self.y + (self.height / 2)
            glVertex2f(x1, y1)
        '''
        glVertex2f(self.x - 10 + self.length, self.y - 10)
        glVertex2f(self.x - 10 , self.y - 10)
        glVertex2f(self.x, self.y)
        
        glEnd()

        inp_space = self.height - 2 * self.inc_height
        div_space = inp_space/(self.n_inputs + 1)

        for i in range(self.n_inputs): 
            y_coord = self.y + self.inc_height + (i+1)*div_space
            x_coord = self.x

            self.make_circle(x_coord, y_coord)
            self.input_list.append((x_coord, y_coord))
        
        self.output_list.append((self.x + self.length + self.height/2, self.y + self.height/2 ))
        self.make_circle(self.x + self.length + self.height/2, self.y + self.height/2)

    def draw_nor_gate(self):
        """Render and draw an OR gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # Note that x,y is defined from the bottom left of the vertical line on the left, as with OR gate
        LogicDrawer.draw_or_gate(self)
        glColor3f(1.0, 0.0, 0.0)  # Red color
        # Draw the circle for the NOT part, radius 5
        glBegin(GL_LINE_LOOP)
        for i in range(self.n_iter + 1):
            angle = 2 * pi * i / float(self.n_iter)
            # Must add radius to x length for x1 argument
            r = 5
            # Note self.height / 2 = R as defined in the AND gate
            x1 = r * cos(angle) + self.x + self.length + (self.height / 2) + r
            y1 = r * sin(angle) + self.y + (self.height / 2)
            glVertex2f(x1, y1)
        glEnd()

        inp_space = self.height - 2 * self.inc_height
        div_space = inp_space/(self.n_inputs + 1)

        for i in range(self.n_inputs): 
            y_coord = self.y + self.inc_height + (i+1)*div_space
            x_coord = self.x

            self.make_circle(x_coord, y_coord)
            self.input_list.append((x_coord, y_coord))
        
        self.output_list.append((self.x + self.length + self.height/2, self.y + self.height/2 ))
        self.make_circle(self.x + self.length + self.height/2, self.y + self.height/2)

    def draw_xor_gate(self):
        """Render and draw an OR gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # n_inputs is ONLY 2 here -- don't modify n_inputs as its default is 2. 
        assert self.n_inputs == 2
        assert self.height == 40

        # Note that x,y is defined from the bottom left of the vertical line on the left, as with OR gate
        LogicDrawer.draw_or_gate(self)
        glColor3f(1.0, 0.0, 0.0)  # Red color
        glBegin(GL_LINE_STRIP)
        # x distance 10 to the left of the OR gate
        glVertex2f(self.x - 20, self.y - 10)
        glVertex2f(self.x - 10, self.y)
        glVertex2f(self.x - 10, self.y + self.height)
        glVertex2f(self.x - 20, self.y + self.height + 10)
        glEnd()

        inp_space = self.height - 2 * self.inc_height
        div_space = inp_space/(self.n_inputs + 1)

        for i in range(self.n_inputs): 
            y_coord = self.y + self.inc_height + (i+1)*div_space
            x_coord = self.x

            self.make_circle(x_coord, y_coord)
            self.input_list.append((x_coord, y_coord))
        
        self.output_list.append((self.x + self.length + self.height/2, self.y + self.height/2 ))
        self.make_circle(self.x + self.length + self.height/2, self.y + self.height/2)

    def draw_switch(self):
        """Render and draw a switch from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # Radius 20
        self.height = 40
        self.width = self.height

        # x, y defined from CENTRE of circle

        glColor3f(0.0, 1.0, 0.0)  # Green color
        glBegin(GL_LINE_LOOP)
        for i in range(self.n_iter + 1):
            angle = 2 * pi * i / float(self.n_iter)
            r = self.height / 2
            x1 = r * cos(angle) + self.x 
            y1 = r * sin(angle) + self.y 
            glVertex2f(x1, y1)
        glEnd()

        self.output_list.append((self.x + r, self.y))
        self.make_circle(self.x + r, self.y)

    def draw_clock(self):
        """Render and draw a clock from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        self.height = 40
        self.width = self.height

        # x, y defined from CENTRE of square
        glColor3f(0.0, 1.0, 0.0)  # Green color
        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x - (self.width / 2), self.y - (self.height / 2))
        glVertex2f(self.x - (self.height / 2), self.y + (self.height / 2))
        glVertex2f(self.x + (self.width / 2), self.y + (self.height / 2))
        glVertex2f(self.x + (self.width / 2), self.y - (self.height / 2))
        glVertex2f(self.x - (self.width / 2), self.y - (self.height / 2))
        glEnd()

        self.output_list.append((self.x + self.width/2, self.y))
        self.make_circle(self.x + self.width/2, self.y)

    def draw_dtype(self):
        """Render and draw a DTYPE from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # x, y defined from CENTRE of rectangle
        # DTYPE has height 100, width 60
        self.height = 100
        self.width = 60

        glColor3f(0.0, 0.0, 1.0)  # Blue color
        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x - (self.width / 2), self.y - (self.height / 2))
        glVertex2f(self.x - (self.width / 2), self.y + (self.height / 2))
        glVertex2f(self.x + (self.width / 2), self.y + (self.height / 2))
        glVertex2f(self.x + (self.width / 2), self.y - (self.height / 2))
        glVertex2f(self.x - (self.width / 2), self.y - (self.height / 2))
        glEnd()

        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x - (self.width / 2), self.y - 2/16 * self.height)
        glVertex2f(self.x - (self.width / 2), self.y - 6/16 * self.height)
        glVertex2f(self.x - (self.width / 2) + (self.height/8), self.y - 4/16 * self.height)
        glVertex2f(self.x - (self.width / 2), self.y - 2/16 * self.height)
        glEnd()


        s_coord = (self.x, self.y + self.height/2)
        r_coord = (self.x, self.y - self.height/2)

        d_coord = (self.x - self.width/2, self.y + 2/8 * self.height)
        ck_coord = (self.x - self.width/2, self.y - 2/8 * self.height)

        q_coord = (self.x + self.width/2, self.y + 2/8 * self.height)
        qb_coord = (self.x + self.width/2, self.y - 2/8 * self.height)

        
        self.make_circle(s_coord[0], s_coord[1])
        self.make_circle(r_coord[0], r_coord[1])
        self.make_circle(d_coord[0], d_coord[1])
        self.make_circle(ck_coord[0], ck_coord[1])
        self.make_circle(q_coord[0], q_coord[1])
        self.make_circle(qb_coord[0], qb_coord[1])

        self.input_list.append(s_coord)
        self.input_list.append(r_coord)
        self.input_list.append(d_coord)
        self.input_list.append(ck_coord)

        self.output_list.append(q_coord)
        self.output_list.append(qb_coord)

        
