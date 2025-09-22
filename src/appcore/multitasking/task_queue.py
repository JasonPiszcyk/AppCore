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
from __future__ import annotations

# Shared variables, constants, etc

# System Modules
import queue
import uuid

# Local app modules
from appcore.appcore_base import AppCoreModuleBase
from appcore.multitasking.message_frame import MessageFrame, MessageType

import appcore.multitasking.exception as exception

# Imports for python variable type hints
from typing import Any, Callable
from threading import Event as EventType


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
STOP_WAIT_TIMEOUT: float = 5.0


#
# Global Variables
#


###########################################################################
#
# TaskQueue Class Definition
#
###########################################################################
class TaskQueue(AppCoreModuleBase):
    '''
    Class to describe a TaskQueue.  Extension to a basic queue to include
    message framing, a listener function to listen for and process messages,
    and a mechanisim to provide a query/response server model

    Attributes:
        message_handler (Callable): Function to run to proces a message.
            The message handler should accept 1 parameter:
                frame - An instance of MessageFrame
            The message handler can return a response.  This will be
            place on the queue specified as 'response_queue' in the frame
            properties.
        keepalive_interval (int): If > 0, the listener will block for this
            number of seconds.  If a message is not received within this
            interval the exception 'MultiTaskingQueueKeepaliveIntervalExceeded'
            will be raised
        listener_running (bool) [ReadOnly]: Indicates if the listener is
            currently running in this process/thread.
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            queue: queue.Queue | None = None,
            message_handler: Callable | None = None,
            keepalive_interval: int = 0,
            stop_event: EventType | None = None,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            queue (Queue): An instance of a SyncManager queue
            message_handler (Callable): Callable to process the received
                message. The message handler should accept 1 parameter:
                    frame - An instance of MessageFrame
                The message handler can return a response.  This will be
                place on the queue specified as 'response_queue' in the frame
                properties.
            keepalive_interval (int): If > 0, the listener will block for this
                number of seconds.  If a message is not received within this
                interval the exception
                'MultiTaskingQueueKeepaliveIntervalExceeded' will be raised
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__listener_running: bool = False

        if not queue:
            raise exception.MultiTaskingQueueNotFoundError(
                "Queue instance missing from queue instantiation"
            )

        self.__queue: queue.Queue = queue

        if not stop_event:
            raise exception.MultiTaskingEventNotFoundError(
                "Stop event missing from Queue instantiation"
            )

        self.__stop_event: EventType = stop_event

        # Attributes
        self.message_handler = message_handler
        self.keepalive_interval = keepalive_interval


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
    # Queuing methods
    #
    ###########################################################################
    #
    # put_frame
    #
    def put_frame(
            self,
            frame: MessageFrame | None = None,
            block: bool = True,
            timeout: float | None = None
    ):
        '''
        Put a raw frame on the queue

        Args:
            frame (MessageFrame | None): The frame to be sent
            block (bool): If True block until message is placed on queue. If 
                false, return immediately
            timeout: Time (in seconds) to wait before returning
        
        Returns:
            None

        Raises:
            None
        '''
        if isinstance(frame, MessageFrame):
            # Put the frame on the queue
            self.__queue.put(frame, block=block, timeout=timeout)

    #
    # _put_type
    #
    def _put_type(
            self,
            message_type: MessageType = MessageType.EMPTY,
            item: Any = None,
            block: bool = True,
            timeout: float | None = None,
            response_queue: TaskQueue | None = None,
            message_id: str = "",
            session_id: str = ""
    ):
        '''
        Put a message on the queue with the specified type

        Args:
            message_type (MessageType): The type of message being sent
            item (Any): The data to be sent
            block (bool): If True block until message is placed on queue. If 
                false, return immediately
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
        self.logger.debug(f"Putting Message")

        _frame = MessageFrame(message_type=message_type, data=item)

        # Set Properties
        _frame.response_queue = response_queue
        _frame.message_id = message_id
        _frame.session_id = session_id

        # Put a message on the queue
        self.__queue.put(_frame, block=block, timeout=timeout)


    #
    # put
    #
    def put(
            self,
            item: Any = None,
            **kwargs
    ):
        '''
        Wrapper for _put_type specifying a type of 'DATA'

        Args:
            item (Any): The data to be sent
            kwargs: Keyword arguments to be passed to _put_type

        Returns:
            None

        Raises:
            None
        '''
        self.logger.debug(f"Putting DATA Message")

        # Put a message on the queue with a type of 'DATA'
        self._put_type(item=item, message_type=MessageType.DATA, **kwargs)


    #
    # query
    #
    def query(
            self,
            item: Any = None,
            response_queue: TaskQueue | None = None,
            **kwargs
    ) -> str:
        '''
        Wrapper for _put_type handling the query message type

        Args:
            item (Any): The data to be sent
            response_queue (Queue): The queue to send the response to
            kwargs: Keyword arguments to be passed to _put_type

        Returns:
            str: The session ID - reponse will have the same ID

        Raises:
            None
        '''
        self.logger.debug(f"Putting Query")
        if not response_queue:
            raise exception.MultiTaskingQueueNotFoundError(
                "A response queue is required for a query"
            )

        # Set any properties specifically for the query
        kwargs["session_id"] = str(uuid.uuid4())
        kwargs["response_queue"] = response_queue

        # Put a message on the queue with a type of 'query'
        self._put_type(
            item=item,
            message_type=MessageType.QUERY,
            **kwargs
        )

        # Return the session ID
        return kwargs["session_id"]


    #
    # get
    #
    def get(
            self,
            block: bool = True,
            timeout: float | None = None
    ) -> MessageFrame | None:
        '''
        Get a message frame from the queue

        Args:
            block (bool): If True block until message received. If false,
                check for message and return
            timeout: Time (in seconds) to wait before returning
        
        Returns:
            MessageFrame: The message frame sent via the queue

        Raises:
            MultiTaskingQueueInvalidFormatError:
                When an incorrectly formatted message is received
            MultiTaskingQueueFrameExit:
                When the queue recieves an exit message frame
            MultiTaskingQueueSystemFrame:
                When the queue receives a system frame.  For example the EXIT
                message.
        '''
        self.logger.debug(f"Getting Message")

        # Get a message from the queue
        _frame = self.__queue.get(block=block, timeout=timeout)

        # Confirm the message is in the correct format
        if not isinstance(_frame, MessageFrame):
            raise exception.MultiTaskingQueueInvalidFormatError(
                "Get - Message format is incorrect"
            )

        if _frame.message_type == MessageType.EXIT:
            raise exception.MultiTaskingQueueFrameExit

        if _frame.message_type in (
                MessageType.DATA,
                MessageType.QUERY,
                MessageType.RESPONSE
        ):
            return _frame

        # The frame should have been processed somewhere above
        raise exception.MultiTaskingQueueSystemFrame


    #
    # get_data
    #
    def get_data(
            self,
            block: bool = True,
            timeout: float | None = None
    ) -> Any:
        '''
        Get a message from the queue (stripping the frame)

        Args:
            block (bool): If True block until message received. If false,
                check for message and return
            timeout: Time (in seconds) to wait before returning

        Returns:
            Any: The data sent via the queue

        Raises:
            None
        '''
        self.logger.debug(f"Getting Message (no frame)")

        # Call 'get' - ignore properties
        _frame = self.get(block=block, timeout=timeout)
        return _frame.data if _frame else None


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
        self.logger.debug(f"Cleanup Queue")

        _queue_not_empty = True
        while _queue_not_empty:
            try:
                _, _ = self.__queue.get(block=False)
            except queue.Empty:
                _queue_not_empty = False


    ###########################################################################
    #
    # Processing Methods
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
        self.logger.debug(f"Starting Listener")

        # If the listener is already running, just return
        if self.__listener_running: return

        _timeout = None
        if isinstance(self.keepalive_interval, int) and \
                self.keepalive_interval > 0:
            _timeout=self.keepalive_interval

        self.__listener_running = True
        while self.__listener_running:
            _frame = None
            _keepalive_interval_exceeded = False

            try:
                _frame = self.get(block=True, timeout=_timeout)

            except queue.Empty:
                # Timed out - Should have received a keepalive before this
                _keepalive_interval_exceeded = True

            except exception.MultiTaskingQueueFrameExit:
                # The exit message frame was received
                self.__listener_running = False
                continue            

            except exception.MultiTaskingQueueSystemFrame:
                # The message was an internal message type (ignore it)
                continue

            if _keepalive_interval_exceeded:
                raise exception.MultiTaskingQueueKeepaliveIntervalExceeded(
                    "No Keepalive message received within interval"
                )

            if not _frame:
                raise exception.MultiTaskingQueueInvalidFormatError(
                    "Message did not contain a frame"
                )

            # Process the data
            if callable(self.message_handler):
                _response = self.message_handler(_frame)

                # Is a response required?
                if _frame.message_type == MessageType.QUERY:
                    self.respond(response=_response, query_frame=_frame)


        # Set the stop event
        if self.__stop_event: self.__stop_event.set()


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
        self.logger.debug(f"Stopping Listener")
        if remote or self.__listener_running:
            if self.__stop_event: self.__stop_event.clear()

            # Put an EXIT message on the queue
            self._put_type(message_type=MessageType.EXIT)

            # If the stop_event exists, wait for it
            if self.__stop_event:
                self.__stop_event.wait(timeout=STOP_WAIT_TIMEOUT)


    #
    # respond
    #
    def respond(
            self,
            response: Any = None,
            query_frame: MessageFrame | None = None,
            **kwargs
    ):
        '''
        Respond to a query

        Args:
            response (Any): The response to be sent
            query_frame (MessageFrame): The message frame from the original query
            response (Any): The queue to send the response to
            kwargs: Keyword arguments to be passed to _put_type

        Returns:
            None

        Raises:
            None
        '''
        self.logger.debug(f"Responding to Query")
        assert query_frame, "A query frame is required to create a response"

        if not isinstance(query_frame.response_queue, TaskQueue):
            raise exception.MultiTaskingQueueNotFoundError(
                "Cannot determine queue to use for response"
            )

        # Put the message on the response queue
        query_frame.response_queue._put_type(
            item=response,
            message_type=MessageType.RESPONSE,
            session_id=query_frame.session_id,
            **kwargs
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
