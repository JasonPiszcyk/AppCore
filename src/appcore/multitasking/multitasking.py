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
import sys
from threading import Lock, Event
import signal
import enum

# Local app modules
from .task import Task
from .base import ignore_signals
from .queue import TaskQueue, MessageFrameBase
from .exceptions import MultiTaskingNotFound
from src.appcore.constants import BasicDict

# Imports for python variable type hints
from typing import Callable
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


# The message types
class TaskAction(enum.Enum):
    START           = "__task_start__"
    STOP            = "__task_stop__"
    ADD             = "__task_add__"
    DELETE          = "__task_delete__"


###########################################################################
#
# MessageFrames - Different Frame types based on MessageFrameBase
#
###########################################################################
#
# Queue Message Frames derived from the MessageFrameBase class
#
class TaskMgmtMessageFrame(MessageFrameBase):
    ''' Message Frame for task mamagement'''
    def __init__(
            self,
            action: TaskAction = TaskAction.ADD,
            task: Task | None = None
        ):
        super().__init__()

        # Validate the args
        if action in TaskAction:
            self.action = action
        else:
            self.action = TaskAction.ADD

        self.task = task


###########################################################################
#
# MultiTasking Class
#
###########################################################################
class MultiTasking():
    '''
    Class to handle multi-processing/multi-threading

    Attributes:
        tasks (list) [Readonly]: A list of the current task IDs
        running_tasks (list) [Readonly]: A list of the current running task IDs
        watchdog_is_alive (bool) [Readonly]: Indicator if the watchdog thread 
            is alive
        queue_loop_is_alive (bool) [Readonly]: Indicator if the queue loop
            thread is alive
    '''

    #
    # __init__
    #
    def __init__(self):
        '''
        Initializes the instance.

        Args:
            id (str): An identifier for the task
        
        Returns:
            None

        Raises:
            None
        '''
        # Private properties
        self.__queue_task_ops: TaskQueue = TaskQueue()
        self.__task_dict: TaskDict = {}
        self.__task_dict_lock = Lock()

        self.__watchdog_task: Task | None = None
        self.__watchdog_ending: Event = Event()
        self.__watchdog_ending.clear()

        self.__queue_loop_task: Task | None = None

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # tasks
    #
    @property
    def tasks(self) -> list:
        ''' List of current task ID's '''
        _task_list: list = []

        for _task in self.__task_dict.values():
            _task_list.append(_task.id)

        return _task_list


    #
    # tasks
    #
    @property
    def running_tasks(self) -> list:
        ''' List of running task ID's '''
        _task_list: list = []

        for _task in self.__task_dict.values():
            if _task.is_alive: _task_list.append(_task.id)

        return _task_list


    #
    # watchdog_is_alive
    #
    @property
    def watchdog_is_alive(self) -> bool:
        ''' Check if the watchdog thread is alive '''
        if self.__watchdog_task:
            return self.__watchdog_task.is_alive
        else:
            return False


    #
    # queue_loop_is_alive
    #
    @property
    def queue_loop_is_alive(self) -> bool:
        ''' Check if the queue loop thread is alive '''
        if self.__queue_loop_task:
            return self.__queue_loop_task.is_alive
        else:
            return False


    ###########################################################################
    #
    # Management Functions for the Multitasking System
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
                    if _task.runnable:
                        # Clean up the dead task
                        _task.cleanup()

                        # Send a message to restart it if needed
                        if _task.restart:
                            if self.__queue_task_ops:
                                self.__queue_task_ops.send(
                                    frame=TaskMgmtMessageFrame(
                                        action=TaskAction.START,
                                        task=_task
                                    )
                                )

                else:
                    if not _task.runnable:
                        # Task is running, but marked not runnable.  Stop it
                        if self.__queue_task_ops:
                            self.__queue_task_ops.send(
                                frame=TaskMgmtMessageFrame(
                                    action=TaskAction.STOP,
                                    task=_task
                                )
                            )

            # Pause, waiting for the 'end watchdog' event
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
            self.refresh()

        # Seems to fail if run via PyTest
        if not "pytest" in sys.modules:
            # Set up the signal handlers
            # SIGINT (CTRL-C) and SIGTERM (kill <pid> can be handled the same)
            signal.signal(signal.SIGTERM, __signal_handler_exit)
            signal.signal(signal.SIGINT, __signal_handler_exit)

            # SIGHUP (kill -1) - Usually means reload
            signal.signal(signal.SIGHUP, __signal_handler_reload)

        #
        # Define the call back functions for the processing loop
        #
        def _on_invalid(frame):
            # Invalid packet or unknown message type - Ignore it
            pass


        def _on_recv(frame):
            # Should be message frames of type: TaskMgmtMessageFrame
            if not isinstance(frame, TaskMgmtMessageFrame):
                # We are going to ignore this message - Invalid frame
                # May want to log this at some stage?
                pass

            else:
                # Make sure there is a task to deal with
                if not frame.task or not isinstance(frame.task, Task):
                    return

                if frame.action == TaskAction.ADD:
                    # Add the task if not in the task dict
                    if not frame.task.id in self.__task_dict:
                        self.__task_dict_lock.acquire()
                        self.__task_dict[frame.task.id] = frame.task
                        self.__task_dict_lock.release()

                elif frame.action == TaskAction.DELETE:
                    # Delete the task from the frame dict
                    if frame.task.id in self.__task_dict:
                        self.__task_dict_lock.acquire()
                        del self.__task_dict[frame.task.id]
                        self.__task_dict_lock.release()

                elif frame.action == TaskAction.START:
                    # Start the task
                    if frame.task.id in self.__task_dict:
                        frame.task.runnable = True
                        frame.task.start()

                elif frame.action == TaskAction.STOP:
                    # Stop the task if it is in the task dict
                    if frame.task.id in self.__task_dict:
                        frame.task.runnable = False
                        frame.task.stop()


        # Process the queue (will loop until stopped)
        self.__queue_task_ops.listener(
            on_recv = _on_recv,
            on_invalid = _on_invalid,
            on_msg_ok = None,
            on_msg_error = None,
            on_msg_exit = None,
            on_msg_refresh = None,
        )


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

        self.__watchdog_task.start()

        # Create the task to listen to the queue
        self.__queue_loop_task = Task(
                id=TASK_ID_QUEUE_LOOP, target=self.__queue_loop,
                restart=True
        )

        self.__queue_loop_task.start()


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
        # Stop all tasks
        self.task_stop_all()

        # Stop the watchdog task
        if self.__watchdog_task:
            self.__watchdog_ending.set()
            self.__watchdog_task.cleanup()
            self.__watchdog_task = None

        # Stop the queue_loop task
        if self.__queue_task_ops:
            self.__queue_task_ops.listener_stop()

        # Cleanup the queue loop task
        if self.__queue_loop_task:
            self.__queue_loop_task.cleanup()
            self.__queue_loop_task = None


    #
    # refresh
    #
    def refresh(self) -> None:
        '''
        Send a refresh message to the task queuing system

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Send the message
        self.__queue_task_ops.send_refresh()


    ###########################################################################
    #
    # Management Functions for tasks
    #
    ###########################################################################
    #
    # task_add
    #
    def task_add(
            self,
            id: str = "",
            target: Callable | None = None,
            stop: Callable | None = None,
            kwargs: BasicDict = {},
            restart: bool = False,
            as_thread: bool = True
    ) -> str:
        '''
        Adds a task to the system

        Args:
            id (str): An identifier for the task
            target (function): Function to run in the new thread/process
            stop (Callable): Function to run to stop the thread/process
            kwargs (dict): Arguments to pass the target function
            restart: (bool): Restart the task if it stops (eg fails)
            as_thread (bool): Start the task as a thread (or a process)
        
        Returns:
            string: The ID of the task that has been created

        Raises:
            None
        '''
        _task = Task(
            id=id,
            target=target,
            stop=stop,
            kwargs=kwargs,
            restart=restart,
            as_thread=as_thread
        )

        # Add the task if not in the task dict
        if not _task.id in self.__task_dict:
            self.__task_dict_lock.acquire()
            self.__task_dict[_task.id] = _task
            self.__task_dict_lock.release()

        return _task.id


    #
    # task_delete
    #
    def task_delete(
            self,
            id: str = "",
    ) -> None:
        '''
        Deletes a task from the system

        Args:
            id (str): An identifier for the task
        
        Returns:
            None

        Raises:
            MultiTaskingNotFound:
                When the task ID cannot be found in the task dict
        '''
        # Check if the task is in the task dict
        if not id in self.__task_dict:
            raise MultiTaskingNotFound

        self.__task_dict_lock.acquire()
        del self.__task_dict[id]
        self.__task_dict_lock.release()


    #
    # task_start
    #
    def task_start(
            self,
            id: str = "",
    ) -> None:
        '''
        Starts a task

        Args:
            id (str): An identifier for the task
        
        Returns:
            None

        Raises:
            MultiTaskingNotFound:
                When the task ID cannot be found in the task dict
        '''
        # Check if the task is in the task dict
        if not id in self.__task_dict:
            raise MultiTaskingNotFound

        self.__queue_task_ops.send(
            frame=TaskMgmtMessageFrame( 
                action=TaskAction.START,
                task=self.__task_dict[id]
            )
        )


    #
    # task_stop
    #
    def task_stop(
            self,
            id: str = "",
    ) -> None:
        '''
        Stops a task

        Args:
            id (str): An identifier for the task
        
        Returns:
            None

        Raises:
            MultiTaskingNotFound:
                When the task ID cannot be found in the task dict
        '''
        # Check if the task is in the task dict
        if not id in self.__task_dict:
            raise MultiTaskingNotFound

        self.__queue_task_ops.send(
            frame=TaskMgmtMessageFrame( 
                action=TaskAction.STOP,
                task=self.__task_dict[id]
            )
        )


    #
    # task_stop_all
    #
    def task_stop_all(self) -> None:
        '''
        Stops all tasks

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        for _task in self.__task_dict.values():
            self.task_stop(_task.id)


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

