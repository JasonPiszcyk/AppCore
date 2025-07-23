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
# from appcore.multitasking import TaskManager
from appcore.multitasking.task import TaskDefinition
from appcore.multitasking.task import ProcessTaskDefinition
from appcore.multitasking.task import ThreadTaskDefinition
from multiprocessing import current_process, Manager

#
# Globals
#

def debug(msg):
    with open("/tmp/jpp.txt", "at") as f:
        f.write(f"{msg}\n")


EXCEPTION = RuntimeError
EXCEPTION_DESC = "The exception description"


###########################################################################
#
# Functions to run in the tasks
#
###########################################################################
#
# Simple task to end when an event is set
#
def simple_event_target(test_event=None):
    debug('Waiting for event')
    assert test_event
    test_event.clear()
    test_event.wait()


def simple_event_stop(test_event=None):
    assert test_event
    test_event.set()


#
# Task to generate an error
#
def error_event_target(test_event=None):
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

    def test_task_simple(self):
        ''' Start/stop a task (as a thread) '''
        TaskManager = Manager()
        # Add a task
        _kwargs = {
            "test_event": TaskManager.Event()
        }

        _task = ThreadTaskDefinition(
            name = f"{self.__class__.id_prefix} - Simple",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()
        time.sleep(1)

         # Start the task
        _task.stop()


#
# Tasks as Processes
#
class Test_Task_Process():
    # Attributes for this set of tests
    id_prefix = "Test Task - Process"
    task_type = "process"

    def test_task_simple(self):
        TaskManager = Manager()

        ''' Start/stop a task (as a process) '''
        # Add a task
        _kwargs = {
            "test_event": TaskManager.Event()
        }

        _task = ProcessTaskDefinition(
            name = f"{self.__class__.id_prefix} - Simple",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()
        time.sleep(2)

         # Start the task
        _task.stop()


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

