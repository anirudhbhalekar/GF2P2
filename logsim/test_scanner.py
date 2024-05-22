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
    return Scanner("definition_files/test_ex_null.txt", Names())

def names():
    return Names()

def test_scanner_initialization(scanner_example_null):
    assert scanner_example_null.file is not None
    assert scanner_example_null.names is not None

def test_get_symbol(scanner_example_null):
    """Test the get_symbol method."""
    scanner_example_null.get_symbol()
    symbol = scanner_example_null.get_symbol()

    print(f"Symbol: {symbol}, {symbol.type}, {symbol.id}, {symbol.line_number}, {symbol.character}")
    assert symbol is not None
    assert symbol.type == "KEYWORD" # This is the KEYWORD 
    assert symbol.id == scanner_example_null.DEFINE_ID
    assert symbol.line_number == 1 # Line starts at 1
    assert symbol.character == 7

def test_get_name(scanner_example_null):
    """Test the get_name method."""
    scanner_example_null.file.seek(0)
    scanner_example_null.advance()
    name = scanner_example_null.get_name()
    assert name == "DEFINE"

def test_get_number(scanner_example_null):
    """Test the get_number method."""
    scanner_example_null.file.seek(0)
    scanner_example_null.advance()
    while not scanner_example_null.current_character.isdigit():
        scanner_example_null.advance()
    number = scanner_example_null.get_number()
    assert number == "2"


@pytest.fixture
def scanner_test_ex0():
    """Return a new instance of the Scanner class."""
    return Scanner("definition_files/test_ex0.txt", Names())

def test_skip_comment(scanner_test_ex0):
    """Test if the scanner properly skips a comment"""
    symbol = scanner_test_ex0.get_symbol() # This will return a COMMENT type symbol 
    symbol = scanner_test_ex0.get_symbol() # This returns the next symbol
    symbol = scanner_test_ex0.get_symbol()

    print(f"Symbol: {symbol}, {symbol.type}, {symbol.id}, {symbol.line_number}, {symbol.character}")
    assert symbol is not None
    assert symbol.type == "KEYWORD"
    assert symbol.id == scanner_test_ex0.DEFINE_ID
    #assert symbol.line_number == 4
    #assert symbol.character == 85

def test_def_symbol_sequence(scanner_test_ex0):
    """Tests symbol sequence for the first define statement"""
    expected_types = [scanner_test_ex0.KEYWORD, scanner_test_ex0.NAME, scanner_test_ex0.KEYWORD,
        scanner_test_ex0.GATE, scanner_test_ex0.KEYWORD, scanner_test_ex0.PARAM,
        scanner_test_ex0.EQUALS, scanner_test_ex0.NUMBER, scanner_test_ex0.SEMICOLON]

    for expected_type in expected_types:
        symbol = scanner_test_ex0.get_symbol()        
        assert symbol.type == expected_type
        
        

def test_con_symbol_sequence(scanner_test_ex0):
    symbol = scanner_test_ex0.get_symbol()
    while not symbol.id == scanner_test_ex0.CONNECT_ID:
        symbol = scanner_test_ex0.get_symbol()
    expected_types = [
        "KEYWORD",   # CONNECT
        "NAME",      # SW1
        "EQUALS",    # =
        "NAME",      # G1
        "DOT",       # .
        "NAME",      # I1
        "COMMA",     # ,
        "NAME",      # SW2
        "EQUALS",    # =
        "NAME",      # G2
        "DOT",       # .
        "NAME",      # I2
        "COMMA",     # ,
        "NAME",      # G1
        "EQUALS",    # =
        "NAME",      # G2
        "DOT",       # .
        "NAME",      # I1
        "SEMICOLON", # ;
        "COMMENT",   # COMMENT HERE
        "NAME",      # G2
        "EQUALS",    # =
        "NAME",      # G1
        "DOT",       # .
        "NAME",      # I2
        "SEMICOLON"  # ;
    ]
    for expected_type in expected_types:
        assert symbol.type == expected_type
        symbol = scanner_test_ex0.get_symbol()
        






