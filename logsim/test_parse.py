from parse import *
from monitors import *
from names import *
from network import *
from scanner import *

import pytest


@pytest.fixture
def folder_path():
    return 'definition_files/'


def test_example_null(folder_path): 
    ''' Tests the null file'''
    
    file_path = folder_path + 'test_example_null.txt'

    names = Names()
    scanner = Scanner(file_path, names)

    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    parser = Parser(names, devices, network, monitors, scanner) 

    assert parser.parse_network()




