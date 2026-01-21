#!/usr/bin/env python3
'''
Conversion functions

Copyright (C) 2025 Jason Piszcyk
Email: Jason.Piszcyk@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (See file: COPYING). If not, see
<https://www.gnu.org/licenses/>.
'''
###########################################################################
#
# Imports
#
###########################################################################
from __future__ import annotations

# Shared variables, constants, etc

# System Modules
import uuid
import pickle
import json
import base64

# Local app modules
from appcore.typing import DataType

# Imports for python variable type hints
from typing import Any


###########################################################################
#
# Module variables/constants/types
#
###########################################################################
#
# Types
#

#
# Constants
#
ENCODE_METHOD = "utf-8"

# Pickle Protocol 5 is supported in Python >= 3.8
MIN_PICKLE_PROTOCOL = 0
MAX_PICKLE_PROTOCOL = 5
DEFAULT_PICKLE_PROTOCOL = 5

#
# Global Variables
#


###########################################################################
#
# Conversion Functions
#
###########################################################################
#
# set_value
#
def set_value(
        data: Any = None,
        type: DataType = DataType.STRING,
        default: Any = ""
    ) -> Any:
    '''
    Convert data to the specified type, using the default value if an error
    occurs.

    Args:
        data (Any): The data to be converted
        type (DataType): The type to convert 'data' to
        default (Any): The value to return of the conversion fails

    
    Returns:
        Any: The converted data (if successful) or the default value.

    Raises:
        None
    '''
    assert isinstance(type, DataType), "Type must be an entry of 'DataType'"

    _val: Any = None

    try:
        if type == DataType.INT or type == DataType.INTEGER:
            _val = int(data)
        elif type == DataType.FLOAT:
            _val = float(data)
        elif type == DataType.BOOL or type == DataType.BOOLEAN:
            _val = bool(data)
        elif type == DataType.DICT or type == DataType.DICTIONARY:
            _val = dict(data)
        elif type == DataType.LIST:
            _val = list(data)
        elif type == DataType.TUPLE:
            _val = tuple(data)
        elif type == DataType.UUID:
            _val = uuid.UUID(data)
        elif type == DataType.UUID1:
            _val = uuid.UUID(data, version=1)
        elif type == DataType.UUID3:
            _val = uuid.UUID(data, version=3)
        elif type == DataType.UUID4:
            _val = uuid.UUID(data, version=4)
        elif type == DataType.UUID5:
            _val = uuid.UUID(data, version=5)
        else:       # Everything else becomes a string
            _val = str(data)

    except:
        _val = default

    return _val


#
# get_value_type
#
def get_value_type(
        data: Any = None,
        json_only: bool = False
    ) -> DataType:
    '''
    Identify the type of the value

    Args:
        data (Any): The data to be typed
        json_only (bool): Only allow supported JSON data types
    
    Returns:
        DataType: The data type of the value

    Raises:
        TypeError:
            When the data type is unsupported
    '''
    # Determine the type of the data - JSON supported types
    if isinstance(data, dict): return DataType.DICTIONARY
    if isinstance(data, list): return DataType.LIST
    if isinstance(data, str): return DataType.STRING
    if isinstance(data, tuple): return DataType.TUPLE
    if isinstance(data, bool): return DataType.BOOLEAN
    if isinstance(data, int): return DataType.INTEGER
    if isinstance(data, float): return DataType.FLOAT

    if data is None: return DataType.NONE

    if not json_only:
        if isinstance(data, uuid.UUID): return DataType.UUID

    # A datatype we can't handle
    raise TypeError(
        f"Data type not supported: {type(data)}"
    )


###########################################################################
#
# Pickle Functions
#
###########################################################################
#
# to_pickle
#
def to_pickle(
        data: Any = None,
        protocol: int = DEFAULT_PICKLE_PROTOCOL,
        fix_imports: bool = True
) -> bytes:
    '''
    Convert data to a python pickle.

    Args:
        data (Any): The data to be converted
        protocol (int): The pickle prootocol to use
        fix_imports (bool): If protocol is less than 3, pickle will try to map
            the new Python 3 names to the old module names used in Python 2, so
            that the pickle data stream is readable with Python 2

    Returns:
        bytes: The data as a python pickle

    Raises:
        AssertionError:
            When the protocol is not an int or not between 1 and 5
        TypeError:
            When the data cannot be converted to a pickle
    '''
    assert isinstance(protocol, int), "protocol must be an integer"
    assert (
                protocol >= MIN_PICKLE_PROTOCOL and
                protocol <= MAX_PICKLE_PROTOCOL
    ), (
            f"protocol must be between {MIN_PICKLE_PROTOCOL} "
            f"and {MAX_PICKLE_PROTOCOL}"
    )

    _exc = ""
    try:
        return pickle.dumps(data, protocol=protocol, fix_imports=fix_imports)

    except Exception as _err:
        _exc = str(_err)

    # Something broke - Raise it a TypeError (standard for this module)
    raise TypeError(_exc)


