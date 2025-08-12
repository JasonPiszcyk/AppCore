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
from datetime import datetime
from appcore.multitasking.message_frame import MessageType
import appcore.multitasking.exception as exception
from appcore.typing import TaskStatus

#
# Globals
#
BASIC_TEXT = "Basic text to send over queue"
BASIC_DICT = {
    "1": "some string value",
    "2": 2,
    "a_key": "a_value",
}

EXCEPTION = RuntimeError
EXCEPTION_DESC = "Queue Check Error"


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


#
# Message handler that raises an exception if the message isn't correct
#
def message_handler(frame):
    if frame.data != BASIC_TEXT:
        raise EXCEPTION(EXCEPTION_DESC)


#
# Message handler that returns the frame data string with "response:" prepended
#
def query_handler_string(frame):
    return f"response:{str(frame.data)}"


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
        _msg = q.get_data()
        assert _msg == BASIC_TEXT

        q.put(BASIC_DICT)
        _msg = q.get_data()
        assert _msg == BASIC_DICT


    def test_put_type_exit(self, manager):
        ''' Test put_type with type of 'EXIT' '''
        q = manager.Queue()

        q._put_type(message_type=MessageType.EXIT)
        with pytest.raises(exception.MultiTaskingQueueFrameExit):
            _ = q.get()


#
# Queue Listener
#
class Test_Queue_Listener():
    def test_listener_start_stop_thread(self, manager):
        ''' Test starting/stopping a listener running in a thread '''
        q = manager.Queue(message_handler=message_handler)

        # Create a thread for the listener
        _kwargs = {
            "queue": q
        }

        _task = manager.Thread(
            name = f"Queue Listener - Start/Stop Thread",
            target = start_queue_listener,
            kwargs = _kwargs,
            stop_function = stop_queue_listener,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Start the task
        _task.stop()


    def test_listener_start_stop_process(self, manager):
        ''' Test sarting/stopping a listener running in a process '''
        q = manager.Queue(message_handler=message_handler)

        # Create a thread for the process
        _kwargs = {
            "queue": q
        }

        _task = manager.Process(
            name = f"Queue Listener - Start/Stop Process",
            target = start_queue_listener,
            kwargs = _kwargs,
            stop_function = stop_queue_listener,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Start the task
        _task.stop()


    def test_listener_thread(self, manager):
        ''' Test a listener running in a thread '''
        q = manager.Queue(message_handler=message_handler)

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

        # Send the message
        q.put(BASIC_TEXT)
        assert _task.status == TaskStatus.RUNNING.value

         # Send a message that should raise an exception (Ending the listener)
        q.put(BASIC_DICT)
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


    def test_listener_process(self, manager):
        ''' Test a listener running in a process '''
        q = manager.Queue(message_handler=message_handler)

        # Create a thread for the listener
        _kwargs = {
            "queue": q
        }

        _task = manager.Process(
            name = f"Queue Listener - Thread",
            target = start_queue_listener,
            kwargs = _kwargs,
            stop_function = stop_queue_listener,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Send the message
        q.put(BASIC_TEXT)
        assert _task.status == TaskStatus.RUNNING.value

         # Send a message that should raise an exception (Ending the listener)
        q.put(BASIC_DICT)
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


#
# Queue Query/Responsd
#
class Test_Queue_Query_Response():
    def test_query_success(self, manager):
        ''' Test a Query/Response - Success'''
        _query_string = str(datetime.today())

        query_q = manager.Queue(message_handler=query_handler_string)
        response_q = manager.Queue()

        # Create a thread for the listener
        _kwargs = {
            "queue": query_q
        }

        _task = manager.Thread(
            name = f"Queue Listener - Query - Success",
            target = start_queue_listener,
            kwargs = _kwargs,
            stop_function = stop_queue_listener,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Send the query
        _session_id = query_q.query(_query_string, response_queue=response_q)

        # Get the response
        _resp_frame = response_q.get(timeout=5.0)
        assert _resp_frame
        assert _resp_frame.session_id == _session_id
        assert _resp_frame.data == f"response:{_query_string}"

        # Stop the task
        _task.stop()


    def test_query_error(self, manager):
        ''' Test a Query/Response - Error'''
        _query_string = str(datetime.today())

        query_q = manager.Queue(message_handler=query_handler_string)
        response_q = manager.Queue()

        # Create a thread for the listener
        _kwargs = {
            "queue": query_q
        }

        # Send the query without the response queue
        with pytest.raises(exception.MultiTaskingQueueNotFoundError):
            _ = query_q.query(_query_string)

        # Send the query with the response queue set to None
        with pytest.raises(exception.MultiTaskingQueueNotFoundError):
            _ = query_q.query(_query_string, response_queue=None)

        # Send the query with the response queue set to a string
        with pytest.raises(AssertionError, match="Response Queue is not valid"):
            _ = query_q.query(_query_string, response_queue="A_queue")


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

