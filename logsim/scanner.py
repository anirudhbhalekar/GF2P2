"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner
    Reads the definition file and translates characters into symbols.
Symbol
    Encapsulates a symbol and stores its properties.
"""

from devices import Devices

class Symbol:
    """Encapsulate a symbol and store its properties."""

    def __init__(self):
        """Initialize symbol properties."""
        self.type = None
        self.id = None  
        self.line_number = None
        self.character = None
        self.length = None


class Scanner:
    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path : str
        Path to the circuit definition file.
    names : Names
        Instance of the names.Names() class.
    """

    def __init__(self, path, names):
        """Open specified file and initialize reserved words and IDs."""
        self.names = names

        try: 
            self.file = open(path, 'r')
        except FileNotFoundError: 
            raise FileNotFoundError

        if names is None: 
            return
        
        self.line_count = 1
        self.total_char_count = 0
        self.line_char_count = 0
        self.symbol_char_count = 0

        self.symbol_type_list = [
            "COMMA", "SEMICOLON", "EQUALS", "KEYWORD", "NUMBER", "NAME",
            "DOT", "DEVICE", "GATE", "PARAM", "DTYPE_INPUT", "DTYPE_OUTPUT", "EOF"
        ]

        self.COMMA, self.SEMICOLON, self.EQUALS, self.KEYWORD, self.NUMBER, \
        self.NAME, self.DOT, self.DEVICE, self.GATE, self.PARAM, \
        self.DTYPE_INPUT, self.DTYPE_OUTPUT, self.EOF = self.symbol_type_list

        self.keywords_list = ["DEFINE", "AS", "WITH", "CONNECT", "MONITOR", "END"]
        self.param_list = ["inputs", "initial", "cycle_rep", "rc_cycles"]

        self.DEFINE_ID, self.AS_ID, self.WITH_ID, self.CONNECT_ID, \
        self.MONITOR_ID, self.END_ID = self.names.lookup(self.keywords_list)

        self.inputs_ID, self.initial_ID, self.cycle_rep_ID, self.rc_cycles_ID = \
            self.names.lookup(self.param_list)

        self.file.seek(0)
        self.current_character = ""
        self.advance()

    def read_next_char(self):
        """Read the next character from the file."""
        next_char = self.file.read(1)
        self.total_char_count += 1
        self.line_char_count += 1
        if self.current_character == "\n":
            self.line_count += 1
            self.line_char_count = 0
        self.current_character = next_char

    def advance(self):
        """Advance the current character."""
        self.file.seek(self.total_char_count)
        self.read_next_char()
        self.symbol_char_count += 1

        if self.current_character == "%":
            self.read_next_char()
            while self.current_character != "%" and self.current_character != "":
                self.read_next_char()
            self.read_next_char()

    def skip_spaces(self):
        """Skip spaces to the next symbol and set the file pointer."""
        space_count = 0
        if self.current_character.isspace() or self.current_character == "\n":
            self.advance() 
            space_count += 1

            while self.current_character.isspace(): 
                self.advance()
                space_count += 1
        return space_count

    def get_name(self):
        """Get name if the first char is alphabet and read until non-alnum char is reached."""
        name_string = ''

        while self.current_character.isalnum() or self.current_character == "_":
            name_string += self.current_character
            self.advance()
            
        return name_string

    def get_number(self):
        """Get number by appending digits together."""
        number_string = ''

        while self.current_character.isdigit(): 
            number_string += self.current_character
            self.advance()
        
        return number_string
    
    def get_line(self, line_number):
        """Return the line of the file at the given line number."""
        self.file.seek(0)
        line_number_count = 1
        line = ""
        while line_number_count != line_number: 
            line = self.file.readline()
            line_number_count += 1
        line = self.file.readline()
        # remove newline
        line = line[:-1]
        return line
        
    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        if self.names is None: 
            return 
        
        symbol = Symbol()
        devices = Devices(self.names)

        space_count = self.skip_spaces()
        
        if self.current_character.isalpha(): 
            name_string = self.get_name()
            if name_string in self.keywords_list: 
                symbol.type = self.KEYWORD
            elif name_string in self.param_list: 
                symbol.type = self.PARAM
            elif name_string in devices.device_strings: 
                symbol.type = self.DEVICE
            elif name_string in devices.gate_strings: 
                symbol.type = self.GATE
            elif name_string in devices.dtype_inputs: 
                symbol.type = self.DTYPE_INPUT
            elif name_string in devices.dtype_outputs: 
                symbol.type = self.DTYPE_OUTPUT
            else: 
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit(): 
            number_string = self.get_number()
            symbol.id = number_string
            symbol.type = self.NUMBER
        
        elif self.current_character == "=": 
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == ",": 
            symbol.type = self.COMMA
            self.advance()
        
        elif self.current_character == ".": 
            symbol.type = self.DOT
            self.advance()

        elif self.current_character == ";": 
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == "" and self.total_char_count != 0:
            symbol.type = self.EOF
            self.advance()

        else: 
            self.advance()

        symbol.line_number = self.line_count
        symbol.character = self.line_char_count
        symbol.length = self.symbol_char_count - space_count

        self.symbol_char_count = 0

        return symbol 

