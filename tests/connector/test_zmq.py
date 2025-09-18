#!/usr/bin/env python3
'''
PyTest - Test of ZMQ Interface functions

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
import functools
from pathlib import Path
from datetime import datetime
from appcore.connector.zmq import ZMQInterface



from appcore.multitasking.message_frame import MessageType
import appcore.multitasking.exception as exception
from appcore.typing import TaskStatus

#
# Globals
#
BASIC_BYTES = b"Basic bytes array to send over queue"
CONTROL_ADDRESS = "ipc:///tmp/_local_receiver_control"
CERT_DIR = f"{Path(__file__).parent}/../data"


###########################################################################
#
# Message Handlers
#
###########################################################################
def request_handler(zmq, client_id, msg):
    zmq.response(client_id, b"Response_" + msg)


def query_handler(msg):
    return b"Response_" + msg


###########################################################################
#
# Functions to run in the tasks
#
###########################################################################
#
# start/stop a ZMQ Server
#
def start_zmq_server():
    # Create a ZMQ receiver
    global zmq
    zmq = ZMQInterface(
        address="*",
        port=9119,
        cert_dir=CERT_DIR,
        server_key_name="zmq_test",
        control_addr=CONTROL_ADDRESS,
        request_handler = request_handler,
        query_handler = query_handler,
        log_level="info",
        log_to_console=True
    )
    zmq.server()
    zmq.listen()


def stop_zmq_server():
    zmq.listen_stop()


###########################################################################
#
# ZMQ Client
#
###########################################################################
def zmq_client():
    _client = ZMQInterface(
        address="127.0.0.1",
        port=9119,
        cert_dir=CERT_DIR,
        client_key_name="zmq_test",
        server_key_name="zmq_test",
        log_level="debug",
        log_to_console=True
    )
    _client.client()

    return _client


###########################################################################
#
# The tests...
#
###########################################################################
#
# Basic 
#
class Test_Messages:
    def test_in_band_query_successful(self, manager):
        ''' Test a simple in band query '''
        # Create a thread for the listener
        _kwargs = {}

        _task = manager.Thread(
            name = f"ZMQ Listener - Start/Stop Thread",
            target = start_zmq_server,
            kwargs = _kwargs,
            stop_function = stop_zmq_server,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        _client = zmq_client()
        x = _client.query(BASIC_BYTES)
        assert x != "Unknown Response"
        assert x == b"Response_" + BASIC_BYTES

        # Start the task
        _task.stop()


    def test_out_of_band_query_successful(self, manager):
        ''' Test a simple out of band query '''
        # Create a thread for the listener
        _kwargs = {}

        _task = manager.Thread(
            name = f"ZMQ Listener - Start/Stop Thread",
            target = start_zmq_server,
            kwargs = _kwargs,
            stop_function = stop_zmq_server,
            stop_kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        _client = zmq_client()
        x = _client.request(BASIC_BYTES)
        assert x != "Unknown Response"
        assert x == b"Response_" + BASIC_BYTES

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
