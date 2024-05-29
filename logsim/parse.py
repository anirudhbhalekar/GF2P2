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

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        
        self.names = names
        [self.EXPECTED_NAME, self.INVALID_CHAR_IN_NAME, self.NULL_DEVICE_IN_CONNECT, 
         self.INVALID_CONNECT_DELIMITER, self.DOUBLE_PUNCTUATION, self.MISSING_SEMICOLON, 
         self.INVALID_KEYWORD, self.INVALID_COMMENT_SYMBOL, self.INVALID_BLOCK_ORDER, 
         self.MISSING_END_STATEMENT, self.EXPECTED_NUMBER, self.EXPECTED_PUNCTUATION, 
         self.INVALID_PIN_REF, self.EXPECTED_EQUALS] = self.names.unique_error_codes(14)
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.error_count = 0
        self.symbol = Symbol()
    

    def error(self, error_code, stopping_symbols=None):
        """Print error message and increment error count."""
        # Note that if there is a syntax error before a semantic one, the semantic error will not be printed
        self.error_count += 1
        line_number = self.symbol.line_number
        character = self.symbol.character
        error_message = self.get_error_message(error_code)
        print(f"Error code {error_code} at line {line_number}, character {character}: {error_message}")
        print(f"Symbol type: {self.symbol.type}, Symbol id: {self.symbol.id}, String: {self.names.get_name_string(self.symbol.id) if self.symbol.type == self.scanner.NAME or self.symbol.type == self.scanner.KEYWORD else ''}")
        while (self.symbol.type not in stopping_symbols and self.symbol.type != self.scanner.EOF):
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
            self.INVALID_KEYWORD: "Invalid keyword, could be missing or misspelled",
            self.INVALID_COMMENT_SYMBOL: "Comments starting or terminating with the wrong symbol",
            self.INVALID_BLOCK_ORDER: "Invalid order of DEFINE, CONNECT, and MONITOR blocks",
            self.MISSING_END_STATEMENT: "No END statement after MONITOR clause",
            self.EXPECTED_NUMBER: "Expected a number",
            self.EXPECTED_PUNCTUATION: "Expected a punctuation mark",
            self.INVALID_PIN_REF: "Invalid pin reference",
            self.EXPECTED_EQUALS: "Expected an equals sign",
            # Network errors
            self.network.DEVICE_ABSENT: "Device absent",
            self.network.INPUT_CONNECTED: "Input is already connected",
            self.network.INPUT_TO_INPUT: "Cannot connect an input to another input",
            self.network.PORT_ABSENT: "Port absent",
            self.network.OUTPUT_TO_OUTPUT: "Cannot connect an output to another output",
            # Device errors
            self.devices.DEVICE_PRESENT: "Device already present",
            self.devices.NO_QUALIFIER: "Qualifier is missing",
            self.devices.INVALID_QUALIFIER: "Invalid qualifier",
            self.devices.QUALIFIER_PRESENT: "Qualifier should not be present",
            self.devices.BAD_DEVICE: "Invalid device type",
            # Monitor errors
            self.monitors.NOT_OUTPUT: "Device output not found",
            self.monitors.MONITOR_PRESENT: "Monitor already present"
            }
        return error_messages.get(error_code, "Unknown error")


    def parse_network(self):
        """Parse the circuit definition file."""
        try:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.EOF:
                return False
            self.spec_file()
            print(f"Total Error Count:{self.error_count}")
            return self.error_count == 0
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
            return False
        

    def spec_file(self):
        """Implements rule spec_file = definition, connection, monitor, end;."""
        self.definition({self.scanner.SEMICOLON})
        self.connection({self.scanner.KEYWORD})
        self.monitor({self.scanner.KEYWORD})
        self.end({self.scanner.SEMICOLON})


    def definition(self, stopping_symbols):
        """Implements rule definition = "DEFINE", [def_list], ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEFINE_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                self.def_list(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
                # While the symbol is not CONNECT, keep search for next symbol - this ignores any extra definitions after the first SEMICOLON
                while self.symbol.type != self.scanner.EOF and self.symbol.id != self.scanner.CONNECT_ID:
                    self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON, stopping_symbols)


    def def_list(self, stopping_symbols):
        """Implements rule def_list = name, "AS", (device | gate), ["WITH", set_param], {",", name, "AS", (device | gate), ["WITH", set_param]};"""
        device_id = self.name(stopping_symbols | {self.scanner.COMMA})
        # If invalid keyword, skip to next definition
        if device_id is not None:
            if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.AS_ID:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.DEVICE:
                    device_kind = self.device(stopping_symbols)
                elif self.symbol.type == self.scanner.GATE:
                    device_kind = self.gate(stopping_symbols)
                else:
                    self.error(self.INVALID_KEYWORD, stopping_symbols)
                if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.WITH_ID:
                    self.symbol = self.scanner.get_symbol()
                    device_property = self.set_param(stopping_symbols)
                else:
                    device_property = None
            else:
                self.error(self.INVALID_KEYWORD, stopping_symbols)
            # Make device 
            if self.error_count == 0:
                error_type = self.devices.make_device(device_id, device_kind, device_property)
                if error_type != self.devices.NO_ERROR:
                    self.error(error_type, stopping_symbols)

            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                device_id = self.name(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
                if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.AS_ID:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.DEVICE:
                        device_kind = self.device(stopping_symbols)
                    elif self.symbol.type == self.scanner.GATE:
                        device_kind = self.gate(stopping_symbols)
                    else:
                        self.error(self.INVALID_KEYWORD, stopping_symbols)
                    if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.WITH_ID:
                        self.symbol = self.scanner.get_symbol()
                        device_property = self.set_param(stopping_symbols)
                    else:
                        device_property = None
                else:
                    self.error(self.MISSING_SEMICOLON, stopping_symbols)
                # Make device
                if self.error_count == 0:
                    error_type = self.devices.make_device(device_id, device_kind, device_property)
                    if error_type != self.devices.NO_ERROR:
                        self.error(error_type, stopping_symbols)

        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)


    def set_param(self, stopping_symbols):
        """Implements rule set_param = param, "=", value;"""
        # Only one param for different devices, so just return the param value
        if self.param(stopping_symbols):
            if self.symbol.type == self.scanner.EQUALS:
                self.symbol = self.scanner.get_symbol()
                device_property = self.value(stopping_symbols)
                return device_property
            else:
                self.error(self.EXPECTED_EQUALS, stopping_symbols)
                return None


    def param(self, stopping_symbols):
        """Implements rule param = "inputs" | "initial" | "cycle_rep";"""
        if self.symbol.type == self.scanner.PARAM:
            self.symbol = self.scanner.get_symbol()
            return True
        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)
            return False

    def value(self, stopping_symbols):
        """Implements rule value = digit, [{digit}];"""
        # Because of scanner module implementation, we actually check for a format of number
        device_property = self.digit(stopping_symbols)
        return device_property

        
    def connection(self, stopping_symbols):
        """Implements rule connection = "CONNECT", [con_list], ";";"""
        if self.symbol.type == self.scanner.EOF:
            return
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECT_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                self.con_list(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON, stopping_symbols)
        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)
            # Keep searching until EOF or CONNECT
            while self.symbol.type != self.scanner.EOF and self.symbol.type != self.scanner.KEYWORD:
                self.symbol = self.scanner.get_symbol()


    def con_list(self, stopping_symbols):
        """Implement rule con_list = input_con, "=", output_con, {",", input_con, "=", output_con} ;"""
        in_device_id, in_port_id = self.input_con(stopping_symbols)
        if in_device_id is not None and in_port_id is not None:
            if self.symbol.type == self.scanner.EQUALS:
                self.symbol = self.scanner.get_symbol()
                out_device_id, out_port_id = self.output_con(stopping_symbols)
            else:
                self.error(self.INVALID_CONNECT_DELIMITER, stopping_symbols)
                # Build network
            if self.error_count == 0:
                error_type = self.network.make_connection(in_device_id, in_port_id, out_device_id, out_port_id)
                if error_type != self.network.NO_ERROR:
                    # Find the corresponding error code 
                    self.error(error_type, stopping_symbols)
            
        # Continue with more connections
        while self.symbol.type == self.scanner.COMMA:
            self.symbol = self.scanner.get_symbol()
            in_device_id, in_port_id = self.input_con(stopping_symbols)
            if in_device_id is not None and in_port_id is not None:
                if self.symbol.type == self.scanner.EQUALS:
                    self.symbol = self.scanner.get_symbol()
                    out_device_id, out_port_id = self.output_con(stopping_symbols)
                else:
                    self.error(self.INVALID_CONNECT_DELIMITER, stopping_symbols)
                if self.error_count == 0:
                    error_type = self.network.make_connection(in_device_id, in_port_id, out_device_id, out_port_id)
                    if error_type != self.network.NO_ERROR:
                        self.error(error_type, stopping_symbols)


    def input_con(self, stopping_symbols):
        """Implements rule input_con = name, ".", input_notation;"""
        in_device_id = self.name(stopping_symbols)
        if in_device_id is not None:
            if self.symbol.type == self.scanner.DOT:
                self.symbol = self.scanner.get_symbol()
                in_port_id = self.input_notation(stopping_symbols)
                return in_device_id, in_port_id
            else:
                self.error(self.EXPECTED_PUNCTUATION, stopping_symbols)
                return None, None
        
    
    def output_con(self, stopping_symbols):
        """Implements rule output_con = name, [".", output_notation];"""
        out_device_id = self.name(stopping_symbols)
        if out_device_id is not None:
            if self.symbol.type == self.scanner.DOT:
                self.symbol = self.scanner.get_symbol()
                out_port_id = self.output_notation(stopping_symbols)
            elif self.symbol.type == self.scanner.COMMA:
                # If no dot, the output id is actually none according to the definition in devices
                out_port_id = None
            elif self.symbol.type == self.scanner.SEMICOLON:
                out_port_id = None
            else:
                self.error(self.EXPECTED_PUNCTUATION, stopping_symbols)
                return None, None
            return out_device_id, out_port_id
        return None, None


    def input_notation(self, stopping_symbols):
        """Implements rule input_notation = "I", digit, {digit} | "DATA" | "CLK" | "CLEAR" | "SET";"""
        # Check if proper dtype input, or if not the first letter must be "I", followed by digits (isnumeric)
        if self.symbol.type == self.scanner.DTYPE_INPUT:
            in_port_id = self.symbol.id
            self.symbol = self.scanner.get_symbol()
        elif self.symbol.type == self.scanner.NAME:
            input_string = self.names.get_name_string(self.symbol.id)
            if input_string[0] == "I" and input_string[1:].isnumeric():
                in_port_id = self.symbol.id
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.INVALID_PIN_REF, stopping_symbols)
                return None
        else:
            self.error(self.INVALID_PIN_REF, stopping_symbols)
            return None
        return in_port_id


    def output_notation(self, stopping_symbols):
        """Implements rule output_notation =  "Q" | "QBAR" ;"""
        if self.symbol.type == self.scanner.DTYPE_OUTPUT:
            out_port_id = self.symbol.id
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.INVALID_PIN_REF, stopping_symbols)
            return None
        return out_port_id

    def name(self, stopping_symbols):
        """Implements name = letter, {letter | digit};, but name is returned as a full symbol from scanner"""
        if self.symbol.type == self.scanner.NAME:
            name = self.symbol.id
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.EXPECTED_NAME, stopping_symbols)
            return None
        return name


    def monitor(self, stopping_symbols):
        """Implements rule monitor = "MONITOR", [output_con, {",", output_con}], ";";"""
        if self.symbol.type == self.scanner.EOF:
            return
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITOR_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                device_id, output_id = self.output_con(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
                if self.error_count == 0:
                    error_type = self.monitors.make_monitor(device_id, output_id)
                    if error_type != self.monitors.NO_ERROR:
                        self.error(error_type, stopping_symbols)
                while self.symbol.type == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    device_id, output_id = self.output_con(stopping_symbols | {self.scanner.COMMA, self.scanner.SEMICOLON})
                    if self.error_count == 0:
                        error_type = self.monitors.make_monitor(device_id, output_id)
                        if error_type != self.monitors.NO_ERROR:
                            self.error(error_type, stopping_symbols)
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON, stopping_symbols)
        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)


    def end(self, stopping_symbols):
        """Implements rule end = "END", ";";"""
        if self.symbol.type == self.scanner.EOF:
            return
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
            value = self.symbol.id
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.EXPECTED_NUMBER, stopping_symbols)
            return None
        # Convert str to int
        return int(value)


    def device(self, stopping_symbols):
        """Implements rule device = "CLOCK" | "SWITCH" | "DTYPE";"""
        if self.symbol.type == self.scanner.DEVICE:
            device_kind = self.symbol.id
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)
        return device_kind


    def gate(self, stopping_symbols):
        """Implement rule gate = "NAND" | "AND" | "OR" | "NOR" | "XOR";"""
        if self.symbol.type == self.scanner.GATE:
            device_kind = self.symbol.id
            self.symbol = self.scanner.get_symbol()
        else:
            self.error(self.INVALID_KEYWORD, stopping_symbols)
        return device_kind

    # Note that letter is already accounted for in the scanner module, where it is checked with isalpha()

