#!/usr/bin/env python3
'''
Extension of _basic_queue to include a listener

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

# Local app modules
from appcore.multitasking._basic_queue import _BasicQueue
from appcore.multitasking._message_frame import _MessageType
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
# Queue Class Definition
#
###########################################################################
class Queue(_BasicQueue):
    '''
    Class to describe a Queue.  Extension to basic queue to include a
    listener function to listen for, and process messages.

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            message_handler: Callable | None = None,
            stop_barrier: Barrier | None = None,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            message_handler (Callable): Callable to process the received
                message. Takes 1 parameter of type Any which is the data
                contained in the frame.
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        super().__init__(*args, **kwargs)

        # Private Attributes
        self._listener_running = False

        if not stop_barrier:
            raise exception.MultiTaskingBarrierNotFoundError(
                "Stop barrier missing from Queue instatiation"
            )

        self._stop_barrier = stop_barrier

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
        return self._listener_running


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
        if self._listener_running: return

        self._listener_running = True
        while self._listener_running:
            try:
                _msg = self.get()

            except exception.MultiTaskingQueueFrameExit:
                # The exit message frame was received
                self._listener_running = False
                continue            

            except exception.MultiTaskingQueueFrameNotData:
                # The message was an internal message type (ignore it)
                continue

            # Process the data
            if callable(self._message_handler):
                self._message_handler(_msg)

        # If the stop_barrier is set, notify it
        if self._stop_barrier:
            try:
                self._stop_barrier.wait(timeout=BARRIER_WAIT_TIMEOUT)
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
        if remote or self._listener_running:
            # Put an EXIT message on the queue
            self.put_action(message_type=_MessageType.EXIT)

            # If the stop_barrier is set, notify it
            if self._stop_barrier:
                try:
                    self._stop_barrier.wait(timeout=BARRIER_WAIT_TIMEOUT)
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
