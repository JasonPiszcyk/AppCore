#!/usr/bin/env python3
'''
General validation functions

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
# is_valid_log_level_string
#
def is_valid_log_level_string(
        log_level: str = "",
) -> bool:
    '''
    Validate the supplied log level string is valid

    Args:
        log_level (str): A string representing a log level

    Returns:
        None

    Raises:
        None
    '''
    # Check if the log level string is valid
    _log_levels: list = list([_entry.value for _entry in LoggingLevel])
    return log_level in _log_levels


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
