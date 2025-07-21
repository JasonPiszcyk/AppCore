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
###########################################################################
#
# Imports
#
###########################################################################
# Shared variables, constants, etc
from appcore.multitasking.shared import AppGlobal

# System Modules
from threading import BrokenBarrierError

# Local app modules
from appcore.multitasking.task import Task
from appcore.multitasking.multitasking import TaskAction, TaskMgmtMessageFrame
import appcore.multitasking.exception as exception

# Imports for python variable type hints


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
    assert parent_process_task

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

            elif frame.action == TaskAction.START:
                # Make sure we are starting a process
                if not frame.task.as_thread:
                    if not frame.task.is_alive:
                        frame.task.start()
                        _id = frame.task.id
                        AppGlobal["TaskInfo"]["status"][_id]["pid"] = \
                            frame.task.process_id


            elif frame.action == TaskAction.STOP:
                # Stop the task
                if not frame.task.as_thread:
                    if frame.task.is_alive: frame.task.stop()

            elif frame.action == TaskAction.STATUS:
                # Update the volatile status info for a process
                if not frame.task.as_thread:
                    _id = frame.task.id
                    AppGlobal["TaskInfo"]["status"][_id]["is_alive"] = \
                        frame.task.is_alive

                    try:
                        frame.task.status_barrier.wait()
                    except BrokenBarrierError:
                        raise exception.MultiTaskingStatusUpdateError (
                            "Timed out waiting while updating status"
                        )


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
