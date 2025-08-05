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
from multiprocessing import current_process
from appcore.typing import TaskStatus

#
# Globals
#
EXCEPTION = RuntimeError
EXCEPTION_DESC = "The exception description"

SHORT_LIVED_RETURN = "short lived task return string"


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


#
# Task to end by itself
#
def short_lived_event_target():
    return SHORT_LIVED_RETURN


#
# Task to generate an error
#
def error_event_target():
    raise EXCEPTION(EXCEPTION_DESC)


###########################################################################
#
# The tests...
#
###########################################################################
#
# Tasks as threads
#
class Test_Task_Threads():
    # Attributes for this set of tests
    id_prefix = "Test Task - Thread"
    task_type = "thread"

    def test_task_simple(self, manager):
        ''' Start/stop a task (as a thread) '''

        # Add a task
        _kwargs = {
            "test_event": manager.Event()
        }

        _task = manager.Thread(
            name = f"{self.__class__.id_prefix} - Simple",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Stop the task
        _task.stop()


    def test_task_status_complete(self, manager):
        ''' 
        Run a task (as thread) successfully and check status at each stage
        '''
        # Add a task
        _kwargs = {
            "test_event": manager.Event()
        }

        _task = manager.Thread(
            name = f"{self.__class__.id_prefix} - Status - Complete",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Start the task
        _task.start()
        assert _task.status == TaskStatus.RUNNING.value

        # Stop the task
        _task.stop()
        assert _task.status == TaskStatus.COMPLETED.value


    def test_task_status_error(self, manager):
        ''' 
        Run a task (as thread) with an error and check status at each stage
        '''
        # Add a task
        _kwargs = {
            "test_event": manager.Event()
        }

        _task = manager.Thread(
            name = f"{self.__class__.id_prefix} - Status - Error",
            target = error_event_target,
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Start the task
        _task.start()

        # Give the task a chance to run/error
        time.sleep(0.2)
        assert _task.status == TaskStatus.ERROR.value

        # Check the results
        _results = _task.results
        assert _results.status == TaskStatus.ERROR.value
        assert not _results.return_value
        assert _results.exception_name == str(EXCEPTION.__name__)
        assert _results.exception_desc == EXCEPTION_DESC
        assert str(_results.exception_stack).find(
                f"{EXCEPTION.__name__}: {EXCEPTION_DESC}") >= 0


    def test_task_short_lived(self, manager):
        ''' 
        Run a task (as thread) that ends itself and returns a value
        '''
        # Add a task
        _task = manager.Thread(
            name = f"{self.__class__.id_prefix} - Short Lived",
            target = short_lived_event_target,
        )

        # Start the task
        _task.start()

        # What for the task to complete
        while _task.status == TaskStatus.RUNNING.value:
            time.sleep(0.1)
        
        # Clean the task (to clean it up / no zombie)
        _task.cleanup()

        # Check the results
        _results = _task.results
        assert _results.status == TaskStatus.COMPLETED.value
        assert _results.return_value == SHORT_LIVED_RETURN


#
# Tasks as Processes
#
class Test_Task_Process():
    # Attributes for this set of tests
    id_prefix = "Test Task - Process"
    task_type = "process"

    def test_task_simple(self, manager):
        ''' Start/stop a task (as a process) '''
        # Add a task
        _kwargs = {
            "test_event": manager.Event()
        }

        _task = manager.Process(
            name = f"{self.__class__.id_prefix} - Simple",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()

         # Start the task
        _task.stop()


    def test_task_status_complete(self, manager):
        ''' 
        Run a task (as process) successfully and check status at each stage
        '''
        # Add a task
        _kwargs = {
            "test_event": manager.Event()
        }

        _task = manager.Process(
            name = f"{self.__class__.id_prefix} - Status - Complete",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Start the task
        _task.start()
        assert _task.status == TaskStatus.RUNNING.value

        # Stop the task
        _task.stop()
        assert _task.status == TaskStatus.COMPLETED.value


    def test_task_status_error(self, manager):
        ''' 
        Run a task (as process) with an error and check status at each stage
        '''
        # Add a task
        _kwargs = {
            "test_event": manager.Event()
        }

        _task = manager.Process(
            name = f"{self.__class__.id_prefix} - Status - Error",
            target = error_event_target
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Start the task
        _task.start()

        # Give the task a chance to run/error
        time.sleep(0.2)
        assert _task.status == TaskStatus.ERROR.value

        # Check the results
        _results = _task.results
        assert _results.status == TaskStatus.ERROR.value
        assert not _results.return_value
        assert _results.exception_name == str(EXCEPTION.__name__)
        assert _results.exception_desc == EXCEPTION_DESC
        assert str(_results.exception_stack).find(
                f"{EXCEPTION.__name__}: {EXCEPTION_DESC}") >= 0


    def test_task_short_lived(self, manager):
        ''' 
        Run a task (as process) that ends itself and returns a value
        '''
        # Add a task
        _task = manager.Process(
            name = f"{self.__class__.id_prefix} - Short Lived",
            target = short_lived_event_target,
        )

        # Start the task
        _task.start()

        # What for the task to complete
        while _task.status == TaskStatus.RUNNING.value:
            time.sleep(0.1)
        
        # Stop the task (to clean it up / no zombie)
        _task.cleanup()

        # Check the results
        _results = _task.results
        assert _results.status == TaskStatus.COMPLETED.value
        assert _results.return_value == SHORT_LIVED_RETURN


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

