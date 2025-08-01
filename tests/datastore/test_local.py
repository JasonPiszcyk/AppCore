#!/usr/bin/env python3
'''
PyTest - Test of local datostore functions

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
DEFAULT_STR_VALUE = "default_string_value"
SIMPLE_STR = "simple.variable"
SIMPLE_STR_VALUE = "Value for simple variable"


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
# Local
#
class Test_Local_Datastore():
    def test_basic(self, manager):
        ''' Test the basics has/get/set/delete '''
        ds = manager.LocalDataStore()

        assert not ds.has(SIMPLE_STR)
        assert not ds.get(SIMPLE_STR)
        assert ds.get(SIMPLE_STR, default=DEFAULT_STR_VALUE) == DEFAULT_STR_VALUE

        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE)
        assert ds.has(SIMPLE_STR)
        assert ds.get(SIMPLE_STR) == SIMPLE_STR_VALUE
        assert ds.get(SIMPLE_STR, default=DEFAULT_STR_VALUE) == SIMPLE_STR_VALUE

        ds.delete(SIMPLE_STR)
        assert not ds.has(SIMPLE_STR)
        assert not ds.get(SIMPLE_STR)
        assert ds.get(SIMPLE_STR, default=DEFAULT_STR_VALUE) == DEFAULT_STR_VALUE


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

