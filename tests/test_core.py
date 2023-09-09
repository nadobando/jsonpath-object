import pytest

from jsonpath_object import JsonPathObject

test_data = {
    "name": "John",
    "age": 30,
    "address": {"city": "New York", "zip_code": "10001"},
    "scores": [85, 90, 78],
}

jsonpath_data = JsonPathObject(test_data)


def test_get_item():
    assert jsonpath_data["name"] == "John"
    assert jsonpath_data["address.city"] == "New York"
    assert jsonpath_data["scores.0"] == 85


def test_set_item():
    jsonpath_data["name"] = "Alice"
    assert jsonpath_data["name"] == "Alice"

    jsonpath_data["address.city"] = "Los Angeles"
    print(jsonpath_data)
    assert jsonpath_data["address.city"] == "Los Angeles"

    jsonpath_data["scores.0"] = 95
    assert jsonpath_data["scores.0"] == 95


def test_key_error():
    with pytest.raises(KeyError):
        jsonpath_data["nonexistent_key"]

    with pytest.raises(KeyError):
        jsonpath_data["address.nonexistent_key"]


def test_index_error():
    with pytest.raises(IndexError):
        jsonpath_data["scores.10"]


def test_nested_instance():
    address = jsonpath_data["address"]
    assert isinstance(address, JsonPathObject)

    scores = jsonpath_data["scores"]
    assert isinstance(scores, JsonPathObject)


def test_nonexistent_key():
    assert "nonexistent_key" not in jsonpath_data


def test_contains():
    assert "name" in jsonpath_data
    assert "nonexistent_key" not in jsonpath_data


def test_len():
    assert len(jsonpath_data) == 4  # Top-level keys


def test_iteration():
    keys = list(jsonpath_data)
    assert "name" in keys
    assert "address" in keys
    assert "scores" in keys


def test_default_factory():
    # Test that the default factory is used when getting a missing key
    def custom_default_factory():
        return "default_value"

    custom_dict = JsonPathObject(default_factory=custom_default_factory)

    assert custom_dict["missing_key"] == "default_value"


def test_nested_default_factory():
    custom_dict = JsonPathObject(default_factory=lambda: {"default_value": 0})
    nested_value = custom_dict["nested.key.0"]
    assert nested_value == {"default_value": 0}
    assert {"nested": {"key": [{"default_value": 0}]}}


def test_nested_json_path_object():
    nested_data = {"outer": {"inner": {"value": "nested_value"}}}
    nested_dict = JsonPathObject(nested_data)

    inner = nested_dict["outer.inner"]
    assert isinstance(inner, JsonPathObject)
    assert inner["value"] == "nested_value"


def test_nested_list():
    nested_data = {"nested_list": [{"name": "Alice"}, {"name": "Bob"}]}
    nested_dict = JsonPathObject(nested_data)

    assert nested_dict["nested_list.0.name"] == "Alice"
    assert nested_dict["nested_list.1.name"] == "Bob"


def test_to_object():
    data = {"name": "John", "age": 30}
    custom_dict = JsonPathObject(data)

    as_dict = custom_dict.to_object()
    assert isinstance(as_dict, dict)
    assert as_dict["name"] == "John"
    assert as_dict["age"] == 30


def test_set_nested_item():
    jsonpath_data["address.city"] = "Los Angeles"
    assert jsonpath_data["address.city"] == "Los Angeles"

    jsonpath_data["address.country.continent"] = "North America"
    assert jsonpath_data["address.country.continent"] == "North America"


def test_delete_item():
    del jsonpath_data["name"]
    assert "name" not in jsonpath_data

    del jsonpath_data["address.city"]
    assert "address.city" not in jsonpath_data


def test_delete_nested_item():
    # Delete a deeply nested item
    del jsonpath_data["address.country.continent"]
    assert "address.country.continent" not in jsonpath_data


