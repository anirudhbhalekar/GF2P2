import pytest
from names import Names


@pytest.fixture
def new_names():
    """Return a new instance of the Names class."""
    return Names()


@pytest.fixture
def example_list():
    """Return a list of example names."""
    return ["var1", "var2", "var3"]


@pytest.fixture
def used_names(example_list):
    """Return an instance of the Names class with example names added."""
    name = Names()
    name.lookup(example_list)
    return name


def test_used_names(used_names, example_list):
    """Test the Names class with example names added."""
    # Test whether name class returns non-None value for existing names
    assert used_names.query(example_list[0]) is not None

    # Test get_name_string works correctly
    assert used_names.get_name_string(0) == example_list[0]

    # Test ambiguous input to Names class
    with pytest.raises(TypeError):
        used_names.lookup({1: 2, 3: 4})
    with pytest.raises(TypeError):
        used_names.lookup(["a string", 90])
    with pytest.raises(ValueError):
        used_names.query("")
    with pytest.raises(ValueError):
        used_names.get_name_string(-2)


def test_empty_names(new_names):
    """Test the Names class with no names added."""
    assert new_names.get_name_string(0) is None


def test_unique_error_codes(new_names):
    """Test the unique_error_codes method."""
    # Test correct range generation for unique error codes
    codes = new_names.unique_error_codes(5)
    assert list(codes) == [0, 1, 2, 3, 4]

    codes = new_names.unique_error_codes(3)
    assert list(codes) == [5, 6, 7]

    # Test invalid type input
    with pytest.raises(TypeError):
        new_names.unique_error_codes("five")


def test_query(new_names):
    """Test the query method."""
    # Test querying a name that does not exist
    assert new_names.query("nonexistent") is None

    # Test invalid type input
    with pytest.raises(TypeError):
        new_names.query(123)
    with pytest.raises(ValueError):
        new_names.query("")


def test_lookup(new_names):
    """Test the lookup method."""
    # Test adding and querying names
    assert new_names.lookup(["var1"]) == [0]
    assert new_names.lookup(["var1", "var2"]) == [0, 1]
    assert new_names.lookup(["var3"]) == [2]

    # Test invalid type inputs
    with pytest.raises(TypeError):
        new_names.lookup("not a list")
    with pytest.raises(TypeError):
        new_names.lookup([123, "var4"])


def test_get_name_string(new_names):
    """Test the get_name_string method."""
    # Test getting name strings from IDs
    new_names.lookup(["var1", "var2", "var3"])
    assert new_names.get_name_string(1) == "var2"
    assert new_names.get_name_string(3) is None

    # Test invalid type and value inputs
    with pytest.raises(TypeError):
        new_names.get_name_string("one")
    with pytest.raises(ValueError):
        new_names.get_name_string(-1)
