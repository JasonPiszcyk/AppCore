#!/usr/bin/env python3
'''
Basic Queue - Extension of queue class to implement a frame around data

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
from queue import Queue
from queue import Empty as QueueEmpty

# Local app modules
from appcore.multitasking._message_frame import _MessageFrame, _MessageType
import appcore.multitasking.exception as exception

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
# Queue Class Definition
#
###########################################################################
class _BasicQueue(Queue):
    '''
    Class to describe the TaskManager.

    The TaskManager is used to create any required multitasking resources

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        super().__init__(*args, **kwargs)

        # Private Attributes

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################


    ###########################################################################
    #
    # Methods
    #
    ###########################################################################
    #
    # get
    #
    def get(
            self,
            block: bool = True,
            timeout: float | None = None
    ) -> Any:
        '''
        Get a message from the queue

        Args:
            block (bool): If True block until message received. If false,
                check for message and return
            timeout: Time (in seconds) to wait before returning
        
        Returns:
            Any: The data sent via the queue

        Raises:
            MultiTaskingQueueInvalidFormatError:
                When an incorrectly formatted message is received 
        '''
        # Get a message from the queue
        try:
            _msg = super().get(block=block, timeout=timeout)
        except QueueEmpty:
            return None

        # Confirm the message is in the correct format
        if not isinstance(_msg, _MessageFrame):
            raise exception.MultiTaskingQueueInvalidFormatError(
                "Get - Message format is incorrect"
            )

        return _msg.data


    #
    # put
    #
    def put(
            self,
            item: Any = None,
            block: bool = True,
            timeout: float | None = None
    ):
        '''
        Put a message on the queue

        Args:
            data (Any): The data to be sent
        
        Returns:
            None

        Raises:
            None
        '''
        _frame = _MessageFrame(message_type=_MessageType.DATA, data=item)

        # Put a message on the queue
        super().put(_frame, block=block, timeout=timeout)


    #
    # cleanup
    #
    def cleanup(self):
        '''
        Clean up the queue (eg remove all messages)

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        _queue_not_empty = True
        while _queue_not_empty:
            try:
                _ = super().get(block=False)
            except QueueEmpty:
                _queue_not_empty = False


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
