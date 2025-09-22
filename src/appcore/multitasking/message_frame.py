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
from __future__ import annotations

# Shared variables, constants, etc

# System Modules
import enum
import uuid

# Local app modules
from appcore.multitasking import exception

# Imports for python variable type hints
from typing import Any


###########################################################################
#
# Module variables/constants/types
#
###########################################################################
# The message types
class MessageType(enum.Enum):
    EMPTY           = "__message_type_empty__"
    EXIT            = "__message_type_exit__"
    DATA            = "__message_type_data__"
    QUERY           = "__message_type_query__"
    RESPONSE        = "__message_type_response__"


###########################################################################
#
# MessageFrame Class
#
###########################################################################
class MessageFrame():
    '''
    Class to describe a queue message frame

    The queue message frame describes the structure of data to be passed
    in the message.

    Attributes:
        message_type (MessageType): The type of message being sent
        data (Any): The data sent via the queue
        response_queue (TaskQueue): The queue to send the response to
        message_id (str): An ID for the message (UUID will be generated if
            empty)
        session_id (str): The message can be related to other messages
            via this ID
    '''

    #
    # __init__
    #
    def __init__(
            self,
            message_type: MessageType = MessageType.EMPTY,
            data: Any = None,
            response_queue: Any = None,
            message_id: str = "",
            session_id: str = ""
    ):
        '''
        Initializes the instance.

        Args:
            message_type (MessageType): The type of message being sent
            data: The data sent via the queue
            response_queue (TaskQueue): The queue to send the response to
            message_id (str): An ID for the message (UUID will be generated if
                empty)
            session_id (str): The message can be related to other messages
                via this ID
        
        Returns:
            None

        Raises:
            None
        '''
        # Private properties
        self.__response_queue: Any = None
        self.__message_id: str = ""
        self.__session_id: str = ""

        # Attributes
        if message_type in MessageType:
            self.message_type: MessageType = message_type
        else:
            self.message_type: MessageType = MessageType.EMPTY

        # The data
        self.data = data

        # Message Properties
        self.response_queue = response_queue
        self.message_id = message_id if message_id else str(uuid.uuid4())
        self.session_id = session_id


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # response_queue
    #
    @property
    def response_queue(self) -> Any:
        ''' The queue to send a response to '''
        return self.__response_queue
        

    @response_queue.setter
    def response_queue(self, value: Any = None) -> None:
        ''' The queue to send a response to '''
        from appcore.multitasking.task_queue import TaskQueue
        if value:
            assert isinstance(value, TaskQueue), "Response Queue is not valid"
            self.__response_queue = value
        else:
            self.__response_queue = None


    #
    # message_id
    #
    @property
    def message_id(self) -> str:
        ''' An ID for the message '''
        return self.__message_id


    @message_id.setter
    def message_id(self, value: str = "") -> None:
        ''' An ID for the message '''
        if value:
            assert isinstance(value, str), "Message ID must be a string"
            self.__message_id = value
        else:
            self.__message_id = ""


    #
    # session_id
    #
    @property
    def session_id(self) -> str:
        ''' An ID to relate messages to each other '''
        return self.__session_id


    @session_id.setter
    def session_id(self, value: str = "") -> None:
        ''' An ID to relate messages to each other '''
        if value:
            assert isinstance(value, str), "Session ID must be a string"
            self.__session_id = value
        else:
            self.__session_id = ""


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