#
# from_pickle
#
def from_pickle(
        data: bytes = b"",
        fix_imports: bool = True,
        encoding: str = "ASCII",
        errors: str = "strict"
) -> Any:
    '''
    Convert a python pickle to python data

    Args:
        data (bytes): The pickle data
        fix_imports (bool): If protocol is less than 3, pickle will try to map
            the new Python 3 names to the old module names used in Python 2, so
            that the pickle data stream is readable with Python 2
        encoding (str): Used to determine how to decode 8-bit string instances
            pickled by Python 2
        errors (str): Used to determine how to decode 8-bit string instances
            pickled by Python 2
    
    Returns:
        Any: The data converted from the pickle

    Raises:
        AssertionError:
            When encoding is not a string
            When errors is not a string
        TypeError:
            When the data cannot be converted from a pickle
    '''
    assert isinstance(encoding, str), "encoding must be a string"
    assert isinstance(errors, str), "errors must be a string"

    _exc = ""
    try:
        return pickle.loads(
            data,
            fix_imports=fix_imports,
            encoding=encoding,
            errors=errors
        )

    except Exception as _err:
        _exc = str(_err)

    # Something broke - Raise it a TypeError (standard for this module)
    raise TypeError(_exc)


###########################################################################
#
# JSON Functions
#
###########################################################################
#
# to_json
#
def to_json(
        data: Any = None,
        skip_invalid: bool = False,
        container: bool = False
) -> str:
    '''
    Convert data to JSON.

    Args:
        data (Any): The data to be converted
        skip_invalid (bool): Skip objects that cannot be serialised rather than
            raising TypeError
        container (bool): If true, the export contains an outer layer:
            {
                "value": { The export values },
                "type": "dictionary"
            }

    Returns:
        str: The data as a JSON string

    Raises:
        TypeError:
            When the data cannot be converted to JSON
    '''
    assert isinstance(skip_invalid, bool), "skip_invalid must be True or False"
    # if isinstance(data, str) and not data: return ""

    # Wrap the data in a dict containing the value and type
    if container:
        _json_dict = {
            "value": data,
            "type": get_value_type(data).value
        }
    else:
        _json_dict = data

    # Define a function to handle invalid types
    def _null_invalid_types(data):
        return None

    default_func = _null_invalid_types if skip_invalid else None

    return json.dumps(_json_dict, default=default_func)


#
# from_json
#
def from_json(
        data: str = "",
        container: bool = False
) -> Any:
    '''
    Convert a JSON string to python data

    Args:
        data (str): The json data
        container (bool): If true, the JSON export contains an outer layer:
            {
                "value": { The export values },
                "type": "dictionary"
            }
    
    Returns:
        Any: The data converted from the JSON string

    Raises:
        TypeError:
            When the data is not a JSON string
        json.decoder.JSONDecodeError:
            When JSON conversion fails
    '''
    _value_from_json = json.loads(data)

    if not container:
        return _value_from_json

    # Extract the value based on the type of the data
    _value = set_value(
        data=_value_from_json['value'],
        type=DataType(_value_from_json['type']),
        default=DataType.NONE
    )

    if _value == DataType.NONE:
        raise TypeError(
            f"Data type not supported: {_value_from_json['type']}"
        )

    return _value


###########################################################################
#
# Base64 Functions
#
###########################################################################
#
# to_base64
#
def to_base64(
        data: bytes = b"",
) -> str:
    '''
    Convert data to base64.

    Args:
        data (bytes): The data to be converted

    Returns:
        str: The data encoded as a string

    Raises:
        AssertionError:
            when data is not in byte format
    '''
    if not data: return ""

    assert isinstance(data, bytes), "data must be in byte format"

    _val = base64.standard_b64encode(data)
    return _val.decode(ENCODE_METHOD)


#
# from_base64
#
def from_base64(
        data: str = "",
) -> bytes:
    '''
    Convert data from base64 to bytes.

    Args:
        data (str): The data to be converted

    Returns:
        bytes: The data decoded as bytes

    Raises:
        AssertionError:
            when data is not in string format
    '''
    if not data: return b""

    assert isinstance(data, str), "data must be in string format"

    return base64.standard_b64decode(data)


###########################################################################
#
# In case this is run directly rather than imported...
#
###########################################################################
'''
Handle case of being run directly rather than imported
'''
if __name__ == "__main__":
    pass

