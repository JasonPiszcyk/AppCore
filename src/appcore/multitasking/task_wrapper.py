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

# System Modules
import sys
import traceback
from threading import BrokenBarrierError

# Local app modules
from appcore.typing import TaskStatus

# Imports for python variable type hints
from typing import Any, Callable
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
# Don't wait too long on start - Don't want to block for no reason
BARRIER_WAIT_TIMEOUT: float = 0.5


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
        start_barrier: Barrier | None = None,
        stop_barrier: Barrier | None = None
) -> None:
    '''
    Wrapper to run a task, and store result information

    Args:
        target (Callable): Function to run in the new thread/process
        kwargs (dict): Arguments to pass the target function
        info (dict): The SyncManager dict object to stored results and status
        start_barrier (Barrier): Barrier to wait on to allow sync with caller
            during task startup
        stop_barrier (Barrier): Barrier to wait on to allow sync with caller
            during task startup

    Returns:
        None

    Raises:
        None
    '''
    log.debug(f"Running Task: {str(target)}")

    # Got here - so let the caller know the task has started
    if start_barrier:
        try:
            start_barrier.wait(timeout=BARRIER_WAIT_TIMEOUT)
        except BrokenBarrierError:
            # Ignore this - The other process/thread should be waiting
            # (and this is to let the caller know we are done)
            pass


    _return_value: Any = None
    _exception_name: str | None = None
    _exception_desc: str | None = None
    _exception_stack: str | None = None

    if callable(target):

        # Run the target, capturing any exceptions and the return value
        try:
            _return_value = target(**kwargs)
            info["status"]= TaskStatus.COMPLETED.value
            log.debug(f"Task finished OK: {str(target)}")

        except Exception:
            info["status"]= TaskStatus.ERROR.value
            _exception_stack = traceback.format_exc()
            log.debug(f"Task FAILED: {str(target)}")
            log.debug(_exception_stack)

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

    if stop_barrier:
        try:
            stop_barrier.wait(timeout=BARRIER_WAIT_TIMEOUT)
        except BrokenBarrierError, EOFError:
            # Ignore this - The other process/thread should be waiting
            # (and this is to let the caller know we are done)
            pass


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
