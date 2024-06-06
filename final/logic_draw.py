from math import cos, sin, pi
from OpenGL.GL import GL_LINE_STRIP, GL_LINE_LOOP, GL_POLYGON, GL_ENABLE_BIT, GL_LINE_STIPPLE
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, glPushAttrib, glLineStipple, glPopAttrib, glEnable
from OpenGL import GL, GLUT

# NB No translation needed here, only drawing shapes.

"""
LogicDrawer: A class for rendering various logic gates and components on a canvas using OpenGL.

This class handles the drawing operations for different logic gates such as AND, NAND, OR, NOR, XOR, as well as components like clocks, switches, DTYPEs, and monitors. The gates are drawn based on their specified inputs and positions. The class supports various drawing methods for each gate type, providing functionality to render the shapes, connections, and labels on the canvas.

Attributes:
    id (int): The device id.
    n_iter (int): Number of iterations used to draw circles for certain gates.
    operator_height (int): Base height of the operator.
    operator_length (int): Length of the operator.
    inc_height (int): Height increment for additional inputs.
    names (Names): Instance of the Names class.
    devices (Devices): Instance of the Devices class.
    monitors (Monitors): Instance of the Monitors class.
    device (Device): The device object.
    device_inputs (dict): Dictionary of device inputs.
    device_outputs (dict): Dictionary of device outputs.
    n_inputs (int): Number of inputs for the device.
    height (int): Height of the gate.
    length (int): Length of the gate.
    input_dict (dict): Dictionary storing input coordinates.
    output_dict (dict): Dictionary storing output coordinates.
    monitor_dict (dict): Dictionary storing monitor coordinates.
    domain (list): List of tuples representing the bounding domain.

Methods:
    draw_with_string(op_string, x, y): Calls the appropriate draw function based on the gate type.
    bound_y(): Returns the y-coordinate padding bound of a device.
    make_circle(x, y): Draws a dot at the specified (x, y) position to symbolize a connection point.
    draw_and_gate(x, y): Renders and draws an AND gate at the specified position.
    draw_nand_gate(x, y): Renders and draws a NAND gate at the specified position.
    draw_or_gate(x, y): Renders and draws an OR gate at the specified position.
    draw_nor_gate(x, y): Renders and draws a NOR gate at the specified position.
    draw_xor_gate(x, y): Renders and draws an XOR gate at the specified position.
    draw_switch(x, y): Renders and draws a switch at the specified position.
    draw_clock(x, y): Renders and draws a clock at the specified position.
    draw_dtype(x, y): Renders and draws a DTYPE at the specified position.
    render_text(text, x_pos, y_pos, color): Handles text drawing operations at the specified position and color.
    draw_monitor(x, y, m_name): Renders and draws a monitor at the specified position.
"""


