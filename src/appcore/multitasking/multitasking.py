#!/usr/bin/env python3
'''
Multitasking module

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
import queue
from threading import Event
import signal

# Local app modules
from .task import Task
from .base import ignore_signals

# Imports for python variable type hints
from queue import Queue
from types import FrameType


###########################################################################
#
# Module variables/constants/types
#
###########################################################################
TaskDict = dict[str, Task]

# How often should the watchdog check the tasks
WATCHDOG_WAIT_TIME: float = 1.0

# A unique ID for the watchdog and queue tasks
TASK_ID_WATCHDOG: str = "ee232fe7-5cbc-43b7-aa7f-43445f75bc2b"
TASK_ID_QUEUE_LOOP: str = "103fa334-0afa-4404-b2fb-d6180a20cda0"


###########################################################################
#
# MultiTasking Class
#
###########################################################################
class MultiTasking():
    '''
    Class to handle multi-processing/multi-threading

    Attributes:
        id (str): Task Identifier.  Will be set to a UUID if not provided.
    '''

    #
    # __init__
    #
    def __init__(
            self,
            id: str = ""
    ):
        '''
        Initializes the instance.

        Args:
            id (str): An identifier for the task
        
        Returns:
            MultiTasking: An instance of the MultiTasking class.

        Raises:
            None
        '''
        # Private properties
        self.__queue_task_ops: Queue = queue.Queue()
        self.__task_dict: TaskDict = {}

        self.__watchdog_task: Task | None = None
        self.__watchdog_ending: Event = Event()
        self.__watchdog_ending.clear()

        self.__queue_loop_task: Task | None = None

        # Attributes
        self.id: str = id


    ###########################################################################
    #
    # Management Functions
    #
    ###########################################################################
    #
    # __watchdog
    #
    def __watchdog(self):
        '''
        Check on the status of the processes and threads

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Disable signal processing (Signals handled in queue_loop)
        ignore_signals()

        # Keep doing this until we receive the vent to exit
        while not self.__watchdog_ending.is_set():
            # Process the tasks to make sure they are OK
            for _task in self.__task_dict.values():
                # Ignore the watchdog task (This is running in it)
                if _task.id == TASK_ID_WATCHDOG: continue

                # Is the task alive?
                if not _task.is_alive:
                    # Clean up the dead task
                    _task.cleanup()

                    # Send a message to restart it if needed
                    if _task.restart: pass

            # Pause, waiting for the end event
            self.__watchdog_ending.wait(timeout=WATCHDOG_WAIT_TIME)


    #
    # __queue_loop
    #
    def __queue_loop(self):
        '''
        Process messsage sent to the queue

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Define the signal handlers
        def __signal_handler_exit(
                signum: int = 0,
                frame: FrameType | None = None
        ):
            self.stop()


        def __signal_handler_reload(
                signum: int = 0,
                frame: FrameType | None = None
        ):
            pass


        # Set up the signal handlers
        # SIGINT (CTRL-C) and SIGTERM (kill <pid> can be handled the same)
        signal.signal(signal.SIGTERM, __signal_handler_exit)
        signal.signal(signal.SIGINT, __signal_handler_exit)

        # SIGHUP (kill -1) - Usually means reload
        signal.signal(signal.SIGHUP, __signal_handler_reload)

        # Process the queue
        _queue_loop_ending = False
        while not _queue_loop_ending:
            _msg = self.__queue_task_ops.get(block=True)


    #
    # start
    #
    def start(self) -> None:
        '''
        Starts the multitasking management tasks

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Start the watchdog task
        self.__watchdog_task = Task(
                id=TASK_ID_WATCHDOG, target=self.__watchdog,
                restart=True
        )

        if self.__watchdog_task: self.__watchdog_task.start()

        # Create the task to listen to the queue
        self.__queue_loop_task = Task(
                id=TASK_ID_QUEUE_LOOP, target=self.__queue_loop,
                restart=True
        )

        if self.__queue_loop_task: self.__queue_loop_task.start()


    #
    # stop
    #
    def stop(self) -> None:
        '''
        Stops the multitasking management tasks

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Stop the watchdog task
        self.__watchdog_ending.set()

        # Stop the queue_loop task
        # self.__watchdog_ending.set()


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

