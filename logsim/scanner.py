"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

from devices import Devices
from names import Names

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
        
        self.names = names

        try: 
            file = open(path, 'r')
        except FileNotFoundError: 
            raise FileNotFoundError
        
        if names is None: 
            return
        
        self.file = file
    
        self.line_count = 1
        self.total_char_count = 0
        self.line_char_count = 0

        symbol_type_list = ["COMMA", "SEMICOLON", "EQUALS", "KEYWORD", "NUMBER", "NAME"
                            ,"DOT", "DEVICE", "GATE", "PARAM", "DTYPE_INPUT", "DTYPE_OUTPUT"
                            ,"EOF"]
        
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.EQUALS,
                                self.KEYWORD, self.NUMBER, self.NAME, 
                                self.DOT, self.DEVICE, self.GATE, self.PARAM, 
                                self.DTYPE_INPUT, self.DTYPE_OUTPUT, self.EOF] = symbol_type_list
        
        self.keywords_list = ["DEFINE", "AS", "WITH", "CONNECT", "MONITOR", "END"]
        self.param_list = ["inputs", "initial", "cycle_rep"]
        
        [self.DEFINE_ID, self.AS_ID, self.WITH_ID, self.CONNECT_ID, self.MONITOR_ID,
            self.END_ID] = self.names.lookup(self.keywords_list)   

        [self.input_ID, self.initial_ID, self.cycle_rep_ID] = self.names.lookup(self.param_list)

        self.file.seek(0)
        self.current_character = " "

    def advance(self): 
        """Advances self.current_character"""

        self.file.seek(self.total_char_count)

        next_char = self.file.read(1)
        self.total_char_count += 1
        self.line_char_count  += 1

        if next_char == "\n": 
            self.line_count += 1
            self.line_char_count = 0

        if next_char == "%": 
            next_char = self.file.read(1)
            self.total_char_count += 1
            self.line_char_count  += 1

            if next_char == "\n": 
                    self.line_count += 1
                    self.line_char_count = 0
                    
            while not next_char == "%":

                next_char = self.file.read(1)
                self.total_char_count += 1
                self.line_char_count  += 1

                if next_char == "\n": 
                    self.line_count += 1
                    self.line_char_count = 0
            
            next_char = self.file.read(1)
            self.total_char_count += 1
            self.line_char_count  += 1

        self.current_character = next_char

    def skip_spaces(self): 
        """ Skips spaces to next symbol and sets file pointer"""
        
        if self.current_character.isspace() or self.current_character == "\n":
            self.advance() 

            while self.current_character.isspace(): 
                self.advance()

    def get_name(self): 
        """Gets name (if first char is alphabet - reads until non alnum char is reached)"""

        name_string = ''

        while self.current_character.isalnum() or self.current_character == "_":
            name_string = name_string + self.current_character
            self.advance()
            
        return name_string

    def get_number(self): 
        """Gets number (so appends digits together)"""

        number_string = ''

        while self.current_character.isdigit(): 
            number_string += self.current_character
            self.advance()
        
        return number_string
    
    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""

        # get the next symbol in the file when called - this is fairly simple to implement

        if self.names is None: 
            return 
    
        symbol = Symbol()
        devices = Devices(self.names)

        # Find first non-space char
        self.skip_spaces()
        
        if self.current_character.isalpha(): 
            # This is a name
            name_string = self.get_name()
            if name_string in self.keywords_list: 
                symbol.type = self.KEYWORD
            
            elif name_string in self.param_list: 
                symbol.type = self.PARAM

            elif name_string in devices.device_strings: 
                symbol.type = self.DEVICE
            
            elif name_string in devices.gate_strings: 
                symbol.type = self.GATE

            elif name_string in devices.dtype_input_ids: 
                symbol.type = self.DTYPE_INPUT
            
            elif name_string in devices.dtype_outputs: 
                symbol.type = self.DTYPE_OUTPUT

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

        elif self.current_character == "" and self.total_char_count != 0:
            symbol.type = self.EOF
            self.advance()

        else: 
            # Invalid character just pass over
            self.advance()

        symbol.line_number = self.line_count
        symbol.character = self.line_char_count

        return symbol 
    
    

if __name__ == "__main__": 
    
    names = Names()
    scanner = Scanner("definition_files/test_ex_null.txt", names)

    for i in range(50): 
        sym = scanner.get_symbol()
        print(sym.type)
        print(sym.id) 
        print(sym.line_number)
        print("----")