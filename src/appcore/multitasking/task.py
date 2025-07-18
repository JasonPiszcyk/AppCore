#!/usr/bin/env python3
'''
Task Class

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
import uuid

# Local app modules
from src.appcore.constants import BasicDict

# Imports for python variable type hints
from typing import Callable
from threading import Thread
from multiprocessing import Process


###########################################################################
#
# Module variables/constants/types
#
###########################################################################
# When joining a thread/process, it may be terminating - wait for it to finish
JOIN_THREAD_TIMEOUT: float = 10.0
JOIN_PROCESS_TIMEOUT: float = 30.0


###########################################################################
#
# Task Class
#
###########################################################################
class Task():
    '''
    Class to describe a task

    Each instance of the class describes a task that the multitasking system
    can manage.

    Attributes:
        id (str): Task Identifier.  Will be set to a UUID if not provided.
        target (function): The Function to run in the new thread/process.
        kwargs (dict): Arguments to pass the target function when starting.
        restart: (bool): If true, attempt to restart the task on completion or
            failure.
        as_thread (bool): If true, run the task as thread.  If False, run the
            task as a process.
    '''

    #
    # __init__
    #
    def __init__(
            self, 
            id: str = "",
            target: Callable | None = None,
            kwargs: BasicDict = {},
            restart: bool = False,
            as_thread: bool = True
    ):
        '''
        Initializes the instance.

        Args:
            id (str): An identifier for the task
            target (function): Function to run in the new thread/process
            kwargs (dict): Arguments to pass the target function
            restart: (bool): Restart the task if it stops (eg fails)
            as_thread (bool): Start the task as a thread (or a process)
        
        Returns:
            Task: An instance of the Task class

        Raises:
            None
        '''
        # Private properties used for managing the task
        self.__thread: Thread | None = None
        self.__process: Process | None = None
        self.__as_thread: bool = as_thread

        # Attributes
        self.id: str = id if id else str(uuid.uuid4())
        self.target: Callable | None = target
        self.kwargs: BasicDict = kwargs
        self.restart: bool = restart


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # as_thread
    #
    @property
    def as_thread(self):
        '''
        Boolean property identifying if the task is run as a thread or process
        '''
        return self.__as_thread


    #
    # thread_id
    #
    @property
    def thread_id(self):
        '''
        The Thread ID property
        '''
        if self.__thread:
            return self.__thread.native_id


    #
    # process_id
    #
    @property
    def process_id(self):
        '''
        The Process ID property
        '''
        if self.__process:
            return self.__process.pid


    #
    # alive
    #
    @property
    def is_alive(self):
        '''
        Boolean property indicating if the task is alive
        '''
        if self.__as_thread:
            return self.__thread.is_alive() if self.__thread else False
        else:
            return self.__process.is_alive() if self.__process else False


    ###########################################################################
    #
    # Thread Operations
    #
    ###########################################################################
    #
    # __thread_cleanup
    #
    def __thread_cleanup(self) -> None:
        '''
        Cleanup the thread once it has completed

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__thread:
            # Try to join the thread - Has to be done to clean it up
            self.__thread.join(timeout=JOIN_THREAD_TIMEOUT)
            self.__thread: Thread | None = None


    #
    # __thread_start
    #
    def __thread_start(self) -> None:
        '''
        Start the thread

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if not self.__thread:
            if callable(self.target):
                # Start the thread
                self.__thread = Thread(
                    target=self.target,
                    kwargs=self.kwargs
                )
                self.__thread.start()


    #
    # __thread_stop
    #
    def __thread_stop(self) -> None:
        '''
        Stop the thread

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__thread:
            # Stop the thread
            pass


    ###########################################################################
    #
    # Process Operations
    #
    ###########################################################################
    #
    # __process_cleanup
    #
    def __process_cleanup(self) -> None:
        '''
        Cleanup the process once it has completed

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__process:
            # If the process is alive, try to kill it
            if self.__process.is_alive():
                self.__process.terminate()

            # Try to join the process - Has to be done to clean it up
            self.__process.join(timeout=JOIN_PROCESS_TIMEOUT)
            self.__process.close()
            self.__process: Process | None = None


    #
    # __process_start
    #
    def __process_start(self) -> None:
        '''
        Start the process

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if not self.__process:
            # Start the process
            if callable(self.target):
                # Start the thread
                self.__process = Process(
                    target=self.target,
                    kwargs=self.kwargs
                )
                self.__process.start()


    #
    # __process_stop
    #
    def __process_stop(self) -> None:
        '''
        Stop the process

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__process:
            # Stop the process
            pass


    ###########################################################################
    #
    # Task Operations
    #
    ###########################################################################
    #
    # cleanup
    #
    def cleanup(self) -> None:
        '''
        Cleanup the task once it has completed

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__as_thread:
            self.__thread_cleanup()
        else:
            self.__process_cleanup()


    #
    # start
    #
    def start(self) -> None:
        '''
        Start the task

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__as_thread:
            self.__thread_start()
        else:
            self.__process_start()



    #
    # stop
    #
    def stop(self) -> None:
        '''
        Stop the task

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__as_thread:
            self.__thread_stop()
        else:
            self.__process_stop()


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
