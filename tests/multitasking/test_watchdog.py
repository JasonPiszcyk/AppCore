#!/usr/bin/env python3
'''
PyTest - Test of the watchdog

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
WATCHDOG_INTERVAL = 1.0

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
def short_lived_event_target(live_time=2.0):
    time.sleep(live_time)
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
class Test_Watchdog():
    def test_single_thread(self, manager):
        ''' Watch a single Thread '''

        # Create the watchdog
        _watchdog = manager.Watchdog(interval=WATCHDOG_INTERVAL)

        # Add a task
        _kwargs = {
            "test_event": manager.Event()
        }

        _task = manager.Thread(
            name = f"Watchdog - Single - Thread",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Register the task
        _task_label = _watchdog.register(_task)

        # Let it run
        time.sleep(0.5)
        assert _task.status == TaskStatus.RUNNING.value
        time.sleep(1)

        # Remove the task
        _watchdog.deregister(_task_label)
        time.sleep(0.5)
        assert _task.status == TaskStatus.COMPLETED.value

        # Stop the watchdog
        _watchdog.loop_stop()


    def test_single_thread_thread_only(self, manager):
        ''' Watch a single Thread '''

        # Create the watchdog
        _watchdog = manager.Watchdog(
            interval=WATCHDOG_INTERVAL,
            thread_only=True
        )

        # Add a task
        _kwargs = {
            "test_event": manager.Event()
        }

        _task = manager.Thread(
            name = f"Watchdog - Single - Thread",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Register the task
        _task_label = _watchdog.register(_task)

        # Let it run
        time.sleep(0.5)
        assert _task.status == TaskStatus.RUNNING.value
        time.sleep(1)

        # Remove the task
        _watchdog.deregister(_task_label)
        time.sleep(0.5)
        assert _task.status == TaskStatus.COMPLETED.value

        # Stop the watchdog
        _watchdog.loop_stop()


    def test_single_process(self, manager):
        ''' Watch a single Thread '''

        # Create the watchdog
        _watchdog = manager.Watchdog(interval=WATCHDOG_INTERVAL)

        # Add a task
        _kwargs = {
            "test_event": manager.Event()
        }

        _task = manager.Thread(
            name = f"Watchdog - Single - Thread",
            target = simple_event_target,
            kwargs = _kwargs,
            stop_function = simple_event_stop,
            stop_kwargs = _kwargs,
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Register the task
        _task_label = _watchdog.register(_task)

        # Let it run
        time.sleep(0.5)
        assert _task.status == TaskStatus.RUNNING.value
        time.sleep(1)

        # Remove the task
        _watchdog.deregister(_task_label)
        time.sleep(0.5)
        assert _task.status == TaskStatus.COMPLETED.value

        # Stop the watchdog
        _watchdog.loop_stop()


    def test_single_thread_ending(self, manager):
        ''' Watch a single Thread that ends '''

        _task_time = 2.0

        # Create the watchdog to check check less frequently than the task ends
        _watchdog = manager.Watchdog(interval=_task_time * 2)

        # Add a task
        _kwargs = {
            "live_time": _task_time
        }

        _task = manager.Thread(
            name = f"Watchdog - Single - Thread",
            target = short_lived_event_target,
            kwargs = _kwargs,
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Register the task
        _task_label = _watchdog.register(_task)

        # Let it run
        time.sleep(0.5)
        assert _task.status == TaskStatus.RUNNING.value
        time.sleep(_task_time)
        assert _task.status == TaskStatus.COMPLETED.value
        time.sleep(_task_time)
        assert _task.status == TaskStatus.RUNNING.value

        # Remove the task
        _watchdog.deregister(_task_label)
        time.sleep(_task_time)
        assert _task.status == TaskStatus.COMPLETED.value

        # Stop the watchdog
        _watchdog.loop_stop()


    def test_single_process_ending(self, manager):
        ''' Watch a single process that ends '''

        _task_time = 2.0

        # Create the watchdog to check check less frequently than the task ends
        _watchdog = manager.Watchdog(interval=_task_time * 2)

        # Add a task
        _kwargs = {
            "live_time": _task_time
        }

        _task = manager.Process(
            name = f"Watchdog - Single - Process",
            target = short_lived_event_target,
            kwargs = _kwargs,
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Register the task
        _task_label = _watchdog.register(_task)

        # Let it run
        time.sleep(0.5)
        assert _task.status == TaskStatus.RUNNING.value
        time.sleep(_task_time)
        assert _task.status == TaskStatus.COMPLETED.value
        time.sleep(_task_time)
        assert _task.status == TaskStatus.RUNNING.value

        # Remove the task
        _watchdog.deregister(_task_label)
        time.sleep(_task_time)
        assert _task.status == TaskStatus.COMPLETED.value

        # Stop the watchdog
        _watchdog.loop_stop()


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

