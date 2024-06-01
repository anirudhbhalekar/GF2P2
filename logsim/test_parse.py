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
    if 'interim1_ex0_error.txt' in error_file_path:
        assert parser.error_count == 3
    
    elif 'interim1_ex1_error.txt' in error_file_path:
        assert parser.error_count == 1
    
    elif 'interim1_ex2_error.txt' in error_file_path:
        assert parser.error_count == 3




    
