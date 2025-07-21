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
from src.appcore.base import set_value
from src.appcore.constants import DataType
import src.appcore.multitasking as multitasking
from multiprocessing import Event


#
# Globals
#

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
    # An event to use
    task_test_event = Event()

    # function to run in the task
    def _task_target(self):
        Test_Task_Threads.task_test_event.clear()
        Test_Task_Threads.task_test_event.wait()

    # function to run to stop a task
    def _task_stop(self):
        Test_Task_Threads.task_test_event.set()


    #
    # Start / Stop a simple task
    #
    def test_simple_task(self, mt):
        # Make sure there are no tasks
        assert len(mt.tasks) == 0
        assert len(mt.running_tasks) == 0

        # Add a task
        _task_id = mt.task_add(
            id = "Test Task - Thread",
            target = self._task_target,
            stop = self._task_stop,
            kwargs = {},
            restart = False,
            as_thread = True
        )

        # Make sure the task is added but not running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 0

        # Start the task
        mt.task_start(_task_id)
        time.sleep(1)

        # Make sure the tasks is running
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
    # An event to use
    task_test_event = Event()

    # function to run in the task
    def _task_target(self):
        Test_Task_Processes.task_test_event.clear()
        Test_Task_Processes.task_test_event.wait()


    # function to run to stop a task
    def _task_stop(self):
        Test_Task_Processes.task_test_event.set()


    #
    # tart / Stop a simple task
    #
    def test_simple_task(self, mt):
        # Make sure there are no tasks
        assert len(mt.tasks) == 0
        assert len(mt.running_tasks) == 0

        # Add a task
        _task_id = mt.task_add(
            id = "Test Task - Process",
            target = self._task_target,
            stop = self._task_stop,
            kwargs = {},
            restart = False,
            as_thread = False
        )

        # Make sure the task is added but not running
        assert len(mt.tasks) == 1
        assert len(mt.running_tasks) == 0

        # Start the task
        mt.task_start(_task_id)
        time.sleep(1)

        # Make sure the tasks is running
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
