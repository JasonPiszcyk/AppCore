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
import enum
import queue

# Local app modules
import src.appcore.multitasking.exceptions as exceptions

# Imports for python variable type hints
from typing import Callable
from queue import Queue


###########################################################################
#
# Module variables/constants/types
#
###########################################################################
# The message types
class MessageType(enum.Enum):
    OK              = "__message_type_ok__"
    ERROR           = "__message_type_error__"
    EMPTY           = "__message_type_empty__"
    EXIT            = "__message_type_exit__"
    REFRESH         = "__message_type_refresh__"
    DATA            = "__message_type_data__"


###########################################################################
#
# MessageFrameBase Class
#
###########################################################################
class MessageFrameBase():
    '''
    Class to describe a queue message frame

    The queue message frame describe the structure of data to be passed
    in the message.

    This is a base class hich should be inherited to build the class in use.

    Attributes:
        type (MessageType): The type of message being sent
    '''
    def __init__(self):
        '''
        Initializes the instance.

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        self.name = __class__.__name__


###########################################################################
#
# MessageFrames - Different Frame types based on MessageFrameBase
#
###########################################################################
#
# Queue Message Frames derived from the MessageFrameBase class
#
class BasicMessageFrame(MessageFrameBase):
    ''' Basic Message Frame '''
    def __init__(self, text: str = ""):
        super().__init__()
        self.text = text


###########################################################################
#
# QueueMessage Class
#
###########################################################################
class QueueMessage():
    '''
    Class to describe message passed over queues

    Each instance of the class describes a message that the multitasking system
    can send via queues.  This class encapsulates a MessageFrame which is used
    for structuring data sent over the queue

    Attributes:
        message_type (MessageType): The type of message being sent
        frame: Structure of the data passed in the message. Derived from
            QueueMessageFrameBase
    '''

    #
    # __init__
    #
    def __init__(
            self,
            message_type: MessageType = MessageType.EMPTY,
            frame: type[MessageFrameBase] | MessageFrameBase = BasicMessageFrame
    ):
        '''
        Initializes the instance.

        Args:
            message_type (MessageType): The type of message being sent
            frame: Structure of the data passed in the message. Derived from
                QueueMessageFrameBase
        
        Returns:
            None

        Raises:
            None
        '''
        # Private properties
        if message_type in MessageType:
            self.__type: MessageType = message_type
        else:
            self.__type: MessageType = MessageType.OK

        # Attributes
        if not isinstance(frame, type):
            # We got a message instance not the class
            _class: type = frame.__class__
            _frame = frame
        else:
            # Frame was passed as the class (not an instance)
            _class: type = frame
            _frame = BasicMessageFrame()

        # Check if this is the base class or a subclass of it
        if isinstance(_class, MessageFrameBase) or \
                issubclass(_class, MessageFrameBase):

            self.__frame: MessageFrameBase = _frame
        else:
            raise exceptions.MultiTaskingQueueInvalidFrame(
                "QueueMessage: Frame not valid when creating message"
            )


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # type
    #
    @property
    def type(self):
        '''
        The messsage type
        '''
        return self.__type


    #
    # frame
    #
    @property
    def frame(self):
        '''
        The messsage frame
        '''
        return self.__frame


###########################################################################
#
# TaskQueue Class
#
###########################################################################
class TaskQueue():
    '''
    Task to manage a queue

    A queue can be used to communicate between threads/processes.  This class
    can create the queue, get and send message to the queue and also provide
    a 'looping' function to process a queue continuously.

    Attributes:
        message_type (MessageType): The type of message being sent
        frame: Structure of the data passed in the message. Derived from
            QueueMessageFrameBase
    '''

    #
    # __init__
    #
    def __init__(self):
        '''
        Initializes the instance.

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Private properties
        self.__queue: Queue = queue.Queue()
        self.__listener_running = False


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
            MultiTaskingQueueInvalidFormat: When message not in correct format
        '''
        # Get a message from the queue
        try:
            _msg = self.__queue.get(block=block, timeout=timeout)
        except queue.Empty:
            _msg = QueueMessage()

        # Confirm the message is in the correct format
        if not isinstance(_msg, QueueMessage):
            raise exceptions.MultiTaskingQueueInvalidFormat(
                "GET - Message format is incorrect"
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
            MultiTaskingQueueInvalidFormat: When message not in correct format
        '''
        assert msg

        # Confirm the message is in the correct format
        if not isinstance(msg.__class__, QueueMessage):
            raise exceptions.MultiTaskingQueueInvalidFormat(
                "Put - Message format is incorrect"
            )

        # Put a message on the queue
        self.__queue.put(msg)


    ###########################################################################
    #
    # Methods to send to the queue
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
            MultiTaskingQueueInvalidFormat: When message not in correct format
        '''
        # Put a message on the queue
        self.__queue.put(QueueMessage(message_type=MessageType.OK))


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
            MultiTaskingQueueInvalidFormat: When message not in correct format
        '''
        # Put a message on the queue
        self.__queue.put(QueueMessage(message_type=MessageType.ERROR))


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
            MultiTaskingQueueInvalidFormat: When message not in correct format
        '''
        # Put a message on the queue
        self.__queue.put(QueueMessage(message_type=MessageType.EXIT))


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
            MultiTaskingQueueInvalidFormat: When message not in correct format
        '''
        # Put a message on the queue
        self.__queue.put(QueueMessage(message_type=MessageType.REFRESH))


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
            MultiTaskingQueueInvalidFormat:
                When message not in correct format
            MultiTaskingQueueInvalidFrame:
                When message frame is invalid
        '''
        # Create message - Will raise exception if message is invalid
        _msg = QueueMessage(message_type=MessageType.DATA, frame=frame)

        # Put a message on the queue
        self.__queue.put(_msg)


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
        self.__listener_running = True
        while self.__listener_running:
            _invalid_msg = False
            _invalid_message_frame = BasicMessageFrame()

            try:
                _msg = self.get()

            except exceptions.MultiTaskingQueueInvalidFormat:
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

                # The refresh signal
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
    def listener_stop(self):
        '''
        Send a DATA message

        Args:
            None
        
        Returns:
            None

        Raises:
            MultiTaskingQueueInvalidFormat:
                When message not in correct format
            MultiTaskingQueueInvalidFrame:
                When message frame is invalid
        '''
        if self.__listener_running:
            # Put an EXIT message on the queue
            self.send_exit()


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
