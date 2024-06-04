"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""

import gettext
import sys
import os
# Initialize gettext translation
locale = "en"
if len(sys.argv) > 2:
    if sys.argv[2] == "el" or sys.argv[2] == "el_GR" or sys.argv[2] == "el_GR.utf8":
        locale = "el_GR.utf8"
        #print("Locale: Ελληνικα")
    elif sys.argv[2] == "en" or sys.argv[2] == "en_GB" or sys.argv[2] == "en_GB.utf8":
        print("Locale: English")
    else:
        #print("Locale unknown, defaulting to English")
        pass
if os.getenv("LANG") == "el_GR.UTF-8":
    locale = "el_GR.utf8"
    #print("Greek system language detected")
elif os.getenv("LANG") == "en_US.UTF-8" or os.getenv("LANG") == "en_GB.UTF-8":
    #print("Your system language is English.")
    locale = "en_GB.utf8"
else:
    #print("Attention - your system language is neither English nor Greek. Logsim will run in English.")
    locale = "en_GB.utf8"
lang = gettext.translation("logsim", localedir=os.path.join(os.path.dirname(__file__), 'locales'), languages=[locale], fallback=True)
lang.install()
_ = lang.gettext

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
        self.error_code_count = 0
        self.name_table = []

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError(_("Expected num_error_codes to be an integer."))
        self.error_code_count += num_error_codes
        return list(range(self.error_code_count - num_error_codes,
                          self.error_code_count))

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """

        # same as in prelim exercise - if name_string in the table, return position, else None
        if not isinstance(name_string, str):
            raise TypeError(_('Need String argument'))
        if name_string == "":
            raise ValueError(_('Null Strings are not accepted'))

        if name_string in self.name_table:
            return self.name_table.index(name_string)
        return None


    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """

        # Call query each time for name in name_string_list, if None - add it and return the length of list (at point)
        if not isinstance(name_string_list, list):
            raise TypeError(_("Name list argument must be a list"))

        id_arr = []
        for name in name_string_list:
            if not isinstance(name, str):
                raise TypeError(_("Names must be strings"))

            name_id = self.query(name)
            if name_id is None:
                name_id = len(self.name_table)
                self.name_table.append(name)
            id_arr.append(name_id)

        return id_arr


    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        # return string from name table
        if not isinstance(name_id, int):
            raise TypeError(_('Name ID must be an integer'))
        if name_id < 0:
            raise ValueError(_("Integer must be greater than or equal to 0"))

        if name_id < len(self.name_table):
            return self.name_table[name_id]
        return None
        
