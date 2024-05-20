import pytest
from scanner import Symbol, Scanner
from names import Names


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
    """Return a new instance of the Scanner class."""
    return Scanner("definition_files/test_example_null.txt", Names())

def test_scanner_initialization(new_scanner):
    assert new_scanner.file is not None
    assert new_scanner.names is not None

def test_get_symbol(new_scanner):
    symbol = new_scanner.get_symbol()
    print(f"Symbol: {symbol}, {symbol.type}, {symbol.id}, {symbol.line_number}, {symbol.character}")
    assert symbol is not None
    assert symbol.type == "KEYWORD"
    assert symbol.id == "DEFINE"
    assert symbol.line_number == 1
    assert symbol.character == "DEFINE"




