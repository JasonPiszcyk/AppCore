#!/usr/bin/env python3
'''
MultiTasking Task Defintion Class

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
# from appcore.multitasking import TaskManager

# System Modules
import sys
import traceback
import uuid
from multiprocessing import Process, get_start_method, current_process
from threading import Thread

# Local app modules

# Imports for python variable type hints
from typing import Any, Callable, Literal, get_args
from appcore.shared import KeywordDict


def debug(msg):
    with open("/tmp/jpp.txt", "at") as f:
        f.write(f"{msg}\n")


###########################################################################
#
# Module Specific Items
#
###########################################################################
#
# Types
#
TaskType = Literal["thread", "process"]

#
# Constants
#


#
# Global Variables
#


###########################################################################
#
# Task Wrapper
#
###########################################################################
#
# run_task
#
def run_task(
        target: Callable | None = None,
        kwargs: KeywordDict = {},
) -> None:
    '''
    Wrapper to run a task, and store result information

    Args:
        target (Callable): Function to run in the new thread/process
        kwargs (dict): Arguments to pass the target function

    Returns:
        None

    Raises:
        None
    '''
    debug(f"Running Task: {str(target)}")
    if callable(target):
        _return_value: Any = None
        _exception_name: str | None = None
        _exception_desc: str | None = None
        _exception_stack: str | None = None

        # Run the target, capturing any exceptions and the return value
        try:
            _return_value = target(**kwargs)
            # self.__task_info["status"][self.id]["status"] = \
            #     TaskStatus.COMPLETED.value
            # self.__task_info["status"][self.id]["is_alive"] = False
            debug(f"Task finished OK: {str(target)}")

        except Exception:
            # self.__task_info["status"][self.id]["status"] = \
            #     TaskStatus.ERROR.value
            # self.__task_info["status"][self.id]["is_alive"] = False
            _exception_stack = traceback.format_exc()
            debug(f"Task FAILED: {str(target)}")
            debug(_exception_stack)

            _exc_info = sys.exc_info()
            if _exc_info:
                if _exc_info[0]:
                    _exception_name = str(_exc_info[0].__name__)
                if _exc_info[1]:
                    _exception_desc = str(_exc_info[1])

        # Set the return Value
        # _results = self.__task_info["results"][self.id]
        # _results["return_value"] = _return_value
        # _results["exception_name"] = _exception_name
        # _results["exception_desc"] = _exception_desc
        # _results["exception_stack"] = _exception_stack


###########################################################################
#
# TaskDefinition Class Definition
#
###########################################################################
class TaskDefinition():
    '''
    Class to describe a task definition.

    Creates an instance of TaskDefinition, which can be used to create
    processes or threads.

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            name: str = "",
            target: Callable | None = None,
            kwargs: KeywordDict = {},
            stop_function: Callable | None = None,
            stop_kwargs: KeywordDict = {},
            task_type: TaskType = "thread"
    ):
        '''
        Initialises the instance.

        Args:
            name (str): An identifier for the task
            target (Callable): Function to run in the new thread/process
            kwargs (dict): Arguments to pass to the target function
            stop_function (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass the stop function

        Returns:
            None

        Raises:
            None
        '''
        task_type_options = get_args(TaskType)
        assert task_type in task_type_options, \
                f"'{task_type}' is not in {task_type_options}"

        # Private Attributes
        self.__task_type = task_type
        self.__thread: Thread | None = None
        self.__process: Process | None = None

        # Attributes
        self.name: str = name if name else str(uuid.uuid4())
        self.target: Callable | None = target
        self.kwargs: KeywordDict = kwargs if kwargs else {}
        self.stop_function: Callable | None = stop_function
        self.stop_kwargs: KeywordDict = stop_kwargs if stop_kwargs else {}


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
            None
        '''
        debug(f"Multiprocessing Start Method: {str(get_start_method())}")
        # Wrap the target function to gather information
        _kwargs: KeywordDict = {
            "target": self.target,
            "kwargs": self.kwargs
        }

        if callable(self.target):
            # self.__task_info["status"][self.id]["status"] = \
            #     TaskStatus.RUNNING.value

            debug(f"Start: Task Type = {self.__task_type}")
            if self.__task_type == "thread":
                # Start the thread
                self.__thread = Thread(
                    target=run_task,
                    kwargs=_kwargs,
                    name=self.name
                )
                self.__thread.start()

            elif self.__task_type == "process":
                debug(f"Creating process ({self.__task_type})")
                self.__process = Process(
                    target=run_task,
                    kwargs=_kwargs,
                    name=self.name
                )
                debug(f"Starting process ({self.__task_type})")
                self.__process.start()
                debug(f"Current Process Name (in start): {current_process().name}")

                # _task_info["pid"] = self.__process.pid
                # time.sleep(PROCESS_STARTUP_DELAY)


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
        if self.__task_type == "thread":
            if self.__thread and self.__thread.is_alive():
                # Run the callable to stop the thread
                if callable(self.stop_function):
                    self.stop_function(**self.stop_kwargs)

        elif self.__task_type == "process":
            if self.__process and self.__process.is_alive():
                # Run the callable to stop the process
                if callable(self.stop_function):
                    self.stop_function(**self.stop_kwargs)


###########################################################################
#
# ThreadTaskDefinition Class Definition
#
###########################################################################
class ThreadTaskDefinition(TaskDefinition):
    '''
    Sub class of TaskDefinition.

    Creates a TaskDefinition instance with a task type of "thread"

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        # if 'task_type' is included, raise an error
        if "task_type" in kwargs.keys():
            raise TypeError("got an unexpected keyword argument 'task_type")

        super().__init__(*args, task_type="thread", **kwargs)
        

###########################################################################
#
# ProcessTaskDefinition Class Definition
#
###########################################################################
class ProcessTaskDefinition(TaskDefinition):
    '''
    Sub class of TaskDefinition.

    Creates a TaskDefinition instance with a task type of "process"

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        # if 'task_type' is included, raise an error
        if "task_type" in kwargs.keys():
            raise TypeError("got an unexpected keyword argument 'task_type")

        super().__init__(*args, task_type="process", **kwargs)
        

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
