#!/usr/bin/env python3
'''
The MultiTask task manager.  This should be used to create any resources.

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
from multiprocessing import get_context
from threading import Event

# Local app modules
from appcore.multitasking.task import Task, TaskType
from appcore.multitasking.queue import Queue as TaskQueue

# Imports for python variable type hints
from typing import Callable
from multiprocessing.context import SpawnContext
from multiprocessing.managers import SyncManager
from threading import Lock, Barrier
from appcore.typing import KeywordDictType

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
DEFAULT_BARRIER_TIMEOUT: float = 5.0

#
# Global Variables
#


###########################################################################
#
# TaskManager Class Definition
#
###########################################################################
class TaskManager():
    '''
    Class to describe the TaskManager.

    The TaskManager is used to create any required multitasking resources

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(self):
        '''
        Initialises the instance.

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Private Attributes
        self.__context: SpawnContext = get_context("spawn")
        self.__manager: SyncManager = self.__context.Manager()

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # context
    #
    @property
    def context(self) -> SpawnContext:
        ''' The context used by the multiprocessing library '''
        return self.__context


    #
    # manager
    #
    @property
    def manager(self) -> SyncManager:
        ''' The multiprocessing SyncManger instance to use '''
        return self.__manager


    ###########################################################################
    #
    # Resource Creation Methods
    #
    ###########################################################################
    #
    # Thread
    #
    def Thread(
            self,
            name: str = "",
            target: Callable | None = None,
            kwargs: KeywordDictType = {},
            stop_function: Callable | None = None,
            stop_kwargs: KeywordDictType = {},
     ) -> TaskType:
        '''
        Create a thread based Task

        Args:
            name (str): An identifier for the task
            target (Callable): Function to run in the new thread/process
            kwargs (dict): Arguments to pass to the target function
            stop_function (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass the stop function

        Returns:
            TaskType: The task created (as a thread based task)

        Raises:
            None
        '''
        log.debug(f"Creating thread ({name})")
        return Task(
            name=name,
            context=self.__context,
            manager=self.__manager,
            target=target,
            kwargs=kwargs,
            stop_function=stop_function,
            stop_kwargs=stop_kwargs,
            task_type="thread"
        )


    #
    # Process
    #
    def Process(
            self,
            name: str = "",
            target: Callable | None = None,
            kwargs: KeywordDictType = {},
            stop_function: Callable | None = None,
            stop_kwargs: KeywordDictType = {},
     ) -> TaskType:
        '''
        Create a process based Task

        Args:
            name (str): An identifier for the task
            target (Callable): Function to run in the new thread/process
            kwargs (dict): Arguments to pass to the target function
            stop_function (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass the stop function

        Returns:
            TaskType: The task created (as a process based task)

        Raises:
            None
        '''
        log.debug(f"Creating process ({name})")
        return Task(
            name=name,
            context=self.__context,
            manager=self.__manager,
            target=target,
            kwargs=kwargs,
            stop_function=stop_function,
            stop_kwargs=stop_kwargs,
            task_type="process"
        )


    #
    # Event
    #
    def Event(self) -> Event:
        '''
        Create an event (using the multiprocessing manager)

        Args:
            None

        Returns:
            None

        Raises:
            Event
        '''
        log.debug(f"Creating event")
        return self.__manager.Event()


    #
    # Lock
    #
    def Lock(self) -> Lock:
        '''
        Create a Lock (using the multiprocessing manager)

        Args:
            None

        Returns:
            None

        Raises:
            Lock
        '''
        log.debug(f"Creating lock")
        return self.__manager.Lock()


    #
    # Barrier
    #
    def Barrier(
            self,
            parties: int = 2,
            action: Callable | None = None,
            timeout: float = 5.0
    ) -> Barrier:
        '''
        Create a Barrier (using the multiprocessing manager)

        Args:
            parties (int): Number of parties required to wait before the
                barrier is lifted
            action (Callable): Function to be executed (by one of the
                waiting parties) when the barrier is lifted
            timeout (float): Time to wait for the barrier to be lifted

        Returns:
            Barrier

        Raises:
            None
        '''
        log.debug(f"Creating barrier")
        return self.__manager.Barrier(
            parties=parties,
            action=action,
            timeout=timeout
        )


    #
    # Queue
    #
    def Queue(
            self,
            message_handler: Callable | None = None
    ) -> TaskQueue:
        '''
        Create a Queue (using the multiprocessing manager)

        Args:
            message_handler (Callable): Callable to process the received
                message. The message handler should accept 2 parameters:
                    The message
                    A queue to respond to (if None then no response)

        Returns:
            None

        Raises:
            Lock
        '''
        log.debug(f"Creating queue")
        return TaskQueue(
            queue=self.__manager.Queue(),
            stop_barrier=self.__manager.Barrier(
                parties=2, action=None, timeout=DEFAULT_BARRIER_TIMEOUT
            ),
            message_handler=message_handler
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
