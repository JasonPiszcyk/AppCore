#!/usr/bin/env python3
'''
Queue Message Classes

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
from . import exception

# Imports for python variable type hints


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
    Base Class to describe a queue message frame

    The queue message frame describes the structure of data to be passed
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
    Class to describe a message passed over queues

    Each instance of the class describes a message that the multitasking system
    can send via queues.  This class encapsulates a MessageFrame which is used
    for structuring data sent over the queue

    Attributes:
        message_type (MessageType) [ReadOnly]: The type of message being sent
        frame (Subclass of QueueMessageFrameBase) [ReadOnly]: Structure of the
            data passed in the message.
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
            MultiTaskingQueueInvalidFrameError:
                When the message frame is not a subclass of MessageFrameBase
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
            raise exception.MultiTaskingQueueInvalidFrameError(
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
# In case this is run directly rather than imported...
#
###########################################################################
'''
Handle case of being run directly rather than imported
'''
if __name__ == "__main__":
    pass
