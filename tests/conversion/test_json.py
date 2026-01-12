#!/usr/bin/env python3
'''
PyTest - Test of json functions

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
from appcore.conversion import from_json, to_json

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
    "String Data": {
        "data": "Just a plain string",
        "json": "\"Just a plain string\"",
        "container_type": "string"
    },
    "List Data": {
        "data": [ "A String", 1, True ],
        "json": "[\"A String\", 1, true]",
        "container_type": "list"
    },
    "Dict Data": {
        "data": { "key": "value", "2": 2 },
        "json": "{\"key\": \"value\", \"2\": 2}",
        "container_type": "dictionary"
    },
}

###########################################################################
#
# The tests...
#
###########################################################################
#
# 
#
class Test_JSON():
    '''
    Test Class - JSON

    Attributes:
        None
    '''
    #
    # Convert to JSON
    #
    @pytest.mark.parametrize("name", DATASET)
    def test_to_json(self, name):
        '''
        Test converting to JSON

        Args:
            name (str): Fixture containing the key to process from the
                DATASET dict

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATASET.keys()
        assert "data" in DATASET[name]
        assert "json" in DATASET[name]
        assert "container_type" in DATASET[name]

        # Convert without container
        _json = to_json(
            data=DATASET[name]["data"],
            container=False
        )
        assert _json == DATASET[name]["json"]

        # Convert with container
        _container_val = (
            f"{{\"value\": {DATASET[name]['json']}, "
            f"\"type\": \"{DATASET[name]['container_type']}\"}}"
        )
        _json = to_json(
            data=DATASET[name]["data"],
            container=True
        )
        assert _json == _container_val


    #
    # Convert from JSON
    #
    @pytest.mark.parametrize("name", DATASET)
    def test_from_json(self, name):
        '''
        Test converting from JSON

        Args:
            name (str): Fixture containing the key to process from the
                DATASET dict

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATASET.keys()
        assert "data" in DATASET[name]
        assert "json" in DATASET[name]
        assert "container_type" in DATASET[name]

        # Convert without container
        _data = from_json(
            data=DATASET[name]["json"],
            container=False
        )
        assert _data == DATASET[name]["data"]

        # Convert with container
        _container_val = (
            f"{{\"value\": {DATASET[name]['json']}, "
            f"\"type\": \"{DATASET[name]['container_type']}\"}}"
        )
        _data = from_json(
            data=_container_val,
            container=True
        )
        assert _data == DATASET[name]["data"]