def test_nested_instance_after_set():
    # Create a nested instance after setting a value
    jsonpath_data["new_key"] = {"nested_key": "nested_value"}
    nested_instance = jsonpath_data["new_key"]
    assert isinstance(nested_instance, JsonPathObject)
    assert nested_instance["nested_key"] == "nested_value"


def test_nested_instance_after_set_nested():
    # Create a nested instance after setting a nested value
    jsonpath_data["new_key.nested_key"] = "nested_value"
    nested_instance = jsonpath_data["new_key"]
    assert isinstance(nested_instance, JsonPathObject)
    assert nested_instance["nested_key"] == "nested_value"


def test_delete_nested_instance():
    # Delete a nested instance
    del jsonpath_data["new_key"]
    assert "new_key" not in jsonpath_data


def test_nested_instance_after_delete_nested():
    # Create a nested instance after deleting a nested value
    jsonpath_data["new_key.nested_key"] = "nested_value"
    del jsonpath_data["new_key.nested_key"]
    nested_instance = jsonpath_data["new_key"]
    assert isinstance(nested_instance, JsonPathObject)


def test_setting_nested_instance():
    # Set a nested instance and access its values
    jsonpath_data["new_key"] = JsonPathObject({"nested_key": "nested_value"})
    nested_instance = jsonpath_data["new_key"]
    assert isinstance(nested_instance, JsonPathObject)
    assert nested_instance["nested_key"] == "nested_value"


def test_nested_list_after_set():
    jsonpath_data["new_list"] = [1, 2, 3]
    nested_list = jsonpath_data["new_list"]
    assert isinstance(nested_list, JsonPathObject)
    assert nested_list[0] == 1


def test_nested_list_after_set_nested():
    jsonpath_data["new_list.0"] = 42
    nested_list = jsonpath_data["new_list"]
    assert isinstance(nested_list, JsonPathObject)
    assert nested_list[0] == 42


def test_delete_nested_list():
    del jsonpath_data["new_list"]
    assert "new_list" not in jsonpath_data


def test_nested_list_in_list():
    # Create a JsonPathObject with nested lists
    data = {"nested_lists": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
    custom_dict = JsonPathObject(data)

    # Access elements in the nested lists
    assert custom_dict["nested_lists.0.0"] == 1
    assert custom_dict["nested_lists.1.1"] == 5
    assert custom_dict["nested_lists.2.2"] == 9

    # Modify elements in the nested lists
    custom_dict["nested_lists.0.0"] = 10
    custom_dict["nested_lists.1.1"] = 50
    custom_dict["nested_lists.2.2"] = 90

    assert custom_dict["nested_lists.0.0"] == 10
    assert custom_dict["nested_lists.1.1"] == 50
    assert custom_dict["nested_lists.2.2"] == 90

    # Test accessing out-of-range indices
    with pytest.raises(IndexError):
        custom_dict["nested_lists.0.3"]

    with pytest.raises(IndexError):
        custom_dict["nested_lists.3.0"]


def test_get_keys():
    # Test with an integer key
    int_key = 42
    keys = JsonPathObject._get_keys(int_key)
    assert keys == ["42"]

    # Test with a string key containing dots
    str_key = "foo.bar.baz"
    keys = JsonPathObject._get_keys(str_key)
    assert keys == ["foo", "bar", "baz"]

    seq_key = ["a", "b", "c"]
    keys = JsonPathObject._get_keys(seq_key)
    assert keys == ["a", "b", "c"]

    with pytest.raises(NotImplementedError):
        unsupported_key = object()
        JsonPathObject._get_keys(unsupported_key)


def test_find_index_out_of_range():
    data = {"nested_list": [1, 2, 3]}
    custom_dict = JsonPathObject(data)

    with pytest.raises(IndexError, match="Index 5 out of range for list."):
        assert custom_dict["nested_list.5"]


def test_delete_note_existing():
    with pytest.raises(KeyError):
        del jsonpath_data["not-existing"]

    with pytest.raises(IndexError):
        del jsonpath_data["scores.10"]
