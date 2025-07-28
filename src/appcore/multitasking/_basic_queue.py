#!/usr/bin/env python3
'''
Basic Queue - A queue class to implement a frame around data

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
# from queue import Queue
from queue import Empty as QueueEmpty

# Local app modules
from appcore.multitasking._message_frame import _MessageFrame, _MessageType
import appcore.multitasking.exception as exception

# Imports for python variable type hints
from typing import Any, Callable
from multiprocessing.managers import SyncManager

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
# _BasicQueue Class Definition
#
###########################################################################
class _BasicQueue():
    '''
    Class to describe a basic queue.

    Attributes:
        None
    '''
    #
    # __init__
    #
    def __init__(
            self,
            manager: SyncManager | None = None,
            frame_handler: Callable | None = None,
    ):
        '''
        Initialises the instance.

        Args:
            manager (SyncManager): An instance of the SyncManager class to
                provision the queue
            frame_handler (Callable): Callable to process the received
                frame. Takes 1 parameter - an instance of _MessageFrame

        Returns:
            None

        Raises:
            MultiTaskingManagerNotFoundError
                when the multiprocessing manager instance is not found
        '''
        # Private Attributes
        if manager:
            self._manager: SyncManager = manager
        else:
            raise exception.MultiTaskingManagerNotFoundError

        self._queue = self._manager.Queue()

        if callable(frame_handler):
            self._frame_handler: Callable | None = frame_handler
        else:
            self._frame_handler: Callable | None = None

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
            MultiTaskingQueueFrameExit:
                When the queue recieves an exit message frame
            MultiTaskingQueueFrameNotData:
                When the queue receives a frame that is not data.  For example
                the exit message.
        '''
        # Get a message from the queue
        try:
            _frame = self._queue.get(block=block, timeout=timeout)
        except QueueEmpty:
            return None

        # Confirm the message is in the correct format
        if not isinstance(_frame, _MessageFrame):
            raise exception.MultiTaskingQueueInvalidFormatError(
                "Get - Message format is incorrect"
            )

        if _frame.message_type == _MessageType.EXIT:
            raise exception.MultiTaskingQueueFrameExit

        if callable(self._frame_handler):
            self._frame_handler(_frame)

        if _frame.message_type == _MessageType.DATA:
            return _frame.data

        # The frame type is not data, so no further processing should occur
        raise exception.MultiTaskingQueueFrameNotData


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
            item (Any): The data to be sent
            block (bool): If True block until message place on queue. If false,
                return immediately
            timeout: Time (in seconds) to wait before returning
        
        Returns:
            None

        Raises:
            None
        '''
        _frame = _MessageFrame(message_type=_MessageType.DATA, data=item)

        # Put a message on the queue
        self._queue.put(_frame, block=block, timeout=timeout)


    #
    # put_action
    #
    def put_action(
            self,
            item: Any = None,
            block: bool = True,
            timeout: float | None = None,
            message_type: _MessageType = _MessageType.EMPTY,
    ):
        '''
        Put a message on the queue

        Args:
            item (Any): The data to be sent
            block (bool): If True block until message place on queue. If false,
                return immediately
            timeout: Time (in seconds) to wait before returning
            message_type (_MessageType): The type of message being sent
        
        Returns:
            None

        Raises:
            None
        '''
        _frame = _MessageFrame(message_type=message_type, data=item)

        # Put a message on the queue
        self._queue.put(_frame, block=block, timeout=timeout)


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
                _ = self._queue.get(block=False)
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
