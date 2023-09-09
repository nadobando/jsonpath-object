# JsonPathObject Module

A Python module for working with JSON-like data using dot-separated keys and JSON path-like syntax.

## Installation

You can install this module using pip:

```shell
pip install jsonpath-object
```

## Usage

Import the `JsonPathObject` class from the module:

```python
from jsonpath_object import JsonPathObject
```

### Creating a JsonPathObject

You can create a `JsonPathObject` instance with optional initial data, raise behavior, and default factory:

```python
from jsonpath_object import JsonPathObject

# Create an empty JsonPathObject
obj = JsonPathObject()

# Create a JsonPathObject with initial data
data = {
    'name': 'John',
    'address': {
        'city': 'New York',
        'zip_code': '10001'
    }
}
obj = JsonPathObject(data)

# You can also specify custom raise behavior and default factory
obj = JsonPathObject(data, raise_on_missing=False, default_factory=lambda: 'N/A')
```

### Accessing Data

You can access data in the `JsonPathObject` using dot-separated keys or JSON path-like syntax:

```python
# Access data using dot-separated keys
name = obj['name']  # 'John'
city = obj['address.city']  # 'New York'

# Access data using JSON path-like syntax
zip_code = obj['address["zip_code"]']  # '10001'
```

### Modifying Data

You can modify data in the `JsonPathObject` by setting values:

```python
# Set a new value
obj['age'] = 30

# Update an existing value
obj['address.city'] = 'Los Angeles'

# Note that this will create nested objects if they don't exist
obj['address.state'] = 'California'
```

### Deleting Data

You can delete data from the `JsonPathObject` using dot-separated keys or JSON path-like syntax:

```python
# Delete a key
del obj['age']

# Delete nested data
del obj['address.zip_code']
```

### Converting to Python Objects

You can convert the `JsonPathObject` to a regular Python dictionary or list using the `to_object` method:

```python
data_dict = obj.to_object()
```

## License

This module is released under the MIT License.
