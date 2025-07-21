#!/usr/bin/env python3
'''
Queue Message Class

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
from multiprocessing import Queue as ProcessQueue
from multiprocessing import Barrier 
from threading import BrokenBarrierError
from queue import Empty as QueueEmpty
from queue import Queue as ThreadQueue


# Local app modules
from .queue_message import QueueMessage, MessageType
from .queue_message import MessageFrameBase, BasicMessageFrame
from . import exception

# Imports for python variable type hints
from typing import Callable
from multiprocessing.synchronize import Barrier as BarrierClass


###########################################################################
#
# Module variables/constants/types
#
###########################################################################
# Max wait time for task to acknowledge listener exit message
LISTENER_EXIT_TIMEOUT: float = 10.0

###########################################################################
#
# TaskQueue Class
#
###########################################################################
class TaskQueue():
    '''
    A queue for the tasking system

    A queue to communicate between threads/process.  The class handles the
    encapsulation of the message in a frame based on the message type.

    Attributes:
        message_type (MessageType): The type of message being sent
        frame: Structure of the data passed in the message. Derived from
            QueueMessageFrameBase
    '''

    #
    # __init__
    #
    def __init__(self, for_thread: bool = True):
        '''
        Initializes the instance.

        Args:
            for_thread (bool): If True create a queue suitable for a thread,
                if false create one suitable for a process
        
        Returns:
            None

        Raises:
            None
        '''
        # Private properties
        if for_thread:
            self.__queue: ThreadQueue | ProcessQueue = ThreadQueue()
        else:
            self.__queue: ThreadQueue | ProcessQueue = ProcessQueue()

        self.__listener_running = False
        self.__listener_exit_barrier: BarrierClass = Barrier(
            parties=2, action=None, timeout=LISTENER_EXIT_TIMEOUT
        )


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################


    ###########################################################################
    #
    # Queue processing
    #
    ###########################################################################
    #
    # get
    #
    def get(
            self,
            block: bool = True,
            timeout: float | None = None
    ) -> QueueMessage:
        '''
        Get a message from the queue

        Args:
            block (bool): If True block until message received. If false,
                check for message and return
            timeout: Time (in seconds) to wait before returning
        
        Returns:
            QueueMessage: A QueueMessage instance containing the message. If
                no message received, the message type is set to EMPTY

        Raises:
            MultiTaskingQueueInvalidFormatError: When message not in correct format
        '''
        # Get a message from the queue
        try:
            _msg = self.__queue.get(block=block, timeout=timeout)
        except QueueEmpty:
            _msg = QueueMessage()

        # Confirm the message is in the correct format
        if not isinstance(_msg, QueueMessage):
            raise exception.MultiTaskingQueueInvalidFormatError(
                "Get - Message format is incorrect"
            )

        return _msg


    #
    # put
    #
    def put(
            self,
            msg: QueueMessage | None = None,
    ):
        '''
        Put a message on the queue

        Args:
            msg (QueueMessage): The message to be sent
        
        Returns:
            None

        Raises:
            MultiTaskingQueueInvalidFormatError: When message not in correct format
        '''
        assert msg

        # Confirm the message is in the correct format
        if not isinstance(msg, QueueMessage):
            raise exception.MultiTaskingQueueInvalidFormatError(
                "Put - Message format is incorrect"
            )

        # Put a message on the queue
        self.__queue.put(msg)


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
                _ = self.__queue.get(block=False)
            except QueueEmpty:
                _queue_not_empty = False


    ###########################################################################
    #
    # Methods to send specific types to the queue
    #
    ###########################################################################
    #
    # send_OK
    #
    def send_OK(self):
        '''
        Send a message - OK

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Put a message on the queue
        self.put(QueueMessage(message_type=MessageType.OK))


    #
    # send_error
    #
    def send_error(self):
        '''
        Send a message - ERROR

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Put a message on the queue
        self.put(QueueMessage(message_type=MessageType.ERROR))


    #
    # send_exit
    #
    def send_exit(self):
        '''
        Send a message - EXIT

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Put a message on the queue
        self.put(QueueMessage(message_type=MessageType.EXIT))


    #
    # send_refresh
    #
    def send_refresh(self):
        '''
        Send a message - REFRESH

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Put a message on the queue
        self.put(QueueMessage(message_type=MessageType.REFRESH))


    #
    # send
    #
    def send(
            self,
            frame: type[MessageFrameBase] | MessageFrameBase = BasicMessageFrame
    ):
        '''
        Send a DATA message

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Create message - Will raise exception if message is invalid
        _msg = QueueMessage(message_type=MessageType.DATA, frame=frame)

        # Put a message on the queue
        self.put(_msg)


    ###########################################################################
    #
    # Processing Loop for receiving queue messages
    #
    ###########################################################################
    #
    # listener
    #
    def listener(
            self,
            on_recv: Callable | None = None,
            on_invalid: Callable | None = None,
            on_msg_ok: Callable | None = None,
            on_msg_error: Callable | None = None,
            on_msg_exit: Callable | None = None,
            on_msg_refresh: Callable | None = None,
    ):
        '''
        Listen for messages on the queue and hand off to processing functions
        as they arrive.

        Each callback function will be passed a message frame as the first and
        only parameter. For 'on_invalid' a new message BasicMessageFrame is
        constructed and the error message stored in the text.

        Args:
            on_recv (Callable): Callable to handle a received message
            on_invalid (Callable): Callable to perform an action when an
                invalid message received
            on_msg_ok (Callable): Processing to perform when a message with
                type 'OK' is recived
            on_msg_error (Callable): Processing to perform when a message with
                type 'ERROR' is recived.  If there is an issue with the
                message itself it is prcessed via 'on_invalid'
            on_msg_exit (Callable): Processing to perform when the EXIT message
                is received
            on_msg_ok (Callable): Processing to perform when a REFRESH message
                is received
        
        Returns:
            None

        Raises:
            None
        '''
        # If the listener is already running, just return
        if self.__listener_running: return

        self.__listener_running = True
        while self.__listener_running:
            _invalid_msg = False
            _invalid_message_frame = BasicMessageFrame()

            try:
                _msg = self.get()

            except exception.MultiTaskingQueueInvalidFormatError:
                # Received message is invalid
                _invalid_msg = True
                _invalid_message_frame.text = "Message format is invalid"
                _msg = QueueMessage(frame=_invalid_message_frame)


            if not _invalid_msg:
                # The exit signal
                if _msg.type == MessageType.EXIT:
                    # Run any additional processing
                    if callable(on_msg_exit):
                        on_msg_exit(_msg.frame)

                    self.__listener_running = False

                    try:
                        self.__listener_exit_barrier.wait()
                    except BrokenBarrierError:
                        raise exception.MultiTaskingQueueListenerShutdownError (
                            "Queue Listener exit sync failed"
                        )

                    continue

                # The refresh signal
                elif _msg.type == MessageType.REFRESH:
                    if callable(on_msg_refresh):
                        on_msg_refresh(_msg.frame)

                    continue

                # Message type of 'OK'
                elif _msg.type == MessageType.OK:
                    if callable(on_msg_ok):
                        on_msg_ok(_msg.frame)

                    continue

                # The refresh signal
                elif _msg.type == MessageType.ERROR:
                    if callable(on_msg_error):
                        on_msg_error(_msg.frame)

                    continue

                # A DATA message
                elif _msg.type == MessageType.DATA:
                    if callable(on_recv):
                        on_recv(_msg.frame)
 
                    continue

                # An unknown message
                else:
                    _invalid_msg = True
                    _invalid_message_frame.text = "Unknown message type"

            # _invalid_msg may be set while processing the message above
            if _invalid_msg:
                if callable(on_invalid):
                    on_invalid(_invalid_message_frame)


    #
    # listener_stop
    #
    def listener_stop(self, remote=False):
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
            self.send_exit()

            # Wait for the queue to acknowledge the message
            try:
                self.__listener_exit_barrier.wait()
            except BrokenBarrierError:
                raise exception.MultiTaskingQueueListenerShutdownError (
                    "Queue Listener failed to shutdown correctly"
                )


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
