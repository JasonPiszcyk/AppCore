#!/usr/bin/env python3
'''
PyTest - Test of set_value function

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

# Local app modules
from appcore.conversion import set_value
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
    "String": {
        "valid": [
            "",
            "a string",
            14,
            192.3,
            { "dict_key": "dict_value"},
            "d5bf0b08-38a3-4116-8a7c-2655e6b54b64"
        ],
        "invalid": [],
        "type_list": [ DataType.STRING, DataType.STR ],
        "default": "Default String"
    },
    "Integer": {
        "valid": [ 14, 192.3 ],
        "invalid": [
            "",
            "a string",
            { "dict_key": "dict_value"},
            "d5bf0b08-38a3-4116-8a7c-2655e6b54b64"
        ],
        "type_list": [ DataType.INTEGER, DataType.INT ],
        "default": 7
    },
    "Dict": {
        "valid": [ "", {}, { "dict_key": "dict_value"} ],
        "invalid": [
            "a string",
            14,
            192.3,
            "d5bf0b08-38a3-4116-8a7c-2655e6b54b64"
        ],
        "type_list": [ DataType.DICTIONARY, DataType.DICT ],
        "default": { "key": "value" }
    },
    "UUID4": {
        "valid": [ "d5bf0b08-38a3-4116-8a7c-2655e6b54b64", ],
        "invalid": [
            "",
            "a string",
            14,
            192.3,
            { "dict_key": "dict_value"}
        ],
        "type_list": [ DataType.UUID4, ],
        "default": "1420a26b-b4c1-4345-ba0a-d42a94569fc9"
    }
}


###########################################################################
#
# The tests...
#
###########################################################################
#
# set_value
#
class Test_SetValue():
    '''
    Test Class - SetValue

    Attributes:
        None
    '''
    #
    # Test with valid data and valid type
    #
    @pytest.mark.parametrize("data", DATASET)
    def test_valid_data_valid_type(self, data):
        '''
        Test with valid data and valid types

        Args:
            data (str): Fixture containing the key to process from the
                DATASET dict

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert data in DATASET.keys()
        assert "valid" in DATASET[data]
        assert "type_list" in DATASET[data]

        for _type in DATASET[data]["type_list"]:
            for _entry in DATASET[data]["valid"]:
                # Set value - with correct info
                _res = set_value(
                    data=_entry,
                    type=_type,
                    default=DEFAULT_NO_MATCH
                )

                if not _entry:
                    # Entry was empty, 0, None, etc
                    assert not _res

                else:
                    assert _res
                    assert _res != DEFAULT_NO_MATCH


    #
    # Test with valid data and invalid type
    #
    @pytest.mark.parametrize("data", DATASET)
    def test_valid_data_invalid_type(self, data):
        '''
        Test with valid data and invalid type

        Args:
            data (str): Fixture containing the key to process from the
                DATASET dict

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert data in DATASET.keys()
        assert "valid" in DATASET[data]
        assert "type_list" in DATASET[data]

        for _entry in DATASET[data]["valid"]:
            # Set value - with incorrect type
            with pytest.raises(AssertionError):
                _ = set_value(
                    data=_entry,
                    type=INVALID_TYPE, # type: ignore
                    default=DEFAULT_NO_MATCH
                )


    #
    # Test with invalid data
    #
    @pytest.mark.parametrize("data", DATASET)
    def test_invalid_data(self, data):
        '''
        Test with invalid data that can't be comnverted to the specified type

        Args:
            data (str): Fixture containing the key to process from the
                INDATASET dict

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert data in DATASET.keys()
        assert "invalid" in DATASET[data]
        assert "type_list" in DATASET[data]
        assert "default" in DATASET[data]

        for _type in DATASET[data]["type_list"]:
            for _entry in DATASET[data]["invalid"]:
                # Set value - with invalid data 
                _res = set_value(
                    data=_entry,
                    type=_type,
                    default=DATASET[data]["default"]
                )
                assert _res
                assert _res == DATASET[data]["default"]
