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
    #
    # Start / Stop a simple task
    #
    def test_simple_task(self, mt):
        # Make sure there are no tasks
        assert len(mt.tasks) == 0
        assert len(mt.running_tasks) == 0

        # Add a task
        _kwargs = {
            "test_event": mt.manager.Event()
        }

        _task_id = mt.task_add(
            id = "Test Task - Thread",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
            restart = False,
            as_thread = True
        )

        # Make sure the task is added but not running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 0

        # Start the task
        mt.task_start(_task_id)
        time.sleep(1)

        # Make sure the task is running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 1

        # Stop the task
        mt.task_stop(_task_id)
        time.sleep(1)

        # Make sure no tasks are running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 0

        # Delete the task
        mt.task_delete(_task_id)

        # Make sure there are no tasks
        assert len(mt.tasks) == 0
        assert len(mt.running_tasks) == 0


#
# Tasks as process
#
class Test_Task_Processes():
    #
    # Start / Stop a simple task
    #
    def test_simple_task(self, mt):
        # Make sure there are no tasks
        assert len(mt.tasks) == 0
        assert len(mt.running_tasks) == 0

        # Add a task
        _kwargs = {
            "test_event": mt.manager.Event()
        }

        # Add a task
        _task_id = mt.task_add(
            id = "Test Task - Process",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
            restart = False,
            as_thread = False
        )

        # Make sure the task is added but not running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 0

        # Start the task
        mt.task_start(_task_id)
        time.sleep(1)

        # Make sure the task is running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 1

        # Stop the task
        mt.task_stop(_task_id)
        time.sleep(1)

        # Make sure no tasks are running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 0

        # Delete the task
        mt.task_delete(_task_id)

        # Make sure there are no tasks
        assert len(mt.tasks) == 0
        assert len(mt.running_tasks) == 0
