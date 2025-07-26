#!/usr/bin/env python3
'''
MultiTasking Task Definition Classes

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
from multiprocessing import get_context, get_start_method
from threading import Thread, BrokenBarrierError

# Local app modules
from appcore.multitasking.task_wrapper import task_wrapper
from appcore.multitasking import exception

# Imports for python variable type hints
from typing import Any, Callable, Literal, get_args
from multiprocessing import Process
from multiprocessing.context import SpawnContext, DefaultContext, SpawnProcess
from multiprocessing.managers import SyncManager
from threading import Barrier
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


##########################################################################
#
# Module Specific Items
#
###########################################################################
#
# Types
#
type TaskType = Task
type ContextType = SpawnContext | DefaultContext
TaskTypeType = Literal["thread", "process"]

#
# Constants
#
TASK_START_TIMEOUT: float = 5.0
TASK_STOP_TIMEOUT: float = 15.0
TASK_JOIN_TIMEOUT: float = 1.0

#
# Global Variables
#


###########################################################################
#
# Task Class Definition
#
###########################################################################
class Task():
    '''
    Class to describe a task.

    Creates an instance of Task, which can be used to create
    processes or threads.

    Attributes:
        None
    '''
    #
    # __init__
    #
    def __init__(
            self,
            context: ContextType | None = None, 
            manager: SyncManager | None = None,
            name: str = "",
            target: Callable | None = None,
            kwargs: KeywordDictType = {},
            stop_function: Callable | None = None,
            stop_kwargs: KeywordDictType = {},
            task_type: TaskTypeType = "thread"
    ):
        '''
        Initialises the instance.

        Args:
            name (str): An identifier for the task
            context (ContextType): The context to run multiprocessing in
            manager (SyncManager): An instance of the SyncManager class to
                provision resources for synching tasks
            target (Callable): Function to run in the new thread/process
            kwargs (dict): Arguments to pass to the target function
            stop_function (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass the stop function
            task_type (TaskTypeType): The type of task to be executed

        Returns:
            None

        Raises:
            None
        '''
        # If the context is not set, use the default
        task_type_options = get_args(TaskTypeType)
        assert task_type in task_type_options, \
                f"'{task_type}' is not in {task_type_options}"

        # Private Attributes
        self.__context: ContextType = context if context else get_context()
        if manager:
            self.__manager: SyncManager = manager
        else:
            self.__manager: SyncManager = self.__context.Manager()

        self.__task_type = task_type
        self.__thread: Thread | None = None
        self.__process: Process | SpawnProcess | None = None

        # Barriers to sync when the task is started/stopped
        self.__start_barrier: Barrier | None = None
        self.__stop_barrier: Barrier | None = None

        # Attributes
        self.name: str = name if name else str(uuid.uuid4())
        self.target: Callable | None = target
        self.kwargs: KeywordDictType = kwargs if kwargs else {}
        self.stop_function: Callable | None = stop_function
        self.stop_kwargs: KeywordDictType = stop_kwargs if stop_kwargs else {}


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################


    ###########################################################################
    #
    # Task Operations
    #
    ###########################################################################
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
            TaskIsNotRunningError:
                When startup of the task does not complete successfully
        '''
        log.debug(f"Multiprocessing Start Method: {str(get_start_method())}")

        # Create a barrier to sync when the task is started
        if not self.__start_barrier:
            self.__start_barrier = self.__manager.Barrier(
                    parties=2, action=None, timeout=TASK_START_TIMEOUT
                )

        # Create a barrier to sync when the task is stopped
        if not self.__stop_barrier:
            self.__stop_barrier = self.__manager.Barrier(
                    parties=2, action=None, timeout=TASK_STOP_TIMEOUT
                )

        if callable(self.target):
            # self.__task_info["status"][self.id]["status"] = \
            #     TaskStatus.RUNNING.value

            log.debug(f"Start: Task Type = {self.__task_type}")

            # Wrap the target functions to gather information
            _kwargs: KeywordDictType = {
                "target": self.target,
                "kwargs": self.kwargs,
                "start_barrier": self.__start_barrier,
                "stop_barrier": self.__stop_barrier
            }

            if self.__task_type == "thread":
                # Start the thread
                self.__thread = Thread(
                    target=task_wrapper,
                    kwargs=_kwargs,
                    name=self.name
                )
                self.__thread.start()

            elif self.__task_type == "process":
                self.__process = self.__context.Process(
                    target=task_wrapper,
                    kwargs=_kwargs,
                    name=self.name
                )
                self.__process.start()

                # _task_info["pid"] = self.__process.pid
                # time.sleep(PROCESS_STARTUP_DELAY)


            # When the process/thread is started, wait for the barrier
            try:
                self.__start_barrier.wait(timeout=TASK_START_TIMEOUT)
            except BrokenBarrierError:
                self.__start_barrier = None
                raise exception.TaskIsNotRunningError(
                    f"Timeout waiting for task to start (Name: {self.name})"
                )


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
            TaskIsNotRunningError:
                When the task cannot be stopped correctly
            TaskIsRunningError:
                When the task cannot be shutdown correctly
        '''
        if self.__task_type == "thread":
            if not  self.__thread:
                raise exception.TaskIsNotRunningError(
                    f"Cannot stop thread as no info found (Task: {self.name})"
                )

            if not self.__thread.is_alive():
                raise exception.TaskIsNotRunningError(
                    f"Cannot stop thread as not alive (Task: {self.name})"
                )

            # Run the callable to stop the thread
            if callable(self.stop_function):
                self.stop_function(**self.stop_kwargs)

                if self.__stop_barrier:
                    # When the process/thread is stopped, wait for the barrier
                    # (set in the task_wrapper)
                    try:
                        log.debug(f"Stop: Waiting at Barrier for Thread")
                        self.__stop_barrier.wait(timeout=TASK_STOP_TIMEOUT)
                    except BrokenBarrierError:
                        self.__stop_barrier = None
                        raise exception.TaskIsNotRunningError(
                            f"Timeout waiting for task to start (Name: {self.name})"
                        )


            # Wait for the thread to finish
            self.__thread.join(TASK_JOIN_TIMEOUT)

            if self.__thread.is_alive():
                raise exception.TaskIsRunningError(
                    f"Thread failed to stop (Task: {self.name})"
                )

            self.__thread = None

        elif self.__task_type == "process":
            if not  self.__process:
                raise exception.TaskIsNotRunningError(
                    f"Cannot stop process as no info found (Task: {self.name})"
                )

            if not self.__process.is_alive():
                raise exception.TaskIsNotRunningError(
                    f"Cannot stop process as not alive (Task: {self.name})"
                )

            # Run the callable to stop the process
            if callable(self.stop_function):
                self.stop_function(**self.stop_kwargs)

                if self.__stop_barrier:
                    # When the process/thread is stopped, wait for the barrier
                    # (set in the task_wrapper)
                    try:
                        log.debug(f"Stop: Waiting at Barrier for Process")
                        self.__stop_barrier.wait(timeout=TASK_STOP_TIMEOUT)
                    except BrokenBarrierError:
                        self.__stop_barrier = None
                        raise exception.TaskIsNotRunningError(
                            f"Timeout waiting for task to start (Name: {self.name})"
                        )

            # Wait for the process to finish
            self.__process.join(TASK_JOIN_TIMEOUT)

            if self.__process.is_alive():
                raise exception.TaskIsRunningError(
                    f"Process failed to stop (Task: {self.name})"
                )

            self.__process.close()
            self.__process = None


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
