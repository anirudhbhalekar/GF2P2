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

# use > pytest -k * runs only the test functions containing the kwd *

def test_definition_files(file_path): 
    ''' Tests the definition files -- these should all return True as they don't contain errors'''

    names = Names()
    scanner = Scanner(file_path, names)

    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner) 

    assert parser.parse_network()


@pytest.mark.parametrize("error_file_path", get_all_files('error_definition_files/'))


def test_error_definition_files(error_file_path): 
    ''' Tests the definition files with errors -- these should all return False as they don't contain errors'''

    names = Names()
    scanner = Scanner(error_file_path, names)

    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner) 

    assert not parser.parse_network()
    