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

# Imports for python variable type hints
from typing import Callable
from multiprocessing.context import SpawnContext
from multiprocessing.managers import SyncManager
from appcore.typing import KeywordDictType


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
# Module
#
###########################################################################
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
        return Task(
            name=name,
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
        return Task(
            name=name,
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
        Create a process based Task

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        return self.__manager.Event()


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
