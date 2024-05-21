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
def scanner_example_null():
    """Return a new instance of the Scanner class."""
    return Scanner("definition_files/test_example_null.txt", Names())
def names():
    return Names()

def test_scanner_initialization(new_scanner):
    assert scanner_example_null.file is not None
    assert scanner_example_null.names is not None

def test_get_symbol(scanner_example_null):
    """Test the get_symbol method."""
    symbol = scanner_example_null.get_symbol()
    print(f"Symbol: {symbol}, {symbol.type}, {symbol.id}, {symbol.line_number}, {symbol.character}")
    assert symbol is not None
    assert symbol.type == "KEYWORD"
    assert symbol.id == scanner_example_null.DEFINE_ID
    assert symbol.line_number == 1
    assert symbol.character == 5

    symbol = scanner_example_null.get_symbol()
    print(f"Symbol: {symbol}, {symbol.type}, {symbol.id}, {symbol.line_number}, {symbol.character}")
    assert symbol is not None
    assert symbol.type == scanner_example_null.NAME
    assert scanner_example_null.names.get_name_string(symbol.id) == "abs"
    assert symbol.line_number == 2
    assert symbol.character == 8

def test_get_def_list(scanner_example_null):
    """Test if we read a def_list properly:     
    DEFINE 
    abs AS NAND WITH input = 2, 
    tgf AS AND WITH input = 3;"""
    symbol = scanner_example_null.get_symbol()
    assert symbol.type == "KEYWORD"
    symbol = scanner_example_null.get_symbol()
    assert symbol.type == "NAME"
    symbol = scanner_example_null.get_symbol()
    assert symbol.type == "KEYWORD"
    symbol = scanner_example_null.get_symbol()
    assert symbol.type == "GATE"
    symbol = scanner_example_null.get_symbol()
    assert symbol.type == "KEYWORD"
    symbol = scanner_example_null.get_symbol()
    assert symbol.type == "PARAM"
    symbol = scanner_example_null.get_symbol()
    assert symbol.type == "EQUALS"
    symbol = scanner_example_null.get_symbol()
    assert symbol.type == "NUMBER"
    symbol = scanner_example_null.get_symbol()
    assert symbol.type == "COMMA"
    symbol = scanner_example_null.get_symbol()
    symbol = scanner_example_null.get_symbol()
    symbol = scanner_example_null.get_symbol()
    symbol = scanner_example_null.get_symbol()
    symbol = scanner_example_null.get_symbol()
    symbol = scanner_example_null.get_symbol()
    symbol = scanner_example_null.get_symbol()
    symbol = scanner_example_null.get_symbol()
    assert symbol.type == "SEMICOLON"


@pytest.fixture
def scanner_test_ex0():
    """Return a new instance of the Scanner class."""
    return Scanner("definition_files/test_ex0.txt", Names())

def test_skip_comment(scanner_test_ex0):
    """Test if the scanner properly skips a comment"""
    symbol = scanner_test_ex0.get_symbol()
    print(f"Symbol: {symbol}, {symbol.type}, {symbol.id}, {symbol.line_number}, {symbol.character}")
    assert symbol is not None
    assert symbol.type == "KEYWORD"
    assert symbol.id == "DEFINE"
    assert symbol.line_number == 4
    assert symbol.character == 85

 





