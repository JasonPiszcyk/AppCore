#!/usr/bin/env python3
'''
General functions

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
import datetime

# Local app modules

# Imports for python variable type hints
from appcore.typing import LoggingLevel


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


#
# Global Variables
#


###########################################################################
#
# Module
#
###########################################################################
#
# timestamp
#
def timestamp(offset: int = 0) -> int:
    '''
    Create a timestamp (in seconds) since the epoch to now

    Args:
        offset (int): Number of seconds to offset the timestamp by

    Returns:
        int: The number of seconds since the epoch to now, +/- offset

    Raises:
        AssertionError:
            When the offset is not an integer value
    '''
    assert isinstance(offset, int)

    # Get the current time
    _now = datetime.datetime.now(datetime.timezone.utc)

    # Return the timestamp
    return int(_now.timestamp()) + offset


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
