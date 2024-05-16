"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """
    # Error codes
    INVALID_FIRST_CHAR_IN_NAME = 1
    INVALID_CHAR_IN_NAME = 2
    NULL_DEVICE_IN_CONNECT = 3
    INVALID_CONNECT_DELIMITER = 4
    DOUBLE_PUNCTUATION = 5
    MISSING_SEMICOLON = 6
    INVALID_KEYWORD = 7
    INVALID_COMMENT_SYMBOL = 8
    INVALID_BLOCK_ORDER = 9
    MISSING_END_STATEMENT = 10

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
    
    def error(self, error_code):
        self.error_count += 1
        # Error handling?
        print(f"Error code {error_code}: {self.get_error_message(error_code)}")

    def get_error_message(self, error_code):
        error_messages = {
            self.INVALID_FIRST_CHAR_IN_NAME: "Invalid first character in name",
            self.INVALID_CHAR_IN_NAME: "Invalid character in name",
            self.NULL_DEVICE_IN_CONNECT: "CONNECT list cannot have null devices",
            self.INVALID_CONNECT_DELIMITER: "CONNECT list must have individual connections delimited by ','",
            self.DOUBLE_PUNCTUATION: "Double punctuation marks are invalid",
            self.MISSING_SEMICOLON: "Semi-colons are required at the end of each line",
            self.INVALID_KEYWORD: "Missing or misspelled keywords",
            self.INVALID_COMMENT_SYMBOL: "Comments starting or terminating with the wrong symbol",
            self.INVALID_BLOCK_ORDER: "Invalid order of DEFINE, CONNECT, and MONITOR blocks",
            self.MISSING_END_STATEMENT: "No END statement after MONITOR clause"
        }
        return error_messages.get(error_code, "Unknown error")


    # Error detection, throwing relevant rules
    # One function for each non-terminal EBNF rule, otherwise defined in the main parse_network function

    # define all the functions for the non-terminal EBNF rules
    def spec_file(self):
        self.definition()
        while self.scanner.current_symbol == "DEFINE":
            self.definition()
        self.connection()
        self.monitor()
        self.end()

    def definition(self):
        if self.scanner.current_symbol == "DEFINE":
            self.scanner.getsymbol()
            self.name()
            if self.scanner.current_symbol == "AS":
                self.scanner.getsymbol()
                self.device_type()
                if self.scanner.current_symbol == "WITH":
                    self.scanner.getsymbol()
                    self.param_list()
                if self.scanner.current_symbol == ";":
                    self.scanner.getsymbol()
                else:
                    self.error(self.MISSING_SEMICOLON)
            else:
                self.error(self.INVALID_KEYWORD)
        else:
            self.error(self.INVALID_KEYWORD)

    def param_list(self):
        self.param()
        if self.scanner.current_symbol == "=":
            self.scanner.getsymbol()
            self.value()
            while self.scanner.current_symbol == ",":
                self.scanner.getsymbol()
                self.param()
                if self.scanner.current_symbol == "=":
                    self.scanner.getsymbol()
                    self.value()
                else:
                    self.error(self.MISSING_SEMICOLON)
        else:
            self.error(self.MISSING_SEMICOLON)

    def param(self):
        if self.scanner.current_symbol in ["input", "initial", "cycle_rep"]:
            self.scanner.getsymbol()
        else:
            self.error(self.INVALID_KEYWORD)

    def value(self):
        self.digit()
        while self.scanner.current_symbol.isdigit() or self.scanner.current_symbol == ".":
            if self.scanner.current_symbol == ".":
                self.scanner.getsymbol()
            self.digit()

    def connection(self):
        if self.scanner.current_symbol == "CONNECT":
            self.scanner.getsymbol()
            if self.scanner.current_symbol != ";":
                self.con_list()
            if self.scanner.current_symbol == ";":
                self.scanner.getsymbol()
            else:
                self.error(self.MISSING_SEMICOLON)
        else:
            self.error(self.INVALID_KEYWORD)

    def con_list(self):
        self.con()
        if self.scanner.current_symbol == "=":
            self.scanner.getsymbol()
            self.con()
            while self.scanner.current_symbol == ",":
                self.scanner.getsymbol()
                self.con()
                if self.scanner.current_symbol == "=":
                    self.scanner.getsymbol()
                    self.con()
                else:
                    self.error(self.INVALID_CONNECT_DELIMITER)
        else:
            self.error(self.INVALID_CONNECT_DELIMITER)

    def monitor(self):
        if self.scanner.current_symbol == "MONITOR":
            self.scanner.getsymbol()
            if self.scanner.current_symbol != ";":
                self.name()
                while self.scanner.current_symbol == ",":
                    self.scanner.getsymbol()
                    self.name()
            if self.scanner.current_symbol == ";":
                self.scanner.getsymbol()
            else:
                self.error(self.MISSING_SEMICOLON)
        else:
            self.error(self.INVALID_KEYWORD)

    def con(self):
        self.name()
        if self.scanner.current_symbol == ".":
            self.scanner.getsymbol()
            self.notation()
    # Then build logic network
    

    def parse_network(self):
        """Parse the circuit definition file."""
        # Initial design to only analyse definition file (no network/devices)
        
        # Define overall flow, falling relevant non-terminal rules and ending in terminal rules, to be implemented.

        # define name
        # define notation
        # define end
        # define letter
        # define digit
        # define device_type
        # stopping symbol is either , or ; depending on error

        return True
    

