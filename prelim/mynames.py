"""Implements a name table for lexical analysis.

Classes
-------
MyNames - implements a name table for lexical analysis.
"""


class MyNames:

    """Implements a name table for lexical analysis.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    lookup(self, name_string): Returns the corresponding name ID for the
                 given name string. Adds the name if not already present.

    get_string(self, name_id): Returns the corresponding name string for the
                 given name ID. Returns None if the ID is not a valid index.
    """
    

    def __init__(self):
        """Initialise the names list."""

        names_list = []
        self.names_list = names_list 


    def lookup(self, name_string):
        """Return the corresponding name ID for the given name_string.
        If the name string is not present in the names list, add it.
        """

        if isinstance(name_string, str): 
            pass 
        else: 
            raise TypeError('Need String Argument')
        
        curr_list = self.names_list

        if name_string in curr_list: 
            index = curr_list.index(name_string)
            return index
        else: 
            curr_list.append(name_string)
            self.names_list = curr_list

            return curr_list.index(name_string)


    def get_string(self, name_id):
        
        if isinstance(name_id, int): 
            pass 
        else: 
            raise TypeError('Need Integer Argument')

        if name_id >= 0: 
            pass
        else: 
            raise ValueError('Need argument > 0')
        
        curr_list = self.names_list
        try: 
            return curr_list[name_id]
        except: 
            return None
    