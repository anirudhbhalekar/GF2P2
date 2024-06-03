from parse import *
from monitors import *
from names import *
from network import *
from scanner import *

import pytest
import os


def get_all_files(folder):
    ''' Return a list of all files in the given folder. '''
    return [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

@pytest.mark.parametrize("file_path", get_all_files('test_definition_files/'))
def test_definition_files(file_path): 
    ''' Tests the definition files -- these should all return True as they don't contain errors'''

    names = Names()
    scanner = Scanner(file_path, names)

    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner) 
    assert parser.parse_network()

@pytest.mark.parametrize("file_path", get_all_files('example_definition_files/'))
def test_definition_files(file_path): 
    ''' Tests the example definition files -- these should all return True as they don't contain errors'''

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
    error_count_map = {
<<<<<<< HEAD
        'interim1_ex0_error.txt': 3,
        'input_output_reversed': 1,
        'undefined_device_and_param': 3,
        'empty_file.txt': 1,
        'missing_section': 3,
        'extra_semicolon': 2,
        'two_define': 1,
        'extra_commas': 2,
        'keyword_instead_of_name': 3,
        'invalid_symbol': 1,
=======
        'early_semicolon.txt': 3,
        'input_output_reversed.txt': 1,
        'undefined_device_and_param.txt': 3,
        'empty_file.txt': 1,
        'missing_section.txt': 3,
        'extra_semicolon.txt': 2,
        'two_define.txt': 1,
        'extra_commas.txt': 2,
        'keyword_instead_of_name.txt': 3,
        'invalid_symbol.txt': 1,
>>>>>>> 254bcdb82968d5e2bd52738d310b49da16e9681d
    }

    for error_file, expected_count in error_count_map.items():
        if error_file in error_file_path:
            print(f"Error file: {error_file}, expected count: {expected_count}")
            assert parser.error_count == expected_count
            break

    




    
