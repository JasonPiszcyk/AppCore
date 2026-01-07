#!/usr/bin/env python3
'''
PyTest - Test of get_value_type function

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
# Shared variables, constants, etc
from tests.constants import *

# System Modules
import pytest
import uuid

# Local app modules
from appcore.conversion import get_value_type
from appcore.typing import DataType

# Imports for python variable type hints


###########################################################################
#
# Module Specific Items
#
###########################################################################
#
# Types
#

#
# Constants
#
DEFAULT_NO_MATCH = "This should not match"
INVALID_TYPE = "Not enum of DataType"

#
# Global Variables
#

# System Imports


#
# Globals
#
DATASET = {
    DataType.NONE.value: {
        "valid": [ None, ],
        "invalid": [ "", {}, [], (), 0 ]
    },
    DataType.INTEGER.value: {
        "valid": [ 0, 14, -1, 9999999 ],
        "invalid": [ None, 0.123, "string", {}, True ]
    },
    DataType.FLOAT.value: {
        "valid": [ 0.123, 123.456, -123.456 ],
        "invalid": [ None, 0, 14, "string", {}, True ] # 0, 14 are integers
    },
    DataType.STRING.value: {
        "valid": [
         "",
         "a string",
         "d5bf0b08-38a3-4116-8a7c-2655e6b54b64"
        ],
        "invalid": [ None, {}, True ]
    },
    DataType.BOOLEAN.value: {
        "valid": [ True, False ],
        "invalid": [ None, 0, 1, "yes", "No", "True", "False" ]
    },
    DataType.DICTIONARY.value: {
        "valid": [ {}, { "dict_key": "dict_value"} ],
        "invalid": [ None, 0, "string", [], True ]
    },
    DataType.LIST.value: {
        "valid": [ [], [ 1, 2, 3 ], [ "str", "a", "b" ] ],
        "invalid": [ None, 0, "string", {}, (), True ]
    },
    DataType.TUPLE.value: {
        "valid": [ (), ( 1, 2, 3 ), ( "str", "a", "b" ) ],
        "invalid": [ None, 0, "string", {}, [], True ]
    }
}

UUID_DATASET = {
    "valid": [
        "d5bf0b08-38a3-4116-8a7c-2655e6b54b64",
        "569866c7-5264-4e5f-85af-361dde057884"
    ],
    "invalid": [ None, 0, "string", {}, [], True ]
}



###########################################################################
#
# The tests...
#
###########################################################################
#
# get_value_type
#
class Test_GetValueType():
    '''
    Test Class - GetValueType

    Attributes:
        None
    '''
    #
    # Test with valid data for the type
    #
    @pytest.mark.parametrize("datatype_name", DATASET)
    def test_valid_data_for_type(self, datatype_name):
        '''
        Test with valid data for the type

        Args:
            datatype_name (str): Fixture containing the key to process from the
                DATASET dict

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert datatype_name in DATASET.keys()
        assert "valid" in DATASET[datatype_name]

        for _entry in DATASET[datatype_name]["valid"]:
            # Get the data type
            _datatype = get_value_type(data=_entry)
            assert DataType(datatype_name) == _datatype


    #
    # Test with invalid data for the type
    #
    @pytest.mark.parametrize("datatype_name", DATASET)
    def test_invalid_data_for_type(self, datatype_name):
        '''
        Test with invalid data for the type

        Args:
            datatype_name (str): Fixture containing the key to process from the
                DATASET dict

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert datatype_name in DATASET.keys()
        assert "invalid" in DATASET[datatype_name]

        for _entry in DATASET[datatype_name]["invalid"]:
            # Get the data type
            _datatype = get_value_type(data=_entry)
            assert DataType(datatype_name) != _datatype


    #
    # Test with UUID data
    #
    @pytest.mark.parametrize("data", UUID_DATASET["valid"])
    def test_UUID_data_type(self, data):
        '''
        Test with UUID data types

        Args:
            data (str): Fixture containing the key to process from the
                UUID_DATASET list

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        # Convert the value to a UUID
        _val = uuid.UUID(data, version=4)

        _datatype = get_value_type(data=_val)
        assert _datatype == DataType.UUID


    #
    # Test with invalid UUID data
    #
    @pytest.mark.parametrize("data", UUID_DATASET["invalid"])
    def test_invalid_UUID_data_type(self, data):
        '''
        Test with UUID data types

        Args:
            data (str): Fixture containing the key to process from the
                UUID_DATASET list

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        _datatype = get_value_type(data=data)
        assert _datatype != DataType.UUID
