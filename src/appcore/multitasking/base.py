#!/usr/bin/env python3
'''
Common functions

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
from appcore.multitasking.shared import AppGlobal

# System Modules
import sys
import signal
from multiprocessing import Manager

# Local app modules
from appcore.multitasking import parent_process
from appcore.multitasking.task import Task
from appcore.multitasking.multitasking import MultiTasking as MultiTaskingClass
from appcore.multitasking.shared import TASK_ID_PARENT_PROCESS
from appcore.multitasking.shared import TASK_ID_QUEUE_LOOP
from appcore.multitasking.shared import TASK_ID_WATCHDOG
from appcore.multitasking.exception import MultiTaskingNotFoundError

# Imports for python variable type hints
from types import FrameType


###########################################################################
#
# Module variables/constants/types
#
###########################################################################


###########################################################################
#
# Multiprocessing Management Functions
#
###########################################################################
#
# start
#
def start() -> MultiTaskingClass:
    '''
    Start the MultiTasking management tasks

    Args:
        None
    
    Returns:
        None

    Raises:
        None
    '''
    # Identify the global variables
    global MultiTasking

    # Create the MultiProcessing Manager
    # Stored in a list so all other modules see the change
    _manager = Manager()
    if not AppGlobal.get("MultiProcessingManager", None):
         AppGlobal['MultiProcessingManager'] = _manager

    # Create the proxy objects in the TaskInfo Dict
    AppGlobal["TaskInfo"]["status"] = _manager.dict()
    AppGlobal["TaskInfo"]["results"] = _manager.dict()

    # Start the parent process early to keep it fairly clean
    _parent_process_task = Task(
            id=TASK_ID_PARENT_PROCESS,
            target=parent_process.entry_point,
            as_thread=False,
            restart=True
    )

    # Pass the task over as a parameter (have to do this after the instance
    # is created above)
    _parent_process_task.kwargs = {
        "parent_process_task": _parent_process_task
    }

    _parent_process_task.start()

    # Define the signal handlers
    def __signal_handler_exit(
            signum: int = 0,
            frame: FrameType | None = None
    ):
        stop()


    def __signal_handler_reload(
            signum: int = 0,
            frame: FrameType | None = None
    ):
        refresh()


    # Seems to fail if run via PyTest
    if not "pytest" in sys.modules:
        # Set up the signal handlers
        # SIGINT (CTRL-C) and SIGTERM (kill <pid> can be handled the same)
        signal.signal(signal.SIGTERM, __signal_handler_exit)
        signal.signal(signal.SIGINT, __signal_handler_exit)

        # SIGHUP (kill -1) - Usually means reload
        signal.signal(signal.SIGHUP, __signal_handler_reload)


    # Create the Multitasking Instance
    MultiTasking = MultiTaskingClass(
        parent_process_task = _parent_process_task,
    )
 
    # Create the task to listen to the queue
    MultiTasking.queue_loop_task = Task(
            id=TASK_ID_QUEUE_LOOP,
            target=MultiTasking.queue_loop,
            restart=True
    )

    MultiTasking.queue_loop_task.start()

    # Start the watchdog task
    MultiTasking.watchdog_task = Task(
            id=TASK_ID_WATCHDOG,
            target=MultiTasking.watchdog,
            restart=True
    )

    MultiTasking.watchdog_task.start()

    # Return the class
    return MultiTasking


#
# stop
#
def stop() -> None:
    '''
    Stop the MultiTasking management tasks

    Args:
        None
    
    Returns:
        None

    Raises:
        MultiTaskingNotFoundError:
            When the MultiTask Instance in not available
    '''
    # Identify the global variables
    global MultiTasking

    # Not much we can do with out the MultiTasking instance
    if not MultiTasking:
        raise MultiTaskingNotFoundError("Unable to find MultiTasking Instance")

    # # Stop all tasks
    MultiTasking.task_stop_all()

    # Stop the watchdog task
    if MultiTasking.watchdog_task:
        MultiTasking.watchdog_task.stop_event.set()
        MultiTasking.watchdog_task.cleanup()
        MultiTasking.watchdog_task = None

    # Stop the queue loop task
    if MultiTasking.queue_loop_task:
        _listener_queue = MultiTasking.queue_loop_task.send_to_task_queue
        _listener_queue.listener_stop()
        MultiTasking.queue_loop_task.cleanup()
        MultiTasking.queue_loop_task = None

    # Stop the parent process task
    if MultiTasking.parent_process_task:
        _listener_queue = MultiTasking.parent_process_task.send_to_task_queue
        _listener_queue.listener_stop(remote=True)
        MultiTasking.parent_process_task.cleanup()
        MultiTasking.parent_process_task = None


#
# refresh
#
def refresh() -> None:
    '''
    Send a refresh message to the tasking system

    Args:
        None
    
    Returns:
        None

    Raises:
        MultiTaskingNotFoundError:
            When the MultiTask Instance in not available
    '''
    # Identify the global variables
    global MultiTasking

    # Not much we can do with out the MultiTasking instance
    if not MultiTasking:
        raise MultiTaskingNotFoundError("Unable to find MultiTasking Instance")

    # Send the message
    if MultiTasking.queue_loop_task:
        MultiTasking.queue_loop_task.send_to_task_queue.send_refresh()


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
