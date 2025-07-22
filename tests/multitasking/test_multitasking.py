#!/usr/bin/env python3
'''
PyTest - Test of multitasking functions

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
# System Imports
import pytest
import time
import appcore.multitasking as multitasking
import appcore.multitasking.exception as exception

#
# Globals
#

def debug(msg):
    with open("/tmp/jpp.txt", "at") as f:
        f.write(f"{msg}\n")



###########################################################################
#
# Functions to run in the tasks
#
###########################################################################
#
# Simple task to end when an event is set
#
def simple_event_target(test_event=None):
    assert test_event
    test_event.clear()
    test_event.wait()


def simple_event_stop(test_event=None):
    assert test_event
    test_event.set()


###########################################################################
#
# The tests...
#
###########################################################################
#
# Test on the system itself
#
class Test_Task_System():

    #
    # Test on the mutitasking system control
    #
    def test_start_stop(self):
        ''' Start and stop of the multitasking system '''
        # Start
        _mt = multitasking.start()

        # Ensure the parent process, queue loop and watchdog tasks have started
        assert _mt.parent_process_is_alive
        assert _mt.queue_loop_is_alive
        assert _mt.watchdog_is_alive

        # Stop
        multitasking.stop()

        # Make sure the queue loop and watchdog threads have stopped
        assert not _mt.parent_process_is_alive
        assert not _mt.queue_loop_is_alive
        assert not _mt.watchdog_is_alive


#
# Tasks as threads
#
class Test_Task_Threads():
    # Attributes for this set of tests
    id_prefix = "Test Task - Thread"
    as_thread = True

    def test_simple_task(self, mt):
        ''' Start/stop a task (as a thread) '''
        # Make sure there are no tasks
        assert len(mt.tasks) == 0
        assert len(mt.running_tasks) == 0

        # Add a task
        _kwargs = {
            "test_event": mt.manager.Event()
        }

        _task_id = mt.task_add(
            id = f"{self.__class__.id_prefix} - Simple",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
            restart = False,
            as_thread = self.__class__.as_thread
        )

        # Make sure the task is added but not running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 0

        # Start the task
        mt.task_start(_task_id)

        # Make sure the task is running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 1

        # Stop the task
        mt.task_stop(_task_id)

        # Make sure no tasks are running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 0

        # Delete the task
        mt.task_delete(_task_id)

        # Make sure there are no tasks
        assert len(mt.tasks) == 0
        assert len(mt.running_tasks) == 0

        # Ensure the task is gone
        with pytest.raises(exception.MultiTaskingTaskNotFoundError):
            mt.task_start(_task_id)


    def test_task_status_complete(self, mt):
        ''' 
        Run a task (as thread) successfully and check status at each stage
        '''
        # Add a task
        _kwargs = {
            "test_event": mt.manager.Event()
        }

        _task_id = mt.task_add(
            id = f"{self.__class__.id_prefix} - Status - Complete",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
            restart = False,
            as_thread = self.__class__.as_thread
        )

        # class TaskStatus(enum.Enum):
        #     NOT_STARTED     = "Not Started"
        #     RUNNING         = "Running"
        #     STOPPED         = "Stopped"
        #     ERROR           = "Error"
        #     COMPLETED       = "Completed"

        assert mt.task_status(_task_id) == "Not Started"

        # Start the task
        mt.task_start(_task_id)
        assert mt.task_status(_task_id) == "Running"

        # Stop the task
        mt.task_stop(_task_id)
        assert mt.task_status(_task_id) == "Completed"

       # Delete the task
        mt.task_delete(_task_id)


#
# Tasks as process
#
class Test_Task_Processes():
    # Attributes for this set of tests
    id_prefix = "Test Task - Process"
    as_thread = False

    def test_simple_task(self, mt):
        ''' Start/stop a task (as a process) '''
        # Make sure there are no tasks
        assert len(mt.tasks) == 0
        assert len(mt.running_tasks) == 0

        # Add a task
        _kwargs = {
            "test_event": mt.manager.Event()
        }

        # Add a task
        _task_id = mt.task_add(
            id = f"{self.__class__.id_prefix} - Simple",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
            restart = False,
            as_thread = self.__class__.as_thread
        )

        # Make sure the task is added but not running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 0

        # Start the task
        mt.task_start(_task_id)

        # Make sure the task is running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 1

        # Stop the task
        mt.task_stop(_task_id)

        # Make sure no tasks are running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 0

        # Delete the task
        mt.task_delete(_task_id)

        # Make sure there are no tasks
        assert len(mt.tasks) == 0
        assert len(mt.running_tasks) == 0

        # Ensure the task is gone
        with pytest.raises(exception.MultiTaskingTaskNotFoundError):
            mt.task_start(_task_id)


    def test_task_status_complete(self, mt):
        ''' 
        Run a task (as process) successfully and check status at each stage
        '''
        # Add a task
        _kwargs = {
            "test_event": mt.manager.Event()
        }

        _task_id = mt.task_add(
            id = f"{self.__class__.id_prefix} - Status - Complete",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
            restart = False,
            as_thread = self.__class__.as_thread
        )

        # class TaskStatus(enum.Enum):
        #     NOT_STARTED     = "Not Started"
        #     RUNNING         = "Running"
        #     STOPPED         = "Stopped"
        #     ERROR           = "Error"
        #     COMPLETED       = "Completed"

        assert mt.task_status(_task_id) == "Not Started"

        # Start the task
        mt.task_start(_task_id)
        assert mt.task_status(_task_id) == "Running"

        # Stop the task
        mt.task_stop(_task_id)
        assert mt.task_status(_task_id) == "Completed"

       # Delete the task
        mt.task_delete(_task_id)
