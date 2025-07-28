#!/usr/bin/env python3
'''
PyTest - Test of queueing functions

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
from appcore.multitasking._basic_queue import _BasicQueue
from appcore.multitasking._message_frame import _MessageType
import appcore.multitasking.exception as exception

#
# Globals
#
BASIC_TEXT = "Basic text to send over queue"
BASIC_DICT = {
    "1": "some string value",
    "2": 2,
    "a_key": "a_value",
}


###########################################################################
#
# Functions to run in the tasks
#
###########################################################################
#
# Tasks to start/stop a queue listener
#
def start_queue_listener(queue=None):
    assert queue
    queue.listener()


def stop_queue_listener(queue=None):
    assert queue
    queue.listener_stop(remote=True)


###########################################################################
#
# The tests...
#
###########################################################################
#
# Basic Queue
#
class Test_Basic_Queue():
    def test_put_get(self, manager):
        ''' Test a simple put/get '''
        q = manager.Queue()

        q.put(BASIC_TEXT)
        _msg = q.get()
        assert _msg == BASIC_TEXT

        q.put(BASIC_DICT)
        _msg = q.get()
        assert _msg == BASIC_DICT


    def test_put_action(self, manager):
        ''' Test put_action '''
        q = manager.Queue()

        q.put_action(message_type=_MessageType.EXIT)
        with pytest.raises(exception.MultiTaskingQueueFrameExit):
            _ = q.get()


#
# Queue
#
class Test_Queue():
    def test_listener_thread(self, manager):
        ''' Test a simple put/get '''
        q = manager.Queue()

        # Create a thread for the listener
        _kwargs = {
            "queue": q
        }

        _task = manager.Thread(
            name = f"Queue Listener - Thread",
            target = start_queue_listener,
            kwargs = _kwargs,
            stop_function = stop_queue_listener,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()

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

