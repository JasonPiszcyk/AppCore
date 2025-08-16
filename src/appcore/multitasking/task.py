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
from multiprocessing import current_process, active_children
from threading import Thread
from threading import enumerate as enumerate_threads

# Local app modules
from appcore.appcore_base import AppCoreModuleBase
from appcore.typing import TaskStatus, TaskAction
from appcore.multitasking.task_results import TaskResults
from appcore.multitasking.task_wrapper import task_wrapper
from appcore.multitasking import exception

# Imports for python variable type hints
from typing import Any, Callable, Literal, get_args
from multiprocessing.context import SpawnContext, DefaultContext
from multiprocessing.process import BaseProcess
from multiprocessing.managers import DictProxy
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
TASK_JOIN_TIMEOUT: float = 5.0

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
        is_alive (bool): Indicates if the task is alive
        id (int): Id of the thread/process
        task_id (str): The unique Task ID
        status (str): The status of the task
        results (TaskResults): The results of the class
        task_action (str): String indicating the action Watchdog should take
            with the task
    '''
    #
    # __init__
    #
    def __init__(
            self,
            *args,
            context: ContextType | None = None,
            info_dict: DictProxy[Any, Any] | None = None,
            results_dict: DictProxy[Any, Any] | None = None,
            start_event: EventType | None = None,
            stop_event: EventType | None = None,
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
            context (ContextType): The context to run multiprocessing in
            info_dict (dict): SyncManger dict to store info on the task
            results_dict (dict): SyncManger dict to store the tasks results
            start_event (Event): A SyncManager event to signal start complete
            stop_event (Event): A SyncManager event to signal stop complete
            name (str): An identifier for the task
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
        assert isinstance(info_dict, DictProxy), \
            f"A SyncManager dict is required for task info"
        assert isinstance(results_dict, DictProxy), \
            f"A SyncManager dict is required for task results"
        assert start_event, "An event is required to manage task start"
        assert stop_event, "An event is required to manage task end"

        super().__init__(*args, **kwargs)

        task_type_options = get_args(TaskTypeType)
        assert task_type in task_type_options, \
                f"'{task_type}' is not in {task_type_options}"

        # Private Attributes
        self.__context: ContextType = context or get_context()

        self.__task_type = task_type
        self.__thread_id: int | None = None
        self.__process_id: int | None = None
        self.__task_id: str = str(uuid.uuid4())

        # Events to sync when the task is started/stopped
        self.__start_event = start_event
        self.__stop_event = stop_event

        # Create the shared information dictionary
        self.__info = info_dict
        self.__info["status"] = TaskStatus.NOT_STARTED.value
        self.__info["results"] = results_dict
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
        self.stop_kwargs: KeywordDictType = stop_kwargs or {}

        self.task_action = TaskAction.IGNORE.value


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # is_alive
    #
    @property
    def is_alive(self) -> bool:
        ''' Check if the process/thread is alive '''
        if self.__task_type == "thread":
            _thread = self.get_thread()
            return _thread.is_alive() if _thread else False

        elif self.__task_type == "process":
            _process = self.get_process()
            return _process.is_alive() if _process else False

        else:
            return False


    #
    # id
    #
    @property
    def id(self) -> int | None:
        ''' Return the thread/process ID '''
        if self.__task_type == "thread":
            return self.__thread_id

        elif self.__task_type == "process":
            return self.__process_id

        else:
            return None


    #
    # task_id
    #
    @property
    def task_id(self) -> str:
        ''' Return the unique Task ID '''
        return self.__task_id


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
    # Thread/Process functions
    #
    ###########################################################################
    #
    # get_thread
    #
    def get_thread(self) -> Thread | None:
        '''
        Find the thread associated with this task

        Args:
            None

        Returns:
            Thread: A thread instance if found or None

        Raises:
        '''
        for _thread in enumerate_threads():
            if _thread.name == self.__task_id:
                return _thread

        return None


    #
    # get_process
    #
    def get_process(self) -> BaseProcess | None:
        '''
        Find the process associated with this task

        Args:
            None

        Returns:
            Process: A process instance if found or None

        Raises:
        '''
        for _process in active_children():
            if _process.name == self.__task_id:
                return _process

        return None


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
        self.logger.debug(
            f"Context Start Method: {str(self.__context.get_start_method())}"
        )
        self.logger.debug(
            f"Start: Start task: {self.name} (Type={self.__task_type})"
        )

        if callable(self.target):
            self.__start_event.clear()
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
                _thread = Thread(
                    target=task_wrapper,
                    kwargs=_kwargs,
                    name=self.__task_id
                )
                _thread.start()
                self.__thread_id = _thread.native_id

            elif self.__task_type == "process":
                _process = self.__context.Process(
                    target=task_wrapper,
                    kwargs=_kwargs,
                    name=self.__task_id
                )
                _process.start()
                self.__process_id = _process.pid


            # When the process/thread is started, wait for the event
            self.__start_event.wait(timeout=TASK_START_TIMEOUT)

        self.logger.debug(
            f"Start: Task Started: {self.name} (Type={self.__task_type})"
        )


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
        self.logger.debug(
            f"Cleanup: Cleanup task: {self.name} (Type={self.__task_type})"
        )

        if self.__task_type == "thread":
            _thread = self.get_thread()
            if _thread:
                # Wait for the thread to finish
                _thread.join(TASK_JOIN_TIMEOUT)

                if _thread.is_alive():
                    raise exception.TaskIsRunningError(
                        f"Thread failed to stop (Task: {self.name})"
                    )

            self.__thread_id = None

        elif self.__task_type == "process":
            _process = self.get_process()
            if _process:
                # Wait for the process to finish
                _process.join(TASK_JOIN_TIMEOUT)

                if _process.is_alive():
                    raise exception.TaskIsRunningError(
                        f"Process failed to stop (Task: {self.name})"
                    )

                _process.close()

            self.__process_id = None

        self.logger.debug(
            f"Cleanup: Cleanup complete: {self.name} (Type={self.__task_type})"
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
        #
        # Run the stop function
        #
        self.logger.debug(
            f"Stop: Stopping task: {self.name} (Type={self.__task_type})"
        )

        if self.__task_type == "thread":
            _thread = self.get_thread()
            if not _thread:
                raise exception.TaskIsNotRunningError(
                    f"Cannot stop thread as no info found (Task: {self.name})"
                )

            if not _thread.is_alive():
                raise exception.TaskIsNotRunningError(
                    f"Cannot stop thread as not alive (Task: {self.name})"
                )

            # Run the callable to stop the thread
            if callable(self.stop_function):
                if self.__stop_event: self.__stop_event.clear()

                self.stop_function(**self.stop_kwargs)

                if self.__stop_event:
                    # When the process/thread is stopped, wait for the event
                    # (set in the task_wrapper)
                    self.logger.debug(
                        f"Stop: Waiting at event for Thread"
                    )
                    self.__stop_event.wait(timeout=TASK_STOP_TIMEOUT)


        elif self.__task_type == "process":
            _process = self.get_process()
            if not _process:
                raise exception.TaskIsNotRunningError(
                    f"Cannot stop process as no info found (Task: {self.name})"
                )

            if not _process.is_alive():
                raise exception.TaskIsNotRunningError(
                    f"Cannot stop process as not alive (Task: {self.name})"
                )

            # Run the callable to stop the process
            if callable(self.stop_function):
                if self.__stop_event: self.__stop_event.clear()

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
        self.logger.debug(
            f"Stop: Stop complete: {self.name} (Type={self.__task_type})"
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
