from parse import *
from monitors import *
from names import *
from network import *
from scanner import *

import pytest


# NOTE: global variables are not encourages in test files - but this is 
# the folder for all the definition files (for ease of reference in tests)

folder_path = 'definition_files/'

def test_example_null(): 
    ''' Tests the null file'''

    file_path = folder_path + 'example_null.txt'

    names = Names()
    network = Network()
    scanner = Scanner()
    monitor = Monitors()
    parser = Parser()    
    pass