class LogicDrawer:
    """Handle all logic gate drawings."""
    
    def __init__(self, names, devices, monitors, id, n_iter=10):
            """Initialize logic drawer with the number of inputs for 
            certain gates and also the number of iterations used to
            draw circles for certain gates."""
            
            # Initialize variables
            self.id = id # -> This is the device id
            self.n_iter = n_iter
            # 2 input gate is 40 high, and every additional input gate adds 5 units of height
            # n_inputs is between 1 and 16, but ONLY 2 for XOR gate. This is checked as a semantic error before
            self.operator_height = 30 
            self.operator_length = 25
            self.inc_height = 5 
           
            self.names = names
            self.devices = devices
            self.monitors = monitors

            try: 
                self.device = self.devices.get_device(self.id) # This is the device obj 

                self.device_inputs = self.device.inputs
                self.device_outputs = self.device.outputs

                self.n_inputs = len(self.device_inputs.keys())
                
                # 5 pixels height increase for each additional input
                # top and bottom padding 5 px each
                # self.height is only the vertical straight bit
                self.height = self.operator_height 

                if self.n_inputs > 2: 
                    self.height += (self.n_inputs - 2) * self.inc_height
                # we can maybe add self.length later to make the length scale with gates
                self.length = self.operator_length
            except: 
                pass

            # These store input and output xy coords for drawing connections
            self.input_dict = {} # This in the form (device_id, port_id): coord
            self.output_dict = {} # This in the form (device_id, port_id): coord
            self.monitor_dict = {} 
           
            self.domain = [] # This is a list of tuples
                
    def draw_with_string(self, op_string, x, y): 
        """Call appropriate draw function"""
        self.x, self.y = x, y
        if op_string == "AND": 
            self.draw_and_gate(self.x, self.y)
        elif op_string == "NAND": 
            self.draw_nand_gate(self.x, self.y)
        elif op_string == "OR": 
            self.draw_or_gate(self.x, self.y)
        elif op_string == "NOR": 
            self.draw_nor_gate(self.x, self.y)
        elif op_string == "XOR": 
            self.draw_xor_gate(self.x, self.y)
        elif op_string == "CLOCK": 
            self.draw_clock(self.x, self.y)
        elif op_string == "DTYPE": 
            self.draw_dtype(self.x, self.y)
        elif op_string == "SWITCH": 
            self.draw_switch(self.x, self.y)
        elif op_string == "RC":
            self.draw_RC(self.x, self.y)
        else:  
            pass
    
    def get_domain(self, x, y): 

        device_kind = self.device.device_kind


        if device_kind == self.devices.AND: 
            
            self.x, self.y = x, y

            self.x = self.x - self.length / 2
            self.y = self.y - self.height / 2

            R = (self.height / 2)

            inp_space = self.height - 2 * self.inc_height
            div_space = inp_space/(self.n_inputs + 1)

            input_ids = self.device_inputs.keys()
            output_ids = self.device_outputs.keys()

            for i, i_id in enumerate(input_ids): 
                y_coord = self.y + self.inc_height + (i+1)*div_space
                x_coord = self.x

                self.input_dict[(self.id, i_id)] = (x_coord, y_coord)

            for o, o_id in enumerate(output_ids): 
                y_coord = self.y + self.height/2 
                x_coord = self.x + self.length + self.height/2

                self.output_dict[(self.id, o_id)] = (x_coord, y_coord)
            
            self.domain = [(self.x - 10, self.y - 10), (self.x + self.length + R + 10, self.y + self.height + 10)]

        elif device_kind == self.devices.NAND: 

            self.x, self.y = x, y

            self.x = self.x - self.length / 2
            self.y = self.y - self.height / 2

            R = (self.height / 2)
            r = 5

            inp_space = self.height - 2 * self.inc_height
            div_space = inp_space/(self.n_inputs + 1)

            input_ids = self.device_inputs.keys()
            output_ids = self.device_outputs.keys()

            for i, i_id in enumerate(input_ids): 
                y_coord = self.y + self.inc_height + (i+1)*div_space
                x_coord = self.x

                self.input_dict[(self.id, i_id)] = (x_coord, y_coord)    

            for o, o_id in enumerate(output_ids): 
                y_coord = self.y + self.height/2 
                x_coord = self.x + self.length + self.height/2 + 2*r

                self.output_dict[(self.id, o_id)] = (x_coord, y_coord)
            
            self.domain = [(self.x - 10, self.y - 10), (self.x + self.length + R + 10 + 2*r, self.y + self.height + 10)]
        
        elif device_kind == self.devices.OR: 
            
            self.x, self.y = x, y

            self.x = self.x - self.length / 2
            self.y = self.y - self.height / 2

            R = (self.height / 2)
            r = 5

            inp_space = self.height - 2 * self.inc_height
            div_space = inp_space/(self.n_inputs + 1)

            input_ids = self.device_inputs.keys()
            output_ids = self.device_outputs.keys()

            for i, i_id in enumerate(input_ids): 
                y_coord = self.y + self.inc_height + (i+1)*div_space
                x_coord = self.x

                self.input_dict[(self.id, i_id)] = (x_coord, y_coord)
    
            for o, o_id in enumerate(output_ids): 
                y_coord = self.y + self.height/2 
                x_coord = self.x + self.length + self.height/2

                self.output_dict[(self.id, o_id)] = (x_coord, y_coord)
                
            self.domain = [(self.x - 15 + 1, self.y - 15 + 1), (self.x + self.length + (self.height / 2) + 15 - 1, self.y + self.height + 15 - 1)]

        elif device_kind == self.devices.NOR: 
            
            self.x, self.y = x, y

            self.x = self.x - self.length / 2
            self.y = self.y - self.height / 2

            R = (self.height / 2)
            r = 5

            inp_space = self.height - 2 * self.inc_height
            div_space = inp_space/(self.n_inputs + 1)

            input_ids = self.device_inputs.keys()
            output_ids = self.device_outputs.keys()

            for i, i_id in enumerate(input_ids): 
                y_coord = self.y + self.inc_height + (i+1)*div_space
                x_coord = self.x

                self.input_dict[(self.id, i_id)] = (x_coord, y_coord)

            for o, o_id in enumerate(output_ids): 
                y_coord = self.y + self.height/2 
                x_coord = self.x + self.length + self.height/2 + 2*r

                self.output_dict[(self.id, o_id)] = (x_coord, y_coord)
                
            self.domain = [(self.x - 15 + 1, self.y - 15 + 1), (self.x + self.length + R + 2*r + 15 - 1, self.y + self.height + 15 - 1)]

        elif device_kind == self.devices.XOR: 
            # Do XOR 
            self.x, self.y = x, y

            self.x = self.x - self.length / 2
            self.y = self.y - self.height / 2 

            R = (self.height / 2)
            r = 5

            inp_space = self.height - 2 * self.inc_height
            div_space = inp_space/(self.n_inputs + 1)

            input_ids = self.device_inputs.keys()
            output_ids = self.device_outputs.keys()

            for i, i_id in enumerate(input_ids): 
                y_coord = self.y + self.inc_height + (i+1)*div_space
                x_coord = self.x

                self.input_dict[(self.id, i_id)] = (x_coord, y_coord)
    
            for o, o_id in enumerate(output_ids): 
                y_coord = self.y + self.height/2 
                x_coord = self.x + self.length + self.height/2

                self.output_dict[(self.id, o_id)] = (x_coord, y_coord)
                
            self.domain = [(self.x - 22, self.y - 22), (self.x + self.length + (self.height / 2) + 22, self.y + self.height + 22 )]

        elif device_kind == self.devices.SWITCH: 
            # Do SWITCH 
            output_ids = self.device_outputs.keys()

            self.x, self.y = x, y
            # Radius 20
            self.height = 40
            self.width = self.height
            R = self.height / 2

            for o, o_id in enumerate(output_ids): 
                y_coord = self.y
                x_coord = self.x + R

            self.output_dict[(self.id, o_id)] = (x_coord, y_coord)
        
            self.domain = [(self.x - R  - 5, self.y - R - 5), (self.x + R + 5, self.y + R + 5)]

        elif device_kind == self.devices.CLOCK: 
            # Do CLOCK 
            self.x, self.y = x, y

            self.height = 40
            self.width = self.height
            R = self.height / 2

            inp_space = self.height - 2 * self.inc_height
            div_space = inp_space/(self.n_inputs + 1)

            input_ids = self.device_inputs.keys()
            output_ids = self.device_outputs.keys()
            
            for i, i_id in enumerate(input_ids): 
                y_coord = self.y + self.inc_height + (i+1)*div_space
                x_coord = self.x

                self.input_dict[(self.id, i_id)] = (x_coord, y_coord)

            for o, o_id in enumerate(output_ids): 
                y_coord = self.y
                x_coord = self.x + (self.width / 2)

                self.output_dict[(self.id, o_id)] = (x_coord, y_coord)
                
            self.domain =  [(self.x - R + 1, self.y - R + 1), (self.x + R - 1, self.y + R - 1)]

        elif device_kind == self.devices.D_TYPE: 
            # Do D_TYPE
            self.x, self.y = x, y
            # x, y defined from CENTRE of rectangle
            # DTYPE has height 100, width 60
            self.height = 100
            self.width = 60

            #Introducing top heavy bias
            self.x = self.x 
            self.y = self.y - self.height/3

            inp_space = self.height - 2 * self.inc_height
            div_space = inp_space/(self.n_inputs + 1)

            input_ids = self.device_inputs.keys()
            output_ids = self.device_outputs.keys()

            temp_input_list = [(self.x - (self.width / 2), self.y + 20), (self.x - (self.width / 2), self.y - 20), 
                               (self.x, self.y + (self.height / 2)), (self.x, self.y - (self.height / 2))]
            
            for i, i_id in enumerate(input_ids): 

                if i_id == self.devices.DATA_ID: 
                    index = 0
                elif i_id == self.devices.CLK_ID:
                    index = 1
                elif i_id == self.devices.SET_ID: 
                    index = 2
                else: 
                    index = 3   

                y_coord = temp_input_list[index][1]
                x_coord = temp_input_list[index][0]

                self.input_dict[(self.id, i_id)] = (x_coord, y_coord)
    
            temp_output_list = [(self.x + (self.width / 2), self.y + 20), (self.x + (self.width / 2), self.y - 20)]
            
            for o, o_id in enumerate(output_ids): 

                if o_id == self.devices.Q_ID: 
                    index = 0
                else: 
                    index = 1

                y_coord = temp_output_list[index][1]
                x_coord = temp_output_list[index][0]

                self.output_dict[(self.id, o_id)] = (x_coord, y_coord)
        
            self.domain = [(self.x - (self.width / 2) - 20, self.y - (self.height / 2) - 20), (self.x + (self.width / 2) + 20, self.y + (self.height / 2) + 20)]
    
        else: 
            # Do RC
            self.x = x
            self.y = y 
            self.height = 40
            self.length = 40

            half_length = self.length / 2
            half_height = self.height / 2
            
            inp_space = self.height - 2 * self.inc_height
            div_space = inp_space/(self.n_inputs + 1)

            input_ids = self.device_inputs.keys()
            output_ids = self.device_outputs.keys()
            
            for i, i_id in enumerate(input_ids): 
                y_coord = self.y + self.inc_height + (i+1)*div_space
                x_coord = self.x
                self.input_dict[(self.id, i_id)] = (x_coord, y_coord)

            for o, o_id in enumerate(output_ids): 
                y_coord = self.y
                x_coord = self.x + (self.length / 2)
                self.output_dict[(self.id, o_id)] = (x_coord, y_coord)

            self.domain =  [(self.x - half_length - 10, self.y - half_height - 10), (self.x + half_length + 10, self.y + half_height + 10)]



        

    def make_circle(self, x, y): 
        """Draw a dot at posiition (x, y) to symbolise a connection point."""
        posx, posy = x, y    
        sides = 10    
        radius = 2

        glBegin(GL_POLYGON)    
        glColor3f(0.0, 0.0, 0.0)
        for i in range(20):    
            cosine= radius * cos(i*2*pi/sides) + posx    
            sine  = radius * sin(i*2*pi/sides) + posy    
            glVertex2f(cosine,sine)

        glEnd()

    def draw_and_gate(self, x, y):
        """Render and draw an AND gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""
        self.x, self.y = x, y

        # Coordinate change to center gates
        self.x = self.x - self.length / 2
        self.y = self.y - self.height / 2

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
        
        d_name = self.names.get_name_string(self.id)
        self.render_text(d_name, self.x + self.length/2, self.y + self.height/2, color="black")

        for coord_input in list(self.input_dict.values()): 
            self.make_circle(coord_input[0], coord_input[1])
        
        for coord_output in list(self.output_dict.values()): 
            self.make_circle(coord_output[0], coord_output[1])
        
    def draw_nand_gate(self, x, y):
        """Render and draw an NAND gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""
        self.x, self.y = x, y

        # Coordinate change to center gates
        self.x = self.x - self.length / 2
        self.y = self.y - self.height / 2

        # Start with the AND gate
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

        d_name = self.names.get_name_string(self.id)
        self.render_text(d_name, self.x + self.length/2, self.y + self.height/2, color="black")

        for coord_input in list(self.input_dict.values()): 
            self.make_circle(coord_input[0], coord_input[1])
        
        for coord_output in list(self.output_dict.values()): 
            self.make_circle(coord_output[0], coord_output[1])
    
    def draw_or_gate(self, x, y):
        """Render and draw an OR gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""
        # Coordinate change to center gates
        self.x, self.y = x, y

        self.x = self.x - self.length / 2
        self.y = self.y - self.height / 2 

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

        d_name = self.names.get_name_string(self.id)
        self.render_text(d_name, self.x + self.length/2, self.y + self.height/2, color="black")

        for coord_input in list(self.input_dict.values()): 
            self.make_circle(coord_input[0], coord_input[1])
        
        for coord_output in list(self.output_dict.values()): 
            self.make_circle(coord_output[0], coord_output[1])

    def draw_nor_gate(self, x, y):
        """Render and draw an OR gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""
        self.x, self.y = x, y

        # Coordinate change to center gates
        self.x = self.x - self.length / 2
        self.y = self.y - self.height / 2 
        
        # Note that x,y is defined from the bottom left of the vertical line on the left, as with OR gate
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
        
        d_name = self.names.get_name_string(self.id)
        self.render_text(d_name, self.x + self.length/2, self.y + self.height/2, color="black")

        for coord_input in list(self.input_dict.values()): 
            self.make_circle(coord_input[0], coord_input[1])
        
        for coord_output in list(self.output_dict.values()): 
            self.make_circle(coord_output[0], coord_output[1])
        
    def draw_xor_gate(self, x, y):
        """Render and draw an OR gate from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""

        # n_inputs is ONLY 2 here -- don't modify n_inputs as its default is 2. 
        assert self.n_inputs == 2
        assert self.height == 30

        self.x, self.y = x, y

        self.x = self.x - self.length / 2
        self.y = self.y - self.height / 2 

        # Note that x,y is defined from the bottom left of the vertical line on the left, as with OR gate
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

        glColor3f(1.0, 0.0, 0.0)  # Red color
        glBegin(GL_LINE_STRIP)
        # x distance 10 to the left of the OR gate
        glVertex2f(self.x - 20, self.y - 10)
        glVertex2f(self.x - 10, self.y)
        glVertex2f(self.x - 10, self.y + self.height)
        glVertex2f(self.x - 20, self.y + self.height + 10)
        glEnd()

        d_name = self.names.get_name_string(self.id)
        self.render_text(d_name, self.x + self.length/2, self.y + self.height/2, color="black")

        for coord_input in list(self.input_dict.values()): 
            self.make_circle(coord_input[0], coord_input[1])
        
        for coord_output in list(self.output_dict.values()): 
            self.make_circle(coord_output[0], coord_output[1])

    def draw_switch(self, x, y):
        """Render and draw a switch from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""
        
        self.x, self.y = x, y
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

        # Render the switch name
        d_name = self.names.get_name_string(self.id)
        self.render_text(d_name, self.x + self.length/2, self.y + self.height/2, color="black")

        for coord_output in self.output_dict.values(): 
            self.make_circle(coord_output[0], coord_output[1])

        # Switch has no input        
        this_device = self.devices.get_device(self.id)
        #print(this_device.device_id)
        if this_device.switch_state == 0:
            # Draw open circuit switch symbol
            glColor3f(0.0, 0.0, 0.0) # Black color
            glBegin(GL_LINE_STRIP)
            glVertex2f((self.x - self.width / 2), self.y)
            glVertex2f((self.x - self.width / 4), self.y)
            glVertex2f((self.x + self.width / 4), (self.y + self.height / 3))
            glEnd()
            
            self.make_circle(self.x - self.width / 4, self.y)
            self.make_circle(self.x + self.width / 4, self.y)

            glBegin(GL_LINE_STRIP)
            glVertex2f(self.x + self.width / 4, self.y)
            glVertex2f(self.x + self.width / 2, self.y)
            glEnd()
            
        elif this_device.switch_state == 1:
            # Draw closed circuit switch symbol
            glColor3f(0.0, 0.0, 0.0) # Black color
            glBegin(GL_LINE_STRIP)
            glVertex2f((self.x - self.width / 2), self.y)
            glVertex2f((self.x + self.width / 2), self.y)
            glEnd()
            self.make_circle(self.x - self.width / 4, self.y)
            self.make_circle(self.x + self.width / 4, self.y)

        else: 
            self.render_text("Error: Unknown switch state!", self.x, (self.y - self.height), color="red")

    def draw_clock(self, x, y):
        """Render and draw a clock from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""
        self.x, self.y = x, y

        self.height = 40
        self.width = self.height
        R = self.height / 2
        
        # x, y defined from CENTRE of square
        glColor3f(0.0, 1.0, 0.0)  # Green color
        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x - (self.width / 2), self.y - (self.height / 2))
        glVertex2f(self.x - (self.height / 2), self.y + (self.height / 2))
        glVertex2f(self.x + (self.width / 2), self.y + (self.height / 2))
        glVertex2f(self.x + (self.width / 2), self.y - (self.height / 2))
        glVertex2f(self.x - (self.width / 2), self.y - (self.height / 2))
        glEnd()

        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x - self.width / 2 + 1, self.y)
        glVertex2f(self.x - self.width / 4, self.y)
        glVertex2f(self.x - self.width / 4, self.y + self.height / 4)
        glVertex2f(self.x, self.y + self.height / 4)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width / 4, self.y)
        glVertex2f(self.x + self.width / 4, self.y + self.height / 4)
        glVertex2f(self.x + self.width / 2 - 1, self.y + self.height / 4)
        glEnd()

        d_name = self.names.get_name_string(self.id)
        self.render_text(d_name, self.x + self.length/2, self.y + self.height/2, color="black")

        for coord_input in list(self.input_dict.values()): 
            self.make_circle(coord_input[0], coord_input[1])
        
        for coord_output in list(self.output_dict.values()): 
            self.make_circle(coord_output[0], coord_output[1])
        
    def draw_dtype(self, x, y):
        """Render and draw a DTYPE from the LogicDrawer on the canvas,
        with the position, inputs and iterations inherited from the class."""
        self.x, self.y = x, y
        # x, y defined from CENTRE of rectangle
        # DTYPE has height 100, width 60
        self.height = 100
        self.width = 60

        #Introducing top heavy bias
        self.x = self.x 
        self.y = self.y - self.height/3

        glColor3f(0.0, 0.0, 1.0)  # Blue color
        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x - (self.width / 2), self.y - (self.height / 2))
        glVertex2f(self.x - (self.width / 2), self.y + (self.height / 2))
        glVertex2f(self.x + (self.width / 2), self.y + (self.height / 2))
        glVertex2f(self.x + (self.width / 2), self.y - (self.height / 2))
        glVertex2f(self.x - (self.width / 2), self.y - (self.height / 2))
        glEnd()

        # triangle shape for clock dtype input
        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x - (self.width / 2), self.y - 7)
        glVertex2f(self.x - (self.width / 2) + (self.height/8), self.y - 20)
        glVertex2f(self.x - (self.width / 2), self.y - 33)
        glVertex2f(self.x - (self.width / 2), self.y - 10)
        glEnd()

        d_name = self.names.get_name_string(self.id)
        self.render_text(d_name, self.x - (self.width / 4), self.y, color="black")

        inp_labels = ["CLK", "SET", "RSET", "DATA"]
        out_labels = ["Q", "QBAR"]

        for coord_input in list(self.input_dict.values()): 
            self.make_circle(coord_input[0], coord_input[1])
            self.render_text(inp_labels.pop(0), coord_input[0] - 5, coord_input[1])
        
        for coord_output in list(self.output_dict.values()): 
            self.make_circle(coord_output[0], coord_output[1])
            self.render_text(out_labels.pop(0), coord_output[0] - 5, coord_output[1])

    def draw_RC(self, x, y): 

        self.x = x
        self.y = y 
        self.height = 40
        self.length = 40

        half_length = self.length / 2
        half_height = self.height / 2

        glColor3f(0.3, 0.5, 0.3)  # dark green color
        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x - half_length, self.y)
        glVertex2f(self.x - half_length, self.y + half_height)
        glVertex2f(self.x + half_length, self.y)
        glVertex2f(self.x - half_length, self.y - half_height)
        glVertex2f(self.x - half_length, self.y)
        glEnd()
        # now draw the schmidt trigger symbol
        glColor3f(0.3, 0.5, 0.3)  # dark green color
        glBegin(GL_LINE_STRIP)
        glVertex2f(self.x - half_length*(7/8), self.y - half_height/3)
        glVertex2f(self.x, self.y - half_height/3)
        glVertex2f(self.x, self.y + half_height/3)
        glVertex2f(self.x + half_length*(2/8), self.y + half_height/3)
        glVertex2f(self.x - half_length*(5/8), self.y + half_height/3)
        glVertex2f(self.x - half_length*(5/8), self.y - half_height/3)
        glEnd()

        d_name = self.names.get_name_string(self.id)
        self.render_text(d_name, self.x + self.length/2, self.y + self.height/2, color="black")

        for coord_input in list(self.input_dict.values()): 
            self.make_circle(coord_input[0], coord_input[1])
        
        for coord_output in list(self.output_dict.values()): 
            self.make_circle(coord_output[0], coord_output[1])


    def draw_monitor(self, x, y, m_name: str):
        """Render and draw a Monitor"""
        
        self.x, self.y = x, y 
        # x, y defined from bottom of vertical line below tringle
        glColor3f(1.0, 0.0, 1.0)  # Purple color
        glBegin(GL_POLYGON)
        glVertex2f(self.x, self.y+ 5)
        #glVertex2f(self.x, self.y + 15)
        glVertex2f(self.x - 10, self.y + 20)
        glVertex2f(self.x + 10, self.y + 20)
        #glVertex2f(self.x, self.y + 15)
        glVertex2f(self.x, self.y+ 5)
        glEnd()

        self.render_text(m_name, self.x + 20, self.y, 'purple')

        # Monitor has one input - where it monitors from
        self.input_list = [(self.x, self.y)]        
        # monitor has no output points
        # draw dots for input and output spaces
        x1, y1 = self.input_list[0][0], self.input_list[0][1]
        self.make_circle(x1, y1)

    def render_text(self, text, x_pos, y_pos, color = 'blue'):
        """Handle text drawing operations."""

        if color == "blue":
            GL.glColor3f(0.0, 0.0, 1.0)  # text is blue
        
        elif color == "purple":
            GL.glColor3f(1.0, 0.0, 1.0)  # text is purple

        elif color == "black": 
            GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        
        elif color == "red":
            GL.glColor3f(1.0, 0.0, 0.0) # text is red
        
        elif color == "green":
            GL.glColor3f(0.0, 1.0, 0.0) # text is green

        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))
                