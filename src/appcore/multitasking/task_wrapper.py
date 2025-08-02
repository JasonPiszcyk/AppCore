#!/usr/bin/env python3
'''
Task Wrapper - wrapper to run the task function, to allow us to capture
state and result information

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
import logging

# System Modules
import sys
import traceback
from threading import get_native_id
from multiprocessing import current_process


# Local app modules
from appcore.typing import TaskStatus
from appcore.appcore_base import AppCoreModuleBase

# Imports for python variable type hints
from typing import Any, Callable
from threading import Event as EventType
from logging import Handler as HandlerType
from appcore.typing import LoggingLevel
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
# Task Wrapper
#
###########################################################################
#
# task_wrapper
#
def task_wrapper(
        target: Callable | None = None,
        kwargs: KeywordDictType = {},
        info: dict = {},
        parent_pid: int = 0,
        start_event: EventType | None = None,
        stop_event: EventType | None = None,
        log_level: str = LoggingLevel.INFO.value,
        log_file: str = "",
        log_to_console: bool = False,
) -> None:
    '''
    Wrapper to run a task, and store result information

    Args:
        target (Callable): Function to run in the new thread/process
        kwargs (dict): Arguments to pass the target function
        info (dict): The SyncManager dict object to stored results and status
        parent_pid (int): The ID of the process that started this task
        start_event (Event): Event to wait on to allow sync with caller
            during task startup
        stop_event (Event): Event to wait on to allow sync with caller
            during task startup
        log_level (str): The log level to use when configuring logging
        log_file (str): Path of file to log to.  If not set, will not log
            to file
        log_to_console (bool): Write the logging out to the standard output 

    Returns:
        None

    Raises:
        None
    '''
    # Figure out if this is a new process or thread
    _task_type = "process"
    _task_id = current_process().pid

    if current_process().pid == parent_pid:
        # Running in a thread
        _task_type = "thread"
        _task_id = get_native_id()

    # Shouldn't write to the same file from multiple processes so add a 
    # suffix to the file name if this is a new process
    _log_file_name = ""
    if log_file:
        if _task_type == "thread":
            # Running as a thread
            _log_file_name = f"{log_file}"
        elif _task_type == "process":
            # Running as a process
            _name, _, _ext = log_file.rpartition(".")
            if not _name:
                _log_file_name = f"{_ext}-{current_process().pid}"
            else:
                _log_file_name = f"{_name}-{current_process().pid}.{_ext}"

    # Create a log handler
    _logger: logging.Logger = logging.getLogger("TaskWrapper")
    AppCoreModuleBase.logging_set_level(logger=_logger, log_level=log_level)

    # Remove existing handlers (eg stderr)
    for _handler in _logger.handlers.copy():
        _logger.removeHandler(_handler)

    # Log to a file if required
    if _log_file_name:
        _ = AppCoreModuleBase.logging_set_file(
            logger=_logger,
            filename=_log_file_name
        )

    if log_to_console:
        _ = AppCoreModuleBase.logging_to_console(logger=_logger)

    _logger.debug(
        f"Running Task as {_task_type}(id={_task_id}): {str(target)}"
    )

    # Got here - so let the caller know the task has started
    if start_event: start_event.set()

    _return_value: Any = None
    _exception_name: str | None = None
    _exception_desc: str | None = None
    _exception_stack: str | None = None

    if callable(target):

        # Run the target, capturing any exceptions and the return value
        try:
            _return_value = target(**kwargs)
            info["status"]= TaskStatus.COMPLETED.value
            _logger.debug(f"Task finished OK: {str(target)}")

        except Exception:
            info["status"]= TaskStatus.ERROR.value
            _exception_stack = traceback.format_exc()
            _logger.debug(f"Task FAILED: {str(target)}")
            _logger.debug(_exception_stack)

            _exc_info = sys.exc_info()
            if _exc_info:
                if _exc_info[0]:
                    _exception_name = str(_exc_info[0].__name__)
                if _exc_info[1]:
                    _exception_desc = str(_exc_info[1])

    # Set the return Value
    if "results" in info:
        info["results"]["return_value"] = _return_value
        info["results"]["exception_name"] = _exception_name
        info["results"]["exception_desc"] = _exception_desc
        info["results"]["exception_stack"] = _exception_stack

    # Set the vent to free other threads/processes
    if stop_event: stop_event.set()


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
