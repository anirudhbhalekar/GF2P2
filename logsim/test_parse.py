from parse import *
from monitors import *
from names import *
from network import *
from scanner import *

import pytest
import os

@pytest.fixture
def folder_path():
    return 'definition_files/'


def get_all_files(folder):
    ''' Return a list of all files in the given folder. '''
    return [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

@pytest.mark.parametrize("file_path", get_all_files('definition_files/'))

#use > pytest -k * runs only the test functions containing the kwd *

# --------------------------------------------------- #
# Unit tests

# Error Codes 

@pytest.fixture
# Removed as we aren't indexing errors with error codes, the idea is instead that we could have different error codes as long as they are unique
# Check parse implementation, will discuss
# def error_codes(): 
#     '''Returns a list of all error codes and their expected strings'''
#     error_map = {
#         1: "Expected a name",
#         2: "Invalid character in name",
#         3: "CONNECT list cannot have null devices",
#         4: "CONNECT list must have individual connections delimited by ','",
#         5: "Double punctuation marks are invalid",
#         6: "Semi-colons are required at the end of each line",
#         7: "Missing or misspelled keywords",
#         8: "Comments starting or terminating with the wrong symbol",
#         9: "Invalid order of DEFINE, CONNECT, and MONITOR blocks",
#         10: "No END statement after MONITOR clause",
#         11: "Expected a number",
#         12: "Expected a punctuation mark",
#         13: "Invalid pin reference",
#         14: "Expected an equals sign",
#         15: "Device absent",
#         16: "Input is already connected",
#         17: "Cannot connect an input to another input",
#         18: "Port absent",
#         19: "Cannot connect an output to another output",
#         20: "Device already present",
#         21: "Qualifier is missing",
#         22: "Invalid qualifier",
#         23: "Qualifier should not be present",
#         24: "Invalid device type"
#     }

#     return error_map

# @pytest.mark.parametrize("file_path", get_all_files('definition_files/'))
# def test_get_error_message(error_codes, file_path): 
#     names = Names()
#     scanner = Scanner(file_path, names)

#     devices = Devices(names)
#     network = Network(names, devices)
#     monitors = Monitors(names, devices, network)
#     parser = Parser(names, devices, network, monitors, scanner) 
#     for i in range(1, 25): 
#         assert error_codes[i] == parser.get_error_message(i)

@pytest.mark.parametrize("file_path", get_all_files('definition_files/'))
def test_definition_line(file_path): 
    names = Names() 
    scanner = Scanner(file_path, names)

    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner) 
    parser.definition(scanner.EOF)
    assert parser.error_count == 0

# --------------------------------------------------- # 
# Integrated tests here

@pytest.mark.parametrize("file_path", get_all_files('definition_files/'))
def test_definition_files(file_path): 
    ''' Tests the definition files -- these should all return True as they don't contain errors'''

    names = Names()
    scanner = Scanner(file_path, names)

    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner) 
    assert parser.parse_network()


# Parameterize with (file_path)
@pytest.mark.parametrize("error_file_path", get_all_files('error_definition_files/'))
def test_error_definition_files(error_file_path): 
    ''' Tests the definition files with errors -- these should all return False as they don't contain errors.
    Furthermore the number of errors should be equal to the actual (hardcoded) number of errors in each file'''

    names = Names()
    scanner = Scanner(error_file_path, names)

    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner) 
    
    bool_parse = parser.parse_network()
    # Have to ensure the error codes are consistent as well

    assert not bool_parse

    # Error codes are hardcoded in the error files
    # interim1_ex0_error.txt has 1 error
    # interim1_ex1_error.txt has 2 errors
    # interim1_ex2_error.txt has 3 errors

    if 'interim1_ex0_error.txt' in error_file_path:
        assert parser.error_count == 1
    
    elif 'interim1_ex1_error.txt' in error_file_path:
        assert parser.error_count == 2
    
    elif 'interim1_ex2_error.txt' in error_file_path:
        assert parser.error_count == 3



# Need to check these unit test implementations
# expected_op_list = [ [('G1', 'GATE', 'NAND', 'inputs', '2'), ('G2', 'GATE', 'NAND', 'inputs', '2'), 
#                         ('SW1', 'DEVICE', 'SWITCH', 'initial', '0'), ('SW2', 'DEVICE', 'SWITCH', 'initial', '0')], 
                        
#                     [('SW1', 'DEVICE', 'SWITCH', 'initial', '0'), ('SW2', 'DEVICE', 'SWITCH', 'initial', '0'), 
#                      ('SW3', 'DEVICE', 'SWITCH', 'initial', '0'), ('G1', 'GATE', 'NAND', 'inputs', '2'), ('G2', 'GATE', 'XOR', 'inputs', '2'), 
#                      ('G3', 'GATE', 'OR', 'inputs', '3'), ('G4', 'GATE', 'XOR', 'inputs', '3'), ('G5', 'GATE', 'AND', 'inputs', '2')],
                     
#                      [('CLK1', 'DEVICE', 'CLOCK', 'cycle_rep', '1000'), ('SW1', 'DEVICE', 'SWITCH', 'initial', '1'), ('G1', 'GATE', 'AND', 'inputs', '2'), 
#                       ('G2', 'GATE', 'XOR', 'inputs', '2'), ('DTYPE1', 'DEVICE', 'DTYPE', 'inputs', '2'), ('DTYPE2', 'DEVICE', 'DTYPE', 'inputs', '2'), 
#                       ('DTYPE3', 'DEVICE', 'DTYPE', 'inputs', '2')], 
                      
#                       [('abs', 'GATE', 'NAND', 'inputs', '2'), ('tgf', 'GATE', 'AND', 'inputs', '3')]]

# @pytest.mark.parametrize("op_lists, file_path", zip(expected_op_list, get_all_files('definition_files/')))
# def test_operator_list(op_lists, file_path): 

#     names = Names()
#     scanner = Scanner(file_path, names)

#     devices = Devices(names)
#     network = Network(names, devices)
#     monitors = Monitors(names, devices, network)
#     parser = Parser(names, devices, network, monitors, scanner) 

#     parser.parse_network()

#     assert parser.operators_list == op_lists




    
