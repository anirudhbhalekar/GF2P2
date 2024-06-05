"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
from scanner import Symbol
import gettext
import sys
import os
'''
# Initialize gettext translation
locale = "en"
if len(sys.argv) > 2:
    if sys.argv[2] == "el" or sys.argv[2] == "el_GR" or sys.argv[2] == "el_GR.utf8":
        locale = "el_GR.utf8"
        #print("Locale: Ελληνικα")
    elif sys.argv[2] == "en" or sys.argv[2] == "en_GB" or sys.argv[2] == "en_GB.utf8":
        #print("Locale: English")
        pass
    else:
        #print("Locale unknown, defaulting to English")
        pass
'''
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
        [self.EXPECTED_NAME, self.INVALID_CONNECT_DELIMITER, self.MISSING_SEMICOLON, 
         self.INVALID_KEYWORD, self.MISSING_END_STATEMENT, self.EXPECTED_NUMBER, self.EXPECTED_DOT, 
         self.INVALID_PIN_REF, self.EXPECTED_EQUALS, self.EXPECTED_DEFINE, self.EXPECTED_CONNECT, 
         self.EXPECTED_MONITOR, self.EXPECTED_END, self.INVALID_PARAM, self.MISSING_DTYPE_INPUTS, 
         self.PASSED_KEYWORD, self.PASSED_DEVICE, self.PASSED_GATE, self.EMPTY_FILE,
         self.EXPECTED_DEVICE_OR_GATE] = self.names.unique_error_codes(20)
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
        symbol_length = self.symbol.length

        error_message = self.get_error_message(error_code, self.symbol.type)
        error_line = self.scanner.get_line(line_number)

        print(error_line) # no translation needed for this
        # print spaces and then a ^ under the character
        print(" " * (character - symbol_length) + "^")
        print(_("Error at line {line_number}, character {character}: {error_message}").format(
        error_code=error_code, line_number=line_number, character=character - symbol_length, error_message=error_message))
        
        if self.symbol.type == self.scanner.EOF:
            return False

        while (self.symbol.type not in stopping_symbols and self.symbol.type != self.scanner.EOF):
            self.symbol = self.scanner.get_symbol()


    def get_error_message(self, error_code, symbol_type):
        """Return the error message corresponding to the error code."""
        error_messages = {
            self.EXPECTED_NAME: _("Expected a name"),
            self.INVALID_CONNECT_DELIMITER: _("CONNECT list must have individual connections delimited by ','"),
            self.MISSING_SEMICOLON: _("Semi-colons are required at the end of each line"),
            self.INVALID_KEYWORD: _("Invalid keyword, could be missing or misspelled"),
            self.MISSING_END_STATEMENT: _("No END statement after MONITOR clause"),
            self.EXPECTED_NUMBER: _("Expected a number"),
            self.EXPECTED_DOT: _("Inputs should be specified - expected a dot"),
            self.INVALID_PIN_REF: _("Invalid pin reference"),
            self.EXPECTED_EQUALS: _("Expected an equals sign"),
            self.EXPECTED_DEFINE: _("Expected a DEFINE statement first"),
            self.EXPECTED_CONNECT: _("Expected a CONNECT statement second"),
            self.EXPECTED_MONITOR: _("Expected a MONITOR statement third"),
            self.EXPECTED_END: _("Expected an END statement fourth"),
            self.INVALID_PARAM: _("Invalid parameter for device"),
            self.MISSING_DTYPE_INPUTS: _("DTYPE device must have 4 inputs"),
            self.PASSED_KEYWORD: _("Passed a keyword when a name was expected"),
            self.PASSED_DEVICE: _("Passed a device when a name was expected"),
            self.PASSED_GATE: _("Passed a gate when a name was expected"),
            self.EMPTY_FILE: _("No symbols detected, either an empty file or all comments"),
            self.EXPECTED_DEVICE_OR_GATE: _("Expected a device or gate"),
            # Network errors
            self.network.DEVICE_ABSENT: _("Device absent"),
            self.network.INPUT_CONNECTED: _("Input is already connected"),
            self.network.INPUT_TO_INPUT: _("Cannot connect an input to another input"),
            self.network.PORT_ABSENT: _("Port absent"),
            self.network.OUTPUT_TO_OUTPUT: _("Cannot connect an output to another output"),
            # Device errors
            self.devices.DEVICE_PRESENT: _("Device already present"),
            self.devices.NO_QUALIFIER: _("Qualifier is missing"),
            self.devices.INVALID_QUALIFIER: _("Invalid qualifier"),
            self.devices.QUALIFIER_PRESENT: _("Qualifier should not be present"),
            self.devices.BAD_DEVICE: _("Invalid device type"),
            # Monitor errors
            self.monitors.NOT_OUTPUT: _("Device output not found"),
            self.monitors.MONITOR_PRESENT: _("Monitor already present")
        }
        if symbol_type == None:
            return f"Invalid symbol type, {error_messages.get(error_code, _('Unknown error'))}"
        return error_messages.get(error_code, _("Unknown error"))


    def parse_network(self):
        """Parse the circuit definition file."""
        try:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.EOF:
                self.error(self.EMPTY_FILE)
                print(_("Total Error Count: {error_count}").format(error_count=self.error_count))
                return False
            self.spec_file()
            print(_("Total Error Count: {error_count}").format(error_count=self.error_count))
            return self.error_count == 0
        except SyntaxError as e:
            print(_("Syntax Error: {error}").format(error=e))
            return False
        

    def spec_file(self):
        """Implements rule spec_file = definition, connection, monitor, end;."""
        self.definition({self.scanner.SEMICOLON})
        self.connection({self.scanner.SEMICOLON})
        self.monitor({self.scanner.SEMICOLON})
        self.end({self.scanner.SEMICOLON})


    def definition(self, stopping_symbols):
        """Implements rule definition = "DEFINE", [def_list], ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEFINE_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                self.def_list(stopping_symbols | {self.scanner.COMMA})
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON, stopping_symbols)
        else:
            self.error(self.EXPECTED_DEFINE, stopping_symbols)
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()


    def def_list(self, stopping_symbols):
        """Implements rule def_list = name, "AS", (device | gate), ["WITH", set_param], {",", name, "AS", (device | gate), ["WITH", set_param]};"""
        device_id = self.name(stopping_symbols)
        # If invalid keyword, skip to while loop for definition
        if device_id is not None:
            if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.AS_ID:
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.DEVICE:
                    device_kind = self.device(stopping_symbols)
                elif self.symbol.type == self.scanner.GATE:
                    device_kind = self.gate(stopping_symbols)
                else:
                    self.error(self.EXPECTED_DEVICE_OR_GATE, stopping_symbols | {self.scanner.COMMA})
                if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.WITH_ID:
                    self.symbol = self.scanner.get_symbol()
                    device_property = self.set_param(device_kind, stopping_symbols)
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
            if device_id is not None:
                if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.AS_ID:
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.type == self.scanner.DEVICE:
                        device_kind = self.device(stopping_symbols)
                    elif self.symbol.type == self.scanner.GATE:
                        device_kind = self.gate(stopping_symbols)
                    else:
                        self.error(self.EXPECTED_DEVICE_OR_GATE, stopping_symbols | {self.scanner.COMMA})
                    if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.WITH_ID:
                        self.symbol = self.scanner.get_symbol()
                        device_property = self.set_param(device_kind, stopping_symbols)
                    else:
                        device_property = None
                else:
                    self.error(self.INVALID_KEYWORD, stopping_symbols)
                # Make device
                if self.error_count == 0:
                    error_type = self.devices.make_device(device_id, device_kind, device_property)
                    if error_type != self.devices.NO_ERROR:
                        self.error(error_type, stopping_symbols)


    def set_param(self, device_kind, stopping_symbols):
        """Implements rule set_param = param, "=", value;"""
        # Only one param for different devices, so just return the param value
        if self.param(device_kind, stopping_symbols):
            if self.symbol.type == self.scanner.EQUALS:
                self.symbol = self.scanner.get_symbol()
                device_property = self.value(stopping_symbols)
                return device_property
            else:
                self.error(self.EXPECTED_EQUALS, stopping_symbols)
                return None
        else:
            if self.error_count == 0:
                self.error(self.INVALID_PARAM, stopping_symbols)
            return None


    def param(self, device_kind, stopping_symbols):
        """Implements rule param = "inputs" | "initial" | "cycle_rep" | rc_cycles;"""
        if self.symbol.type == self.scanner.PARAM:
            # The scanner module does 
            device_string = self.names.get_name_string(device_kind)
            if device_string in self.devices.gate_strings and self.symbol.id == self.scanner.inputs_ID:
                self.symbol = self.scanner.get_symbol()
                return True
            elif device_string == "SWITCH" and self.symbol.id == self.scanner.initial_ID:
                self.symbol = self.scanner.get_symbol()
                return True
            elif device_string == "CLOCK" and self.symbol.id == self.scanner.cycle_rep_ID:
                self.symbol = self.scanner.get_symbol()
                return True
            elif device_string == "RC" and self.symbol.id == self.scanner.rc_cycles_ID:
                self.symbol = self.scanner.get_symbol()
                return True
            else:
                self.error(self.INVALID_PARAM, stopping_symbols)
                return False
        else:
            self.error(self.INVALID_PARAM, stopping_symbols)
            return False

    def value(self, stopping_symbols):
        """Implements rule value = digit, [{digit}];"""
        # Because of scanner module implementation, we actually check for a format of number
        device_property = self.digit(stopping_symbols)
        return device_property

        
    def connection(self, stopping_symbols):
        """Implements rule connection = "CONNECT", [con_list], ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECT_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.SEMICOLON:
                self.con_list(stopping_symbols | {self.scanner.COMMA})
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                print("hi")
                self.error(self.MISSING_SEMICOLON, stopping_symbols)
        else:
            self.error(self.EXPECTED_CONNECT, stopping_symbols)
            if self.symbol.type == self.scanner.SEMICOLON:
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

        # If DTYPE exists, check it has all 4 inputs: we enforce all 4
        d_type_devices = self.devices.find_devices(self.devices.D_TYPE)
        for device_id in d_type_devices:
            device = self.devices.get_device(device_id)
            if any(value is None for value in device.inputs.values()) and self.error_count == 0:
                self.error(self.MISSING_DTYPE_INPUTS, stopping_symbols)


    def input_con(self, stopping_symbols):
        """Implements rule input_con = name, ".", input_notation;"""
        in_device_id = self.name(stopping_symbols)
        if in_device_id is not None:
            if self.symbol.type == self.scanner.DOT:
                self.symbol = self.scanner.get_symbol()
                in_port_id = self.input_notation(stopping_symbols)
                return in_device_id, in_port_id
            else:
                self.error(self.EXPECTED_DOT, stopping_symbols)
                return None, None
        else:
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
                self.error(self.EXPECTED_DOT, stopping_symbols)
                return None, None
            return out_device_id, out_port_id
        else:
            self.error(self.EXPECTED_NAME, stopping_symbols)
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
        elif self.symbol.type == self.scanner.KEYWORD:
            self.error(self.PASSED_KEYWORD, stopping_symbols)
            return None
        elif self.symbol.type == self.scanner.DEVICE:
            self.error(self.PASSED_DEVICE, stopping_symbols)
            return None
        elif self.symbol.type == self.scanner.GATE:
            self.error(self.PASSED_GATE, stopping_symbols)
            return None
        else:
            self.error(self.EXPECTED_NAME, stopping_symbols)
            return None
        return name


    def monitor(self, stopping_symbols):
        """Implements rule monitor = "MONITOR", [output_con, {",", output_con}], ";";"""
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
            self.error(self.EXPECTED_MONITOR, stopping_symbols)
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()


    def end(self, stopping_symbols):
        """Implements rule end = "END", ";";"""
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.END_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
            else:
                self.error(self.MISSING_SEMICOLON, stopping_symbols)
        else:
            self.error(self.EXPECTED_END, stopping_symbols)
    

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
        """Implements rule device = "CLOCK" | "SWITCH" | "DTYPE" | "RC";"""
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

