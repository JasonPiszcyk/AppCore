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
from multiprocessing import Process, get_context, get_start_method
from multiprocessing import current_process
from threading import Thread

# Local app modules
from appcore.appcore_base import AppCoreModuleBase
from appcore.typing import TaskStatus
from appcore.multitasking.task_results import TaskResults
from appcore.multitasking.task_wrapper import task_wrapper
from appcore.multitasking import exception

# Imports for python variable type hints
from typing import Any, Callable, Literal, get_args
from multiprocessing.context import SpawnContext, DefaultContext
from multiprocessing.context import SpawnProcess as SpawnProcessType
from multiprocessing.managers import SyncManager as SyncManagerType
from threading import Event as EventType
from appcore.typing import KeywordDictType


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
class Task(AppCoreModuleBase):
    '''
    Class to describe a task.

    Creates an instance of Task, which can be used to create
    processes or threads.

    Attributes:
        name (str): An identifier for the task
        target (Callable): Function to run in the new thread/process
        target_kwargs (dict): Arguments to pass to the target function
        stop_function (Callable): Function to run to stop the
            thread/process
        stop_kwargs (dict): Arguments to pass the stop function
        status (str): The status of the task
        results (TaskResults): The results of the class
    '''
    #
    # __init__
    #
    def __init__(
            self,
            *args,
            context: ContextType | None = None, 
            manager: SyncManagerType | None = None,
            name: str = "",
            target: Callable | None = None,
            target_kwargs: KeywordDictType = {},
            stop_function: Callable | None = None,
            stop_kwargs: KeywordDictType = {},
            task_type: TaskTypeType = "thread",
            **kwargs
     ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            name (str): An identifier for the task
            context (ContextType): The context to run multiprocessing in
            manager (SyncManager): An instance of the SyncManager class to
                provision resources for synching tasks
            target (Callable): Function to run in the new thread/process
            target_kwargs (dict): Arguments to pass to the target function
            stop_function (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass the stop function
            task_type (TaskTypeType): The type of task to be executed
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        super().__init__(*args, **kwargs)

        # If the context is not set, use the default
        task_type_options = get_args(TaskTypeType)
        assert task_type in task_type_options, \
                f"'{task_type}' is not in {task_type_options}"

        # Private Attributes
        self.__context: ContextType = context if context else get_context()
        if manager:
            self.__manager: SyncManagerType = manager
        else:
            self.__manager: SyncManagerType = self.__context.Manager()

        self.__task_type = task_type
        self.__thread: Thread | None = None
        self.__process: Process | SpawnProcessType | None = None

        # Events to sync when the task is started/stopped
        self.__start_event: EventType | None = None
        self.__stop_event: EventType | None = None

        # Create the shared information dictionary
        self.__info = self.__manager.dict()
        self.__info["status"] = TaskStatus.NOT_STARTED.value
        self.__info["results"] = self.__manager.dict()
        self.__info["results"]["return_value"] = None
        self.__info["results"]["exception_name"] = ""
        self.__info["results"]["exception_desc"] = ""
        self.__info["results"]["exception_stack"] = ""

        # Attributes
        self.name: str = name if name else str(uuid.uuid4())
        self.target: Callable | None = target
        if target_kwargs:
            self.target_kwargs: KeywordDictType = target_kwargs
        else:
            self.target_kwargs: KeywordDictType = {}

        self.stop_function: Callable | None = stop_function
        self.stop_kwargs: KeywordDictType = stop_kwargs if stop_kwargs else {}

        self._info = self.__manager.dict()


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # status
    #
    @property
    def status(self) -> str:
        ''' The status of the task '''
        if "status" in self.__info:
            return self.__info["status"]
        else:
            return TaskStatus.UNKNOWN.value


    #
    # results
    #
    @property
    def results(self) -> TaskResults:
        ''' The results of the task '''
        if not "results" in self.__info:
            return TaskResults(status=self.status)

        return TaskResults(
            status=self.status,
            return_value=self.__info["results"].get("return_value", None),
            exception_name=self.__info["results"].get("exception_name", ""),
            exception_desc=self.__info["results"].get("exception_desc", ""),
            exception_stack=self.__info["results"].get("exception_stack", ""),
        )


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
        self.logger.debug(
            f"Multiprocessing Start Method: {str(get_start_method())}"
        )

        # Create an event to sync when the task is started
        if not self.__start_event:
            self.__start_event = self.__manager.Event()

        # Create an event to sync when the task is stopped
        if not self.__stop_event:
            self.__stop_event = self.__manager.Event()

        if callable(self.target):
            self.__info["status"] = TaskStatus.RUNNING.value

            self.logger.debug(f"Start: Task Type = {self.__task_type}")

            # Wrap the target functions to gather information
            _kwargs: KeywordDictType = {
                "target": self.target,
                "kwargs": self.target_kwargs,
                "info": self.__info,
                "parent_pid": current_process().pid,
                "start_event": self.__start_event,
                "stop_event": self.__stop_event,
                "log_level": self._log_level,
                "log_file": self._log_file,
                "log_to_console": self._log_to_console,
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


            # When the process/thread is started, wait for the event
            self.__start_event.wait(timeout=TASK_START_TIMEOUT)


    #
    # cleanup
    #
    def cleanup(self) -> None:
        '''
        Cleanup a stopped task

        Args:
            None

        Returns:
            None

        Raises:
            TaskIsNotRunningError:
                When the task cannot be found
            TaskIsRunningError:
                When the task cannot be shutdown correctly
        '''
        if self.__task_type == "thread":
            if not  self.__thread:
                raise exception.TaskIsNotRunningError(
                    f"Cannot stop thread as no info found (Task: {self.name})"
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

            # Wait for the process to finish
            self.__process.join(TASK_JOIN_TIMEOUT)

            if self.__process.is_alive():
                raise exception.TaskIsRunningError(
                    f"Process failed to stop (Task: {self.name})"
                )

            self.__process.close()
            self.__process = None


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
        #
        # Run the stop function
        #
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

                if self.__stop_event:
                    # When the process/thread is stopped, wait for the event
                    # (set in the task_wrapper)
                    self.logger.debug(
                        f"Stop: Waiting at event for Thread"
                    )
                    self.__stop_event.wait(timeout=TASK_STOP_TIMEOUT)


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

                if self.__stop_event:
                    # When the process/thread is stopped, wait for the Event
                    # (set in the task_wrapper)
                    self.logger.debug(
                        f"Stop: Waiting at Event for Process"
                    )
                    self.__stop_event.wait(timeout=TASK_STOP_TIMEOUT)


        #
        # Run the cleanup
        #
        self.cleanup()


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
