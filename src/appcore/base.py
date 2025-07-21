#!/usr/bin/env python3
'''
Shared info (eg variables, constants types)

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

# System Modules
import uuid

# Local app modules
from .shared import DataType

# Imports for python variable type hints
from typing import Any


###########################################################################
#
# Module variables/constants/types
#
###########################################################################


###########################################################################
#
# Convenience/Helper Functions
#
###########################################################################
#
# set_value
#
def set_value(
        data: Any = None,
        type: DataType = DataType.STRING,
        default: Any = None
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
    assert type in DataType

    _val:Any = None

    try:
        if type == DataType.INT or type == DataType.INTEGER:
            _val = int(data)
        elif type == DataType.BOOL or type == DataType.BOOLEAN:
            _val = bool(data)
        elif type == DataType.DICT or type == DataType.DICTIONARY:
            _val = dict(data)
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

