"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


class Names:

    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    

    def __init__(self):
        """Initialise names list."""

        self.error_code_count = 0  # how many error codes have been declared
        names_list = []
        self.name_table = names_list

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """

        # same as in prelim exercise - if name_string in the table, return position, else None
        
        if not isinstance(name_string, str): 
            raise TypeError('Need String argument')
        
        curr_list = self.name_table

        if name_string in curr_list: 
            return curr_list.index(name_string)
        else: 
            return None


    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """

        # Call query each time for name in name_string_list, if None - add it and return the length of list (at point)

        id_arr = []
        if not isinstance(name_string_list, list): 
            raise TypeError("Name list argument must be a list") 
        
        for name in name_string_list: 

            if not isinstance(name, str): 
                raise TypeError("Names must be strings")
            
            id = self.query(name)
            if id is None: 
                curr_list = self.name_table
                id = len(curr_list)
                curr_list.append(name)
                self.name_table = curr_list
                
            id_arr.append(id) 

        return id_arr


    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        # return string from name table
        if not isinstance(name_id, int): 
            raise TypeError('Name ID must be an integer')
        
        curr_list = self.name_table

        if name_id < len(curr_list): 
            return curr_list[name_id]
        else: 
            return None
        
