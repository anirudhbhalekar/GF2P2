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
    EXPECTED_NAME = 1
    INVALID_CHAR_IN_NAME = 2
    NULL_DEVICE_IN_CONNECT = 3
    INVALID_CONNECT_DELIMITER = 4
    DOUBLE_PUNCTUATION = 5
    MISSING_SEMICOLON = 6
    INVALID_KEYWORD = 7
    INVALID_COMMENT_SYMBOL = 8
    INVALID_BLOCK_ORDER = 9
    MISSING_END_STATEMENT = 10
    EXPECTED_NUMBER = 11
    EXPECTED_PUNCTUATION = 12
    INVALID_PIN_REF = 13

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.error_count = 0
        self.symbol = None
    
    def error(self, error_code):
        """Print error message and increment error count."""
        self.error_count += 1
        line_number = self.symbol.line_number
        character = self.symbol.character
        error_message = self.get_error_message(error_code)
        print(f"Error code {error_code} at line {line_number}, character {character}: {error_message}")

    def get_error_message(self, error_code):
        """Return the error message corresponding to the error code."""
        error_messages = {
            self.EXPECTED_NAME: "Expected a name",
            self.INVALID_CHAR_IN_NAME: "Invalid character in name",
            self.NULL_DEVICE_IN_CONNECT: "CONNECT list cannot have null devices",
            self.INVALID_CONNECT_DELIMITER: "CONNECT list must have individual connections delimited by ','",
            self.DOUBLE_PUNCTUATION: "Double punctuation marks are invalid",
            self.MISSING_SEMICOLON: "Semi-colons are required at the end of each line",
            self.INVALID_KEYWORD: "Missing or misspelled keywords",
            self.INVALID_COMMENT_SYMBOL: "Comments starting or terminating with the wrong symbol",
            self.INVALID_BLOCK_ORDER: "Invalid order of DEFINE, CONNECT, and MONITOR blocks",
            self.MISSING_END_STATEMENT: "No END statement after MONITOR clause",
            self.EXPECTED_NUMBER: "Expected a number",
            self.EXPECTED_PUNCTUATION: "Expected a punctuation mark",
            self.INVALID_PIN_REF: "Invalid pin reference"
        }
        return error_messages.get(error_code, "Unknown error")

    def parse_network(self):
        """Parse the circuit definition file."""
        try:
            self.symbol = self.scanner.get_symbol()
            print(f"Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}")
            self.spec_file()
            return self.error_count == 0
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
            return False
        
    # Semantic analysis and network construction
    # def connection(self)

    # Error detection, throwing relevant rules
    # One function for each non-terminal EBNF rule, and each terminal rule calls get_symbol 

    def spec_file(self):
        """Implements rule spec_file = definition, {definition}, connection, monitor, end;."""
        self.definition()
        self.connection()
        self.monitor()
        self.end()

    def definition(self):
        """Implements rule definition = "DEFINE", name, "AS", device_type, ["WITH", param_list], ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEFINE:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                print(f"Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}")
                self.def_list()
            if self.symbol.type == self.scanner.SEMICOLON:
                print("Semicolon found")
                self.symbol = self.scanner.get_symbol()
                print(f"Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}")
            else:
                self.error(self.MISSING_SEMICOLON)

    def def_list(self):
        """Implements rule def_list = name, "AS", (device | gate), ["WITH", param_list], {",", name, "AS", (device | gate), ["WITH", param_list]};"""
        self.name()
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.AS:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.DEVICE:
                self.device()
            elif self.symbol.type == self.scanner.GATE:
                self.gate()
            else:
                print(f"deflist 0 Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}")
                self.error(self.INVALID_KEYWORD)
            if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.WITH:
                self.symbol = self.scanner.get_symbol()
                self.param_list()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.name()
                if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.AS:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.DEVICE:
                        self.device()
                    elif self.symbol.type == self.scanner.GATE:
                        self.gate()
                    else:
                        print(f"def list 1Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}")
                        self.error(self.INVALID_KEYWORD)
                    if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.WITH:
                        self.symbol = self.scanner.get_symbol()
                        self.param_list()
                    else:
                        self.error(self.MISSING_SEMICOLON)
                else:
                    self.error(self.MISSING_SEMICOLON)
            else:
                print(f"def list Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}")
                self.error(self.INVALID_KEYWORD)
        else:
            self.error(self.INVALID_KEYWORD)

    def param_list(self):
        """Implements rule param_list = param, "=", value, {",", param, "=", value};"""
        self.param()
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            self.value()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.param()
                if self.symbol.type == self.scanner.EQUALS:
                    self.symbol = self.scanner.get_symbol()
                    self.value()
                else:
                    self.error(self.MISSING_SEMICOLON)
        else:
            self.error(self.MISSING_SEMICOLON)

    def param(self):
        """Implements rule param = "input" | "initial" | "cycle_rep";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id in [self.scanner.input_ID, self.scanner.initial_ID, self.scanner.cycle_rep_ID]:
            self.symbol = self.scanner.get_symbol()
        else:
            print(f"param Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}")    
            self.error(self.INVALID_KEYWORD)

    def value(self):
        """Implements rule value = digit, [{digit}];"""
        # Because of scanner module implementation, we actually check for a format of number
        self.digit()

        
    def connection(self):
        """Implements rule connection = "CONNECT", [con_list], ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECT:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                self.con_list()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON)
        else:
            print(f"Connection Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}")
            self.error(self.INVALID_KEYWORD)

    def con_list(self):
        """Implement rule con_list = input_con, "=", output_con, {",", input_con, "=", output_con} ;"""
        self.input_con()
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            self.output_con()
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.input_con()
                if self.symbol.type == self.scanner.EQUALS:
                    self.symbol = self.scanner.get_symbol()
                    self.output_con()
                else:
                    self.error(self.INVALID_CONNECT_DELIMITER)
        else:
            self.error(self.INVALID_CONNECT_DELIMITER)

    def input_con(self):
        """Implements rule input_con = name, ".", input_notation;"""
        self.name()
        if self.symbol.type == self.scanner.DOT:
            self.symbol = self.scanner.get_symbol()
            self.input_notation()
        else:
            self.error(self.EXPECTED_PUNCTUATION)
    
    def output_con(self):
        """Implements rule output_con = name, [".", output_notation];"""
        self.name()
        if self.symbol.type == self.scanner.DOT:
            self.symbol = self.scanner.get_symbol()
            self.output_notation()
        else:
            self.error(self.EXPECTED_PUNCTUATION)

    def input_notation(self):
        """Implements rule input_notation = "I", digit, {digit} | "DATA" | "CLK" | "CLEAR" | "SET";"""
        # Check if proper dtype input, or if not the first letter must be "I", followed by digits (isnumeric)
        if self.symbol.type == self.scanner.DTYPE_INPUT:
            self.symbol = self.scanner.get_symbol()
        elif self.symbol.type == self.scanner.NAME:
            if self.symbol.id[0] == "I" and self.symbol.id[1:].isnumeric():
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.INVALID_PIN_REF)
        else:
            self.error(self.INVALID_PIN_REF)

    def output_notation(self):
        """Implements rule output_notation =  "Q" | "QBAR" ;"""
        if self.symbol.type == self.scanner.DTYPE_OUTPUT:
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.INVALID_PIN_REF)

    def name(self):
        """Implements name = letter, {letter | digit};, but name is returned as a full symbol from scanner"""
        if self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.EXPECTED_NAME)

    def monitor(self):
        """Implements rule monitor = "MONITOR", [name, {",", name}], ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITOR:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                self.name()
                while self.symbol.type == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.name()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON)
        else:
            self.error(self.INVALID_KEYWORD)

    def end(self):
        """Implements rule end = "END", ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.END:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON)
        else:
            print(f"Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}")
            self.error(self.MISSING_END_STATEMENT)
    
    def digit(self):
        """Implements rule digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";"""
        # Because of how get_number is implemented, we check for a number rather than individual digits, but underlying logic is same
        if self.symbol.type == self.scanner.NUMBER:
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.EXPECTED_NUMBER)

    def device(self):
        """Implements rule device = "CLOCK" | "SWITCH" | "DTYPE";"""
        if self.symbol.type == self.scanner.DEVICE:
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.INVALID_KEYWORD)

    def gate(self):
        """Implement rule gate = "NAND" | "AND" | "OR" | "NOR" | "XOR";"""
        if self.symbol.type == self.scanner.GATE:
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.INVALID_KEYWORD)

    # Note that letter is already accounted for in the scanner module, where it is checked with isalpha()