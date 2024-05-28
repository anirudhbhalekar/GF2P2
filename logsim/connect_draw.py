from math import cos, sin, pi
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINE_STRIP
from logic_draw import LogicDrawer


""" Basic Premis of ConnectDrawer is to take a dictionary of connections and 
    draw out all the connections as poly-lines 


"""

class ConnectDrawer:
    """Handle all Connections drawings."""
    
    def __init__(self, connection_def: tuple, domain_dict: dict, padding: float) -> None:
        
        # We receive connection_list in the form (draw_obj, outgoing id, draw_obj, input_id)
        self.connection = connection_def

        # Stores dict of all min_max coords {LogicDraw obj: (bounding box tuple)} for all operators
        self.domain_dict = domain_dict

        # This is the padding when connection line tries to navigate around another bounding box
        self.padding = padding
    
    def draw_connection(self) -> None: 
        
        connection_def = self.connection
        inp_obj = connection_def[0] 
        out_obj = connection_def[2]

        inp_id = connection_def[1]
        out_id = connection_def[3]

        inp_domain = self.domain_dict[inp_obj]

        inp_min_x, inp_max_x = inp_domain[0][0], inp_domain[0][1]
        inp_min_y, inp_max_y = inp_domain[1][0], inp_domain[1][1]

        num_inputs = len(inp_obj.input_list)

        (start_x, start_y) = inp_obj.input_list[inp_id]
        (end_x, end_y) = out_obj.output_list[out_id]

        glColor3f(0.0,0.0,0.0) 
        glBegin(GL_LINE_STRIP)
        glVertex2f(start_x, start_y)
        glVertex2f(end_x, end_y)
        glEnd()
        '''
        if inp_id + 1 < num_inputs/2: 
            # We will go down and to the left
            d_coord = inp_domain[0]
            d_coord = (d_coord[0] - self.padding, d_coord[1] - self.padding *(1 + 0.1 * num_inputs))
        else: 
            # We will go up and to the left
            d_coord = inp_domain[1]
            d_coord = (d_coord[0] - self.padding, d_coord[1] + self.padding *(1 + 0.1 * num_inputs))
        
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(start_x, start_y)
        glVertex2f(d_coord[0], start_y)
        glVertex2f(d_coord[0], d_coord[1])
        glEnd()

        # We are now at one of the bounding box corners
        # Check if there is any bounding box that intersects the ray y coordinate as it travels to 
        curr_coord = d_coord
        nav_tup = self.navigate_intersection(curr_coord, (end_x, end_y), self.domain_dict, inp_obj)
        while nav_tup[0]: 
            # This is the bounds of the problematic object
            new_bounds = nav_tup[1]
            min_x, max_x = new_bounds[0][0], new_bounds[1][0]
            min_y, max_y = new_bounds[0][1], new_bounds[1][1]

            # This is to preserve directionality - aka choose the x bound closest to you
            if abs(curr_coord[0] - min_x) < abs(curr_coord[0] - max_x):
                next_x_coord = min_x - self.padding * 2
                next_y_coord = curr_coord[1]
            else: 
                next_x_coord = max_x + self.padding * 2
                next_y_coord = curr_coord[1]

            # If we have to go up overall we will choose to travel to the top corner

            if end_y < curr_coord[1]: 
                next_seed_y = min_y - self.padding * 2
            else: 
                next_seed_y = max_y + self.padding * 2

            # We now update curr corner
            curr_coord = (next_x_coord, next_seed_y)

            # Draw line between points: curr coord -> closes x value coord of next intersecting box -> down or up to corners with padding -> reset to curr coords
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_LINE_STRIP)
            glVertex2f(curr_coord[0], curr_coord[1])
            glVertex2f(next_x_coord, next_y_coord)
            glVertex2f(next_x_coord, next_seed_y)
            glEnd()
            
            # We call the navigation function again
            nav_tup = self.navigate_intersection(curr_coord, (end_x, end_y), self.domain_dict, inp_obj)
            
        # At this point we are at one of the corners of the bounding box of the output obj itself so we just need two updates
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(curr_coord[0], curr_coord[1])
        glVertex2f(end_x, curr_coord[1])
        glVertex2f(end_x, end_y)
        glEnd()

        '''

        # Should have reached destination element now
    
    def navigate_intersection(self, curr_coord, dest_coord, domain_dict, inp_obj): 
        
        curr_y = curr_coord[1]
        curr_x = curr_coord[0]

        dest_x = dest_coord[0]

        for key in domain_dict.keys(): 
            
            if key is inp_obj: 
                continue

            min_y = domain_dict[key][0][1]
            min_x = domain_dict[key][0][0]

            max_y = domain_dict[key][1][1]
            max_x = domain_dict[key][1][0]

            if min_y <= curr_y and max_y >= curr_y: 
                # Check if there is an object that intersects this y ray 
                if min_x <= max(curr_x, dest_x) and max_x >= min(dest_x, curr_x): 
                    # Check if it lies between the two (src and dest) x values
                    return (True, domain_dict[key])

        return (False, None)




            



        