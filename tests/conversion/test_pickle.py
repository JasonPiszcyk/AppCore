#!/usr/bin/env python3
'''
PyTest - Test of pickle functions

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
from appcore.conversion import from_pickle, to_pickle

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
    "String Data": "Just a plain string",
    "List Data": [ "A String", 1, True ],
    "Dict Data": { "key": "value", "2": 2 },
}

###########################################################################
#
# The tests...
#
###########################################################################
#
# 
#
class Test_Pickle():
    '''
    Test Class - Pickle

    Attributes:
        None
    '''
    #
    # Convert to/from pickle
    #
    @pytest.mark.parametrize("name", DATASET)
    def test_to_from_pickle(self, name):
        '''
        Test converting to/from Pickle

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

        _val = DATASET[name]

        # Convert to pickle
        _pickle = to_pickle(data=_val)
        assert isinstance(_pickle, bytes)

        # Convert from pickle
        _pickle_val = from_pickle(data=_pickle)
        assert _pickle_val == _val
