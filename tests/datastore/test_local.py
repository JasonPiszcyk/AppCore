#!/usr/bin/env python3
'''
PyTest - Test of local datastore functions

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
import crypto_tools

#
# Globals
#
DEFAULT_STR_VALUE = "default_string_value"
SIMPLE_STR = "simple.variable"
SIMPLE_STR_VALUE = "Value for simple variable"


###########################################################################
#
# The tests...
#
###########################################################################
#
# Local
#
class Test_Local_Datastore():
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
        assert ds.get(item) != value
        assert ds.get(item, decrypt=True) == value
        assert ds.get(item, default=default, decrypt=True) == value


    def test_basic(self, manager):
        ''' Test the basics has/get/set/delete '''
        ds = manager.LocalDataStore(security="low")

        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )

        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE)
        self._assert_set(ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE)

        ds.delete(SIMPLE_STR)
        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )


    def test_encryption_no_password(self, manager):
        ''' Test encryption - no password supplied '''
        # Use 'low' security as it is just quicker to compute the key
        ds = manager.LocalDataStore(security="low")

        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )

        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE, encrypt=True)
        self._assert_set_enc(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )

        ds.delete(SIMPLE_STR)
        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )


    def test_encryption_with_password(self, manager):
        ''' Test encryption - simple password supplied '''
        # Use 'low' security as it is just quicker to compute the key
        ds = manager.LocalDataStore(password="a password", security="low")

        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )

        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE, encrypt=True)
        self._assert_set_enc(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )

        ds.delete(SIMPLE_STR)
        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )


    def test_encryption_with_password_salt(self, manager):
        ''' Test encryption - simple password supplied '''
        # Use 'low' security as it is just quicker to compute the key
        ds = manager.LocalDataStore(
            password="a password",
            salt=crypto_tools.fernet.generate_salt(),
            security="low")

        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )

        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE, encrypt=True)
        self._assert_set_enc(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )

        ds.delete(SIMPLE_STR)
        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )


    def test_expiry(self, manager):
        ''' Test an expiring value '''
        ds = manager.LocalDataStore(security="low")

        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
        )
 
        ds.set(SIMPLE_STR, SIMPLE_STR_VALUE, timeout=2)
        self._assert_set(ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE)

        time.sleep(3)
        self._assert_not_set(
            ds, SIMPLE_STR, SIMPLE_STR_VALUE, DEFAULT_STR_VALUE
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

