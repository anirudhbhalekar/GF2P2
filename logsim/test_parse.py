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

def test_definition_files(file_path): 
    ''' Tests the definition files -- these should all return True as they don't contain errors'''

    names = Names()
    scanner = Scanner(file_path, names)

    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner) 

    assert parser.parse_network()
    
# Hardcoded number of errors for each error definition file
num_error_list = [4, 1, 9]

# Create iterable tuple for parametrization
test_tuple = zip(get_all_files('error_definition_files/'), num_error_list)

# Parameterize with (file_path, num_errors)
@pytest.mark.parametrize("error_file_path, num_errors", test_tuple)

def test_error_definition_files(error_file_path, num_errors): 
    ''' Tests the definition files with errors -- these should all return False as they don't contain errors.
    Furthermore the number of errors should be equal to the actual (hardcoded) number of errors in each file'''

    names = Names()
    scanner = Scanner(error_file_path, names)

    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner) 
    
    assert parser.error_count == num_errors
    