import pytest
from names import Names
 
@pytest.fixture
def new_names(): 
    return Names()

@pytest.fixture()
def example_list(): 

    return ["Billy-Bob", "Dog12", "Dog4", "Cat", "Cat-Dog"]

@pytest.fixture
def used_names(example_list):
    name = Names()
    name.lookup(example_list) 
    return name


def test_used_names(used_names, example_list): 
    # test whether name class returns non None value for exisiting 
    assert used_names.query(example_list[0]) is not None
    # test get_id works
    assert used_names.get_name_string(0) == example_list[0]
    # test ambiguous input to Names class

    with pytest.raises(TypeError): 
        used_names.lookup({1:2, 3:4})
    with pytest.raises(TypeError): 
        used_names.lookup(["Goo Goo", 90])
    
    with pytest.raises(ValueError): 
        used_names.query("")
    with pytest.raises(ValueError): 
        used_names.get_name_string(-2)
    
def test_empty_names(new_names): 
    assert new_names.get_name_string(0) is None