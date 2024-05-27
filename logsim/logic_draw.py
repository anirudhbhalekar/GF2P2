from math import cos, sin, pi
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINE_STRIP, GL_LINE_LOOP


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
            self.inc_height = 15 
            # 15 pixels height increase for each additional input
            # top and bottom padding 5 px each
            # self.height is only the vertical straight bit
            self.height = self.operator_height + (n_inputs - 2) * self.inc_height
            # we can maybe add self.length later to make the length scale with gates
            self.length = self.operator_length

    def draw_and_gate(self):
        """Render and draw an AND gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""
        
        glColor3f(1.0, 0.0, 0.0)  # Red color
        glBegin(GL_LINE_STRIP)
        # Draw the straight body, x,y defined from bottom left corner
        glVertex2f(self.x, self.y)
        glVertex2f(self.x, self.y + self.height)
        glVertex2f(self.x + self.length, self.y + self.height)      
        
        # Draw the curve part
        R = (self.height / 2)
        for i in range(self.n_iter + 1):
            angle = (pi/2) - (i / float(self.n_iter)) * (pi)
            x1 = R * cos(angle) + self.x + self.length 
            y1 = R * sin(angle) + self.y + (self.height / 2)
            glVertex2f(x1, y1)
        
        # Close the shape
        glVertex2f(self.x + self.length, self.y)
        glVertex2f(self.x, self.y)
                         
        glEnd()

        # List of tuples containing input locations
        input_list = [(self.x, self.y + 5 + self.inc_height*i) for i in range(self.n_inputs)]
        # List of tuple containing output location
        output_list = [(self.x + self.length + R), R]
        # List of tuples containing domain (bottom left, top right)
        # Give padding 1 px
        domain_list = [(self.x + 1, self.y + 1), (self.x + self.length + R - 1, self.y + self.height - 1)]

        return (input_list, output_list, domain_list)
    
    def draw_nand_gate(self):
        """Render and draw an NAND gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # Start with the AND gate
        LogicDrawer.draw_and_gate(self)

        # Draw the circle for the NOT part, radius 5
        glColor3f(1.0, 0.0, 0.0)  # Red color
        glBegin(GL_LINE_LOOP)

        R = (self.height / 2)
        r = 5
        for i in range(self.n_iter + 1):
            angle = 2 * pi * i / float(self.n_iter)
            # Must add radius to x length for x1 argument
            x1 = r * cos(angle) + self.x + self.length + R + r
            y1 = r * sin(angle) + self.y + R
            glVertex2f(x1, y1)
        glEnd()

        # List of tuples containing input locations
        input_list = [(self.x, self.y + 5 + self.inc_height*i) for i in range(self.n_inputs)]
        # List of tuple containing output location
        output_list = [(self.x + self.length + R + 2*r), R]
        # List of tuples containing domain (bottom left, top right)
        # Give padding 1 px
        domain_list = [(self.x + 1, self.y + 1), (self.x + self.length + R + 2*r - 1, self.y + self.height - 1)]

        return (input_list, output_list, domain_list)
    
    def draw_or_gate(self):
        """Render and draw an OR gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # Note that x,y is defined from the bottom of the vertical line on the left
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
        glVertex2f(self.x - 10 + self.length, self.y - 10)
        glVertex2f(self.x - 10 , self.y - 10)
        glVertex2f(self.x, self.y)
        
        glEnd()

        # List of tuples containing input locations
        input_list = [(self.x, self.y + 5 + self.inc_height*i) for i in range(self.n_inputs)]
        # List of tuple containing output location
        output_list = [(self.x + self.length + (self.height / 2)), self.y + (self.height / 2)]
        # List of tuples containing domain (bottom left, top right)
        # Give padding 1 px
        domain_list = [(self.x - 10 + 1, self.y - 10 + 1), (self.x + self.length + (self.height / 2) - 1, self.y + self.height + 10 - 1)]

        return (input_list, output_list, domain_list)
        
    def draw_nor_gate(self):
        """Render and draw an OR gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # Note that x,y is defined from the bottom left of the vertical line on the left, as with OR gate
        LogicDrawer.draw_or_gate(self)
        glColor3f(1.0, 0.0, 0.0)  # Red color
        # Draw the circle for the NOT part, radius 5
        glBegin(GL_LINE_LOOP)
        r = 5
        R = self.height / 2
        for i in range(self.n_iter + 1):
            angle = 2 * pi * i / float(self.n_iter)            
            # Note self.height / 2 = R as defined in the AND gate
            x1 = r * cos(angle) + self.x + self.length + R + r
            y1 = r * sin(angle) + self.y + R
            glVertex2f(x1, y1)
        glEnd()

        # List of tuples containing input locations
        input_list = [(self.x, self.y + 5 + self.inc_height*i) for i in range(self.n_inputs)]
        # List of tuple containing output location
        output_list = [(self.x + self.length + R + 2*r), self.y + R]
        # List of tuples containing domain (bottom left, top right)
        # Give padding 1 px
        domain_list = [(self.x - 10 + 1, self.y - 10 + 1), (self.x + self.length + R + 2*r - 1, self.y + self.height + 10 - 1)]

        return (input_list, output_list, domain_list)
    
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

        # List of tuples containing input locations
        input_list = [(self.x - 10, self.y + 5 + self.inc_height*i) for i in range(self.n_inputs)]
        # List of tuple containing output location
        output_list = [(self.x + self.length + (self.height / 2)), self.y + (self.height / 2)]
        # List of tuples containing domain (bottom left, top right)
        # Give padding 1 px
        domain_list = [(self.x - 10 - 10 + 1, self.y - 10 + 1), (self.x + self.length + (self.height / 2) - 1, self.y + self.height + 10 - 1)]

        return (input_list, output_list, domain_list)
    
    def draw_switch(self):
        """Render and draw a switch from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # Radius 20
        self.height = 40
        self.width = self.height
        R = self.height / 2
        # x, y defined from CENTRE of circle

        glColor3f(0.0, 1.0, 0.0)  # Green color
        glBegin(GL_LINE_LOOP)
        for i in range(self.n_iter + 1):
            angle = 2 * pi * i / float(self.n_iter)
            x1 = R * cos(angle) + self.x 
            y1 = R * sin(angle) + self.y 
            glVertex2f(x1, y1)
        glEnd()

        # Switch has no input
        input_list = None
        # List of tuple containing output location
        output_list = [(self.x + R, self.y)]
        # List of tuples containing domain (bottom left, top right)
        # Give padding 1 px
        domain_list = [(self.x - R + 1, self.y - R + 1), (self.x + R - 1, self.y + R - 1)]

        return (input_list, output_list, domain_list)
    
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

        # Clock has no input
        input_list = None
        # List of tuple containing output location
        output_list = [(self.x + (self.width / 2), self.y)]
        # List of tuples containing domain (bottom left, top right)
        # Give padding 1 px
        R = self.height / 2
        domain_list = [(self.x - R + 1, self.y - R + 1), (self.x + R - 1, self.y + R - 1)]

        return (input_list, output_list, domain_list)
    
    def draw_dtype(self):
        """Render and draw a DTYPE from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # x, y defined from CENTRE of rectangle
        # DTYPE has height 100, width 60
        self.height = 100
        self.width = 60

        glColor3f(0.0, 0.0, 1.0)  # Blue color
        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x, self.y + self.height)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x, self.y)
        glEnd()

        # inputs in order: data (left top), clock (left bottom), set (top), reset (bottom)
        input_list = [(self.x - (self.width / 2), self.y + 20), (self.x - (self.width / 2), self.y - 20), (self.x, self.y + (self.height / 2)), (self.x, self.y - (self.height / 2))]
        # ouputs in order: Q, Q_bar
        output_list = [(self.x + (self.width / 2), self.y + 20), (self.x + (self.width / 2), self.y - 20)]
        # List of tuples containing domain (bottom left, top right)
        # Give padding 1 px
        domain_list = [(self.x - (self.width / 2) + 1, self.y - (self.height / 2) + 1), (self.x + (self.width / 2) - 1, self.y + (self.height / 2) - 1)]

        return (input_list, output_list, domain_list)