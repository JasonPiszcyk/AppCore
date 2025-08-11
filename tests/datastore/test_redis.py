#!/usr/bin/env python3
'''
PyTest - Test of redis datastore functions

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
from appcore.typing import TaskStatus
import crypto_tools
import json
import appcore.datastore.exception as exception


#
# Globals
#
DEFAULT_SIMPLE_STR_VALUE = "default_string_value"
SIMPLE_STR = "simple.variable"
SIMPLE_STR_VALUE = "Value for simple variable"
CHANGE_SIMPLE_STR_VALUE = "New value for the simple variable"

DEFAULT_TASK_STR_VALUE = "default_string_value_for_task"
TASK_STR = "task.variable"
TASK_STR_VALUE = "Value for task variable"
CHANGE_TASK_STR_VALUE = "New value for the task variable"

DOT_NAME_LIST = [ "1", "2.1", "2.2" , "2.3.1" ]
INVALID_DOT_NAME_LIST = [ "1.1", "2" ]


###########################################################################
#
# Functions to run in the tasks
#
###########################################################################
#
# Task to set a value
#
def shared_value_target(redis_ds=None, item=None):
    assert redis_ds

    # Connect to Redis
    redis_ds.connect()
    # Make sure the value exists
    assert redis_ds.has(item)

    # Change the value
    redis_ds.set(item, CHANGE_TASK_STR_VALUE, encrypt=True)

    # Return the original value + new value
    return TASK_STR_VALUE + CHANGE_TASK_STR_VALUE



###########################################################################
#
# The tests...
#
###########################################################################
#
# Local
#
class Test_Redis_Datastore():
    def _assert_not_set(self, ds, item, value, default):
        assert not ds.has(item)
        assert not ds.get(item)
        assert ds.get(item, default=default) == default


    def _assert_set(self, ds, item, value, default):
        assert ds.has(item)
        assert ds.get(item) == value
        assert ds.get(item, default=default) == value


    def _assert_set_enc(self, ds, item, value, default):
        assert ds.has(item)
        with pytest.raises(json.decoder.JSONDecodeError):
            _ = ds.get(item)

        assert ds.get(item, decrypt=True) == value
        assert ds.get(item, default=default, decrypt=True) == value


    def test_basic(self, manager):
        ''' Test the basics has/get/set/delete '''
        ds = manager.RedisDataStore(security="low")
        ds.connect()

        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )

        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE)
        self._assert_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )

        ds.delete(SIMPLE_STR)
        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )


    def test_encryption_no_password(self, manager):
        ''' Test encryption - no password supplied '''
        # Use 'low' security as it is just quicker to compute the key
        ds = manager.RedisDataStore(security="low")
        ds.connect()

        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )

        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE, encrypt=True)
        self._assert_set_enc(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )

        ds.delete(SIMPLE_STR)
        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )


    def test_encryption_with_password(self, manager):
        ''' Test encryption - simple password supplied '''
        # Use 'low' security as it is just quicker to compute the key
        ds = manager.RedisDataStore(password="a password", security="low")
        ds.connect()

        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )

        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE, encrypt=True)
        self._assert_set_enc(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )

        ds.delete(SIMPLE_STR)
        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )


    def test_encryption_with_password_salt(self, manager):
        ''' Test encryption - simple password supplied '''
        # Use 'low' security as it is just quicker to compute the key
        ds = manager.RedisDataStore(
            password="a password",
            salt=crypto_tools.fernet.generate_salt(),
            security="low")

        ds.connect()

        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )

        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE, encrypt=True)
        self._assert_set_enc(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )

        ds.delete(SIMPLE_STR)
        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )


    def test_expiry(self, manager):
        ''' Test an expiring value '''
        ds = manager.RedisDataStore(security="low")
        ds.connect()

        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )
 
        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE, timeout=2)
        self._assert_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )

        time.sleep(3)
        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_SIMPLE_STR_VALUE
        )


    def test_share_thread(self, manager):
        ''' Test sharing a value to a thread '''
        ds = manager.RedisDataStore(security="low")

        # Create an item
        # Connect and disconnect to prevent Redis connection being
        # copied to child task
        ds.connect()
        ds.set(TASK_STR, TASK_STR_VALUE, encrypt=True)
        self._assert_set_enc(
            ds, TASK_STR, TASK_STR_VALUE, DEFAULT_TASK_STR_VALUE
        )

        # Add a task
        _kwargs = {
            "redis_ds": ds,
            "item": TASK_STR,
        }

        _task = manager.Thread(
            name = f"Redis Datastore - Test Share Thread",
            target = shared_value_target,
            kwargs = _kwargs
        )

        # Start the task (and connect to Redis in this thread)
        _task.start()

        # What for the task to complete
        while _task.status == TaskStatus.RUNNING.value:
            time.sleep(0.1)
        
        # Stop the task (to clean it up / no zombie)
        _task.cleanup()

        # Check the results
        _results = _task.results
        assert _results.status == TaskStatus.COMPLETED.value
        assert _results.return_value == TASK_STR_VALUE + CHANGE_TASK_STR_VALUE

        # Check the value of the item
        ds.connect()
        self._assert_set_enc(
            ds, TASK_STR, CHANGE_TASK_STR_VALUE, DEFAULT_TASK_STR_VALUE
        )


    def test_share_process(self, manager):
        ''' Test sharing a value to a process '''
        ds = manager.RedisDataStore(security="low")

        # Create an item
        # Connect and disconnect to prevent Redis connection being
        # copied to child task
        ds.connect()
        ds.set(TASK_STR, TASK_STR_VALUE, encrypt=True)
        self._assert_set_enc(
            ds, TASK_STR, TASK_STR_VALUE, DEFAULT_TASK_STR_VALUE
        )
        ds.disconnect()

        # Add a task
        _kwargs = {
            "redis_ds": ds,
            "item": TASK_STR,
        }

        _task = manager.Process(
            name = f"Redis Datastore - Test Share Process",
            target = shared_value_target,
            kwargs = _kwargs
        )

        # Start the task (and connect to Redis in this process)
        _task.start()

        # What for the task to complete
        while _task.status == TaskStatus.RUNNING.value:
            time.sleep(0.1)
        
        # Stop the task (to clean it up / no zombie)
        _task.cleanup()

        # Check the results
        _results = _task.results
        assert _results.status == TaskStatus.COMPLETED.value
        assert _results.return_value == TASK_STR_VALUE + CHANGE_TASK_STR_VALUE

        # Check the value of the item
        ds.connect()
        self._assert_set_enc(
            ds, TASK_STR, CHANGE_TASK_STR_VALUE, DEFAULT_TASK_STR_VALUE
        )


    def test_basic_dotname(self, manager):
        ''' Test the basics has/get/set/delete '''
        ds = manager.RedisDataStore(security="low", dot_names=True)
        ds.connect()

        for _name in DOT_NAME_LIST:
            self._assert_not_set(
                ds, _name, f"{_name}_value", DEFAULT_SIMPLE_STR_VALUE
            )

            ds.set(_name, f"{_name}_value")
            self._assert_set(
                ds, _name, f"{_name}_value", DEFAULT_SIMPLE_STR_VALUE
            )

        # Test writing to an invalid dot name
        # - trying to add a value in the lower level of a tree
        # - Trying to add a branch when a value is set
        for _name in INVALID_DOT_NAME_LIST:
            with pytest.raises(exception.DataStoreDotNameError):
                ds.set(_name, f"{_name}_value")

        for _name in DOT_NAME_LIST:
            ds.delete(_name)
            self._assert_not_set(
                ds, _name, f"{_name}_value", DEFAULT_SIMPLE_STR_VALUE
            )


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

