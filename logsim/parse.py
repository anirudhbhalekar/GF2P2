"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
from scanner import Symbol, Scanner
from names import Names
from devices import Devices
from monitors import Monitors
from network import Network

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
    EXPECTED_EQUALS = 14

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.error_count = 0
        self.symbol = Symbol()

        self.curr_name = None
        self.curr_type = None 
        self.curr_sub_type = None
        self.curr_ptype = None
        self.curr_pval = None

        self.operators_list = [] # Stores list of (NAME, DEVICE/GATE, DEVICE/GATE TYPE, PARAM_TYPE, PARAM_VAL)
    
    def error(self, error_code, stopping_symbol=None):
        """Print error message and increment error count."""
        self.error_count += 1
        line_number = self.symbol.line_number
        character = self.symbol.character
        error_message = self.get_error_message(error_code)
        print(f"Error Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}, String: {self.names.get_name_string(self.symbol.id) if self.symbol.type == self.scanner.NAME else ''}")
        print(f"Error code {error_code} at line {line_number}, character {character}: {error_message}")
        while (self.symbol.type != stopping_symbol and self.symbol.type != self.scanner.EOF):
            self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.EOF:
            return False

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
            self.INVALID_PIN_REF: "Invalid pin reference",
            self.EXPECTED_EQUALS: "Expected an equals sign"
        }
        return error_messages.get(error_code, "Unknown error")

    def parse_network(self):
        """Parse the circuit definition file."""
        try:
            self.symbol = self.scanner.get_symbol()
            self.spec_file()
            print(self.error_count)
            return self.error_count == 0
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
            return False
        
    # Semantic analysis and network construction
    # def connection(self)

    # Error detection, throwing relevant rules
    # One function for each non-terminal EBNF rule, and each terminal rule calls get_symbol 

    def spec_file(self):
        """Implements rule spec_file = definition, connection, monitor, end;."""
        self.definition({self.scanner.KEYWORD})
        self.connection({self.scanner.KEYWORD})
        self.monitor({self.scanner.KEYWORD})
        self.end({self.scanner.SEMICOLON})

    def definition(self, stopping_symbols):
        """Implements rule definition = "DEFINE", [def_list], ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEFINE_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                self.def_list(stopping_symbols | {self.scanner.SEMICOLON})
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON, stopping_symbols)

    def def_list(self, stopping_symbols):
        """Implements rule def_list = name, "AS", (device | gate), ["WITH", set_param], {",", name, "AS", (device | gate), ["WITH", set_param]};"""
        self.name(stopping_symbols | {self.scanner.COMMA})
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.AS_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.DEVICE:
                self.device(stopping_symbols)
            elif self.symbol.type == self.scanner.GATE:
                self.gate(stopping_symbols)
            else:
                self.error(self.INVALID_KEYWORD, stopping_symbols)
            if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.WITH_ID:
                self.symbol = self.scanner.get_symbol()
                self.set_param(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
            
            self.operators_list.append((self.curr_name, self.curr_type, self.curr_sub_type,
                                        self.curr_ptype, self.curr_pval)) # Add first operator
            
            while self.symbol.type == self.scanner.COMMA:
                print(f"Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}")
                self.symbol = self.scanner.get_symbol()
                self.name(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
                if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.AS_ID:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.DEVICE:
                        self.device(stopping_symbols)
                    elif self.symbol.type == self.scanner.GATE:
                        self.gate(stopping_symbols)
                    else:
                        self.error(self.INVALID_KEYWORD, stopping_symbols)
                    if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.WITH_ID:
                        self.symbol = self.scanner.get_symbol()
                        self.set_param(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
                else:
                    self.error(self.MISSING_SEMICOLON, stopping_symbols)
                
                self.operators_list.append((self.curr_name, self.curr_type, self.curr_sub_type,
                                        self.curr_ptype, self.curr_pval)) # Add subsequent operators

        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)

    def set_param(self, stopping_symbols):
        """Implements rule set_param = param, "=", value, {",", param, "=", value};"""
        self.param(stopping_symbols)
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            self.value(stopping_symbols)
        else:
            self.error(self.EXPECTED_EQUALS, stopping_symbols)

    def param(self, stopping_symbols):
        """Implements rule param = "inputs" | "initial" | "cycle_rep";"""
        if self.symbol.type == self.scanner.PARAM:
            self.curr_ptype = self.names.get_name_string(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)

    def value(self, stopping_symbols):
        """Implements rule value = digit, [{digit}];"""
        # Because of scanner module implementation, we actually check for a format of number
        self.digit(stopping_symbols)

        
    def connection(self, stopping_symbols):
        """Implements rule connection = "CONNECT", [con_list], ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECT_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                self.con_list(stopping_symbols | {self.scanner.SEMICOLON})
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON, stopping_symbols)
        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)

    def con_list(self, stopping_symbols):
        """Implement rule con_list = input_con, "=", output_con, {",", input_con, "=", output_con} ;"""
        self.input_con(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            self.output_con(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                self.input_con(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
                if self.symbol.type == self.scanner.EQUALS:
                    self.symbol = self.scanner.get_symbol()
                    self.output_con(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
                else:
                    self.error(self.INVALID_CONNECT_DELIMITER, stopping_symbols)
        else:
            self.error(self.INVALID_CONNECT_DELIMITER, stopping_symbols)

    def input_con(self, stopping_symbols):
        """Implements rule input_con = name, ".", input_notation;"""
        self.name(stopping_symbols)
        if self.symbol.type == self.scanner.DOT:
            self.symbol = self.scanner.get_symbol()
            self.input_notation(stopping_symbols)
        else:
            self.error(self.EXPECTED_PUNCTUATION, stopping_symbols)
    
    def output_con(self, stopping_symbols):
        """Implements rule output_con = name, [".", output_notation];"""
        self.name(stopping_symbols)
        if self.symbol.type == self.scanner.DOT:
            self.symbol = self.scanner.get_symbol()
            self.output_notation(stopping_symbols)
        elif self.symbol.type == self.scanner.COMMA:
            pass
        elif self.symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error(self.EXPECTED_PUNCTUATION, stopping_symbols)

    def input_notation(self, stopping_symbols):
        """Implements rule input_notation = "I", digit, {digit} | "DATA" | "CLK" | "CLEAR" | "SET";"""
        # Check if proper dtype input, or if not the first letter must be "I", followed by digits (isnumeric)
        if self.symbol.type == self.scanner.DTYPE_INPUT:
            self.symbol = self.scanner.get_symbol()
        elif self.symbol.type == self.scanner.NAME:
            input_string = self.names.get_name_string(self.symbol.id)
            if input_string[0] == "I" and input_string[1:].isnumeric():
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.INVALID_PIN_REF, stopping_symbols)
        else:
            self.error(self.INVALID_PIN_REF, stopping_symbols)

    def output_notation(self, stopping_symbols):
        """Implements rule output_notation =  "Q" | "QBAR" ;"""
        if self.symbol.type == self.scanner.DTYPE_OUTPUT:
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.INVALID_PIN_REF, stopping_symbols)

    def name(self, stopping_symbols):
        """Implements name = letter, {letter | digit};, but name is returned as a full symbol from scanner"""
        if self.symbol.type == self.scanner.NAME:
            self.curr_name = self.names.get_name_string(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.EXPECTED_NAME, stopping_symbols)

    def monitor(self, stopping_symbols):
        """Implements rule monitor = "MONITOR", [output_con, {",", output_con}], ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITOR_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                self.output_con(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
                while self.symbol.type == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    self.output_con(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON, stopping_symbols)
        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)

    def end(self, stopping_symbols):
        """Implements rule end = "END", ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.END_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON, stopping_symbols)
        else:
            self.error(self.MISSING_END_STATEMENT, stopping_symbols)
    
    def digit(self, stopping_symbols):
        """Implements rule digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";"""
        if self.symbol.type == self.scanner.NUMBER:
            self.curr_pval = self.symbol.id
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.EXPECTED_NUMBER, stopping_symbols)

    def device(self, stopping_symbols):
        """Implements rule device = "CLOCK" | "SWITCH" | "DTYPE";"""
        if self.symbol.type == self.scanner.DEVICE:
            self.curr_type = self.scanner.DEVICE
            self.curr_sub_type = self.names.get_name_string(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)

    def gate(self, stopping_symbols):
        """Implement rule gate = "NAND" | "AND" | "OR" | "NOR" | "XOR";"""
        if self.symbol.type == self.scanner.GATE:
            self.curr_type = self.scanner.GATE 
            self.curr_sub_type = self.names.get_name_string(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)

    # Note that letter is already accounted for in the scanner module, where it is checked with isalpha()


if __name__ == "__main__": 

    file_path = "definition_files/test_ex_null.txt"
    names = Names()
    scanner = Scanner(file_path, names)

    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner) 

    print(parser.operators_list)
    parser.parse_network()

    print(parser.operators_list)