#!/usr/bin/env python3
'''
The parent process functions

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

def debug(msg):
    with open("/tmp/jpp.txt", "at") as f:
        f.write(f"{msg}\n")

###########################################################################
#
# Imports
#
###########################################################################
# Shared variables, constants, etc

# System Modules

# Local app modules
from appcore.multitasking.task import Task, TaskMgmtMessageFrame
from appcore.multitasking.shared import TaskAction

# Imports for python variable type hints
from appcore.multitasking.task import TaskDict


###########################################################################
#
# Module variables/constants/types
#
###########################################################################


###########################################################################
#
# Parent Process Function
#
###########################################################################
#
# entry_point
#
def entry_point(parent_process_task: Task | None = None):
    '''
    Entry point for the parent process task

    If we fork/spawn from this process, it copies across any threads
    that may have been started.

    This process should be started before any other threads or processes in
    the Task Management system

    Args:
        parent_process_task (Task): The task instance use to start this
            process
    
    Returns:
        None

    Raises:
        None
    '''
    assert parent_process_task, \
            "A task represent the parent process must be provided"

    # Create a task dict here to store the tasks we are managing
    # Will be a subset of the tasks in MultiTasking
    _task_dict: TaskDict = {}

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

                # Delete the task from the frame dict
                if frame.task.id in _task_dict:
                    del _task_dict[frame.task.id]

            elif frame.action == TaskAction.START:
                # Make sure we are starting a process
                if frame.task.as_thread: return

                # Add the task if not in the task dict
                # We need a local copy to track the process
                if not frame.task.id in _task_dict:
                    # We can use frame.task, as it is already a copy of the
                    # task stored in MultiTasking
                    _task_dict[frame.task.id] = frame.task

                if not _task_dict[frame.task.id].is_process_alive:
                    _task_dict[frame.task.id].start(barrier=frame.barrier)

            elif frame.action == TaskAction.STOP:
                # Make sure we are stopping a process
                if frame.task.as_thread: return

                if frame.task.id in _task_dict:
                    # Stop the task
                    if _task_dict[frame.task.id].is_process_alive:
                        _task_dict[frame.task.id].stop(barrier=frame.barrier)

                    # Delete the local copy of the task
                    # It will be re-added if started again
                    del _task_dict[frame.task.id]


    # Process the queue (will loop until stopped)
    parent_process_task.send_to_task_queue.listener(
        on_recv = _on_recv,
        on_invalid = _on_invalid,
        on_msg_ok = None,
        on_msg_error = None,
        on_msg_exit = None,
        on_msg_refresh = None,
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
