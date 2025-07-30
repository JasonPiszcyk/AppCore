#!/usr/bin/env python3
'''
Extension of the queue to include additional functionality

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
from queue import Empty as QueueEmpty

# Local app modules
from appcore.multitasking._message_frame import _MessageFrame, _MessageType
from appcore.multitasking._message_frame import MessageFrameProperties

import appcore.multitasking.exception as exception
from threading import Barrier, BrokenBarrierError

# Imports for python variable type hints
from typing import Any, Callable

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
BARRIER_WAIT_TIMEOUT: float = 0.5
LISTENER_SHUTDOWN_TIMEOUT: float = 5.0


#
# Global Variables
#


###########################################################################
#
# TaskQueue Class Definition
#
###########################################################################
class TaskQueue():
    '''
    Class to describe a TaskQueue.  Extension to a basic queue to include
    message framing, a listener function to listen for and process messages,
    and a mechanisim to provide a query/response server model

    Attributes:
        listener_running (bool) [ReadOnly]: Indicates if the listener is
            currently running in this process/thread.
    '''

    #
    # __init__
    #
    def __init__(
            self,
            queue: TaskQueue | None = None,
            frame_handler: Callable | None = None,
            message_handler: Callable | None = None,
            stop_barrier: Barrier | None = None,
    ):
        '''
        Initialises the instance.

        Args:
            queue (Queue): An instance of a SyncManager queue
            frame_handler (Callable): Callable to process the received
                frame. Takes 1 parameter - an instance of _MessageFrame
            message_handler (Callable): Callable to process the received
                message. The message handler should accept 2 parameters:
                    The message
                    A queue to respond to (if None then no response)

        Returns:
            None

        Raises:
            None
        '''
        # Private Attributes
        self.__listener_running: bool = False

        if not queue:
            raise exception.MultiTaskingQueueNotFoundError(
                "Queue instance missing from queue instantiation"
            )

        self.__queue: TaskQueue = queue

        if callable(frame_handler):
            self.__frame_handler: Callable | None = frame_handler
        else:
            self.__frame_handler: Callable | None = None

        if not stop_barrier:
            raise exception.MultiTaskingBarrierNotFoundError(
                "Stop barrier missing from Queue instatiation"
            )

        self.__stop_barrier: Barrier = stop_barrier

        if callable(message_handler):
            self._message_handler: Callable | None = message_handler
        else:
            self._message_handler: Callable | None = None

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # listener_running
    #
    @property
    def listener_running(self) -> bool:
        ''' Boolean property indicating if the listener is running '''
        return self.__listener_running


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
    ) -> tuple[Any, MessageFrameProperties | None]:
        '''
        Get a message and properties from the queue

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
            _frame = self.__queue.get(block=block, timeout=timeout)
        except QueueEmpty:
            return None, None

        # Confirm the message is in the correct format
        if not isinstance(_frame, _MessageFrame):
            raise exception.MultiTaskingQueueInvalidFormatError(
                "Get - Message format is incorrect"
            )

        if _frame.message_type == _MessageType.EXIT:
            raise exception.MultiTaskingQueueFrameExit

        if callable(self.__frame_handler):
            self.__frame_handler(_frame)

        if _frame.message_type == _MessageType.DATA:
            return _frame.data, _frame.properties

        # The frame type is not data, so no further processing should occur
        # (and we should not have got to this point as it should have already
        # been handled)
        raise exception.MultiTaskingQueueFrameNotData


    #
    # get_data
    #
    def get_data(
            self,
            block: bool = True,
            timeout: float | None = None
    ) -> Any:
        '''
        Get a message from the queue (ignore the properties)

        Args:
            block (bool): If True block until message received. If false,
                check for message and return
            timeout: Time (in seconds) to wait before returning
        
        Returns:
            Any: The data sent via the queue

        Raises:
            None
        '''
        # Call 'get' - ignore properties
        _data, _ = self.get(block=block, timeout=timeout)
        return _data


    #
    # put
    #
    def put(
            self,
            item: Any = None,
            block: bool = True,
            timeout: float | None = None,
            response_queue: TaskQueue | None = None,
            message_id: str = "",
            session_id: str = ""
    ):
        '''
        Put a message on the queue

        Args:
            item (Any): The data to be sent
            block (bool): If True block until message place on queue. If false,
                return immediately
            timeout: Time (in seconds) to wait before returning
            response_queue (Queue): The queue to send the response to
            message_id (str): An ID for the message (UUID will be generated if
                empty)
            session_id (str): The message can be related to other messages
                via this ID
        
        Returns:
            None

        Raises:
            None
        '''
        _frame = _MessageFrame(message_type=_MessageType.DATA, data=item)

        # Set Properties
        _frame.properties.response_queue = response_queue
        _frame.properties.message_id = message_id
        _frame.properties.session_id = session_id

        # Put a message on the queue
        self.__queue.put(_frame, block=block, timeout=timeout)


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
        self.__queue.put(_frame, block=block, timeout=timeout)


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
                _, _ = self.__queue.get(block=False)
            except QueueEmpty:
                _queue_not_empty = False


    ###########################################################################
    #
    # Methods
    #
    ###########################################################################
    #
    # listener
    #
    def listener(self):
        '''
        Listen for messages on the queue and hand off the message_handler.

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # If the listener is already running, just return
        if self.__listener_running: return

        self.__listener_running = True
        while self.__listener_running:
            try:
                _msg = self.get()

            except exception.MultiTaskingQueueFrameExit:
                # The exit message frame was received
                self.__listener_running = False
                continue            

            except exception.MultiTaskingQueueFrameNotData:
                # The message was an internal message type (ignore it)
                continue

            # Process the data
            if callable(self._message_handler):
                self._message_handler(_msg)

        # If the stop_barrier is set, notify it
        if self.__stop_barrier:
            try:
                self.__stop_barrier.wait(timeout=BARRIER_WAIT_TIMEOUT)
            except BrokenBarrierError:
                # Ignore this - The other process/thread should be waiting
                # (and this is to let the caller know we are done)
                pass


    #
    # listener_stop
    #
    def listener_stop(
            self,
            remote: bool = False
    ):
        '''
        Stop the listener

        Args:
            remote (boolean): If true, the listener is in a separate process.
        
        Returns:
            None

        Raises:
            MultiTaskingQueueListenerShutdownError:
                When the Listener does not acknowledge the exit message
        '''
        if remote or self.__listener_running:
            # Put an EXIT message on the queue
            self.put_action(message_type=_MessageType.EXIT)

            # If the stop_barrier is set, notify it
            if self.__stop_barrier:
                try:
                    self.__stop_barrier.wait(timeout=BARRIER_WAIT_TIMEOUT)
                except BrokenBarrierError:
                    # Ignore this - The other process/thread should be waiting
                    # (and this is to let the caller know we are done)
                    pass


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
