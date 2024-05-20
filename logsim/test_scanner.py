import pytest
from scanner import Symbol, Scanner

# Symbol class tests
def test_symbol_initialization():
    symbol = Symbol()
    assert symbol.type is None
    assert symbol.id is None
    assert symbol.line_number is None
    assert symbol.character is None

def test_symbol_properties():
    symbol = Symbol()
    symbol.type = "KEYWORD"
    symbol.id = 1
    symbol.line_number = 10
    symbol.character = 5

    assert symbol.type == "KEYWORD"
    assert symbol.id == 1
    assert symbol.line_number == 10
    assert symbol.character == 5

# Scanner class tests
@pytest.fixture
def new_scanner():
    return Scanner()

@pytest.fixture
def scanner(mock_names, mock_devices):
    # Creating a fake file-like object using StringIO
    file_content = "DEFINE name1 123\nWITH name2\nCONNECT DEVICE1\nMONITOR GATE1\nEND\n"
    # Patch the Devices import in Scanner to use the MockDevices
    scanner = Scanner(file_content, mock_names)
    scanner.devices = mock_devices
    return scanner

# To be implemented
