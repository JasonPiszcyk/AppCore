#!/usr/bin/env python3
'''
Message Frame Classes

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
import enum

# Local app modules
from appcore.multitasking import exception

# Imports for python variable type hints
from typing import Any

# Logging
from appcore.logging import configure_logger
# _log_level = "info"
_log_level = "debug"
log = configure_logger(
        name="TaskManager",
        log_file="/tmp/appcore.log",
        log_level=_log_level,
        to_console=False
)


###########################################################################
#
# Module variables/constants/types
#
###########################################################################
# The message types
class _MessageType(enum.Enum):
    OK              = "__message_type_ok__"
    ERROR           = "__message_type_error__"
    EMPTY           = "__message_type_empty__"
    EXIT            = "__message_type_exit__"
    REFRESH         = "__message_type_refresh__"
    DATA            = "__message_type_data__"


###########################################################################
#
# MessageFrame Class
#
###########################################################################
class _MessageFrame():
    '''
    Class to describe a queue message frame

    The queue message frame describes the structure of data to be passed
    in the message.

    Attributes:
        type (_MessageType): The type of message being sent
    '''
    def __init__(
            self,
            message_type: _MessageType = _MessageType.EMPTY,
            data: Any = None
    ):
        '''
        Initializes the instance.

        Args:
            message_type (_MessageType): The type of message being sent
            data: The data sent via the queue
        
        Returns:
            None

        Raises:
            None
        '''
        # Private properties
        if message_type in _MessageType:
            self.message_type: _MessageType = message_type
        else:
            self.message_type: _MessageType = _MessageType.OK

        # Attributes
        self.data = data


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
