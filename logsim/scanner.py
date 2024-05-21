"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

from devices import Devices

class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None  
        self.line_number = None
        self.character = None


    # Set symbol properties above
    # Define what types of symbols - names (keywords and names), numbers, punctuation, EOF
    # Initialise key word list (this includes paramter values)

class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""

        try: 
            file = open(path, 'r')
        except FileNotFoundError: 
            raise FileNotFoundError
        
    
        self.file = file
        self.names = names

        self.line_count = 0 

        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.EQUALS,
                                self.KEYWORD, self.NUMBER, self.NAME, 
                                self.DOT, self.DEVICE, self.GATE, self.PARAM, 
                                self.EOF] = range(11)
        
        self.keywords_list = ["DEFINE", "AS", "WITH", "CONNECT", "MONITOR", "END"]
        self.param_list = ["input", "initial", "cycle_rep"]
        
        
        [self.DEFINE_ID, self.AS_ID, self.WITH_ID, self.CONNECT_ID, self.MONITOR_ID,
            self.END_ID] = self.names.lookup(self.keywords_list)   

        [self.input_ID, self.initial_ID, self.cycle_rep_ID] = self.names.lookup(self.param_list)


        self.current_character = ""

        self.file.seek(0)

    def skip_spaces(self): 
        """ Skips spaces to next symbol and sets file pointer"""

        self.advance()
        while self.current_character.isspace(): 
            self.advance()

    def advance(self): 
        """Advances self.current_character"""

        self.current_character = self.file.read(1)

    def get_name(self): 
        """Gets name (if first char is alphabet - reads until non alnum char is reached)"""

        name_string = ''
        name_string += self.current_character

        self.advance()

        while self.current_character.isalnum() or self.current_character == "_": 
            name_string += self.current_character
            self.advance()
            
        return name_string

    def get_number(self): 
        """Gets number (so appends digits together)"""

        number_string = ''
        number_string += self.current_character

        self.advance()

        while self.current_character.isdigit(): 
            number_string += self.current_character
            self.advance()
        
        return number_string
    
    def skip_comment(self): 
        
        self.advance()

        while not self.current_character == "%": 
            self.advance()
        

        
    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""

        # get the next symbol in the file when called - this is fairly simple to implement

        symbol = Symbol()
        devices = Devices(self.names)

        char_count = len(self.file.read())

        # Find first non-space char
        self.skip_spaces()

        if self.current_character.isalpha(): 
            # This is a name

            name_string = self.get_name()

            if name_string in self.keywords_list: 
                symbol.type = self.KEYWORD
            
            elif name_string in self.param_list: 
                symbol.type = self.PARAM

            elif name_string in devices.devices_list: 
                symbol.type = self.DEVICE
            
            elif name_string in devices.gate_types: 
                symbol.type = self.GATE
            else: 
                symbol.type = self.NAME
            
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit(): 
            # This is a number - we get the number string and pass it as the id
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

        elif self.current_character == "%":
            # Comments start and end with a % symbol 
            self.skip_comment()
            self.advance()

        elif self.current_character == "#": 
            #
            while not self.current_character == "\n": 
                self.advance()
            self.advance()

        elif self.current_character == "\n":
            # we update line number only and don't pass a symbol 
            self.line_count += 1

        else: 
            # Invalid character just pass over
            self.advance()

        symbol.line_number = self.line_count
        symbol.character = self.file.tell()

        return symbol 
    