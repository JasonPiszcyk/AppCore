#!/usr/bin/env python3
'''
PyTest - Test of conversion functions

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
from appcore.conversion import set_value
from appcore.typing import DataType


#
# Globals
#
DEFAULT_NO_MATCH = "This should not match"



###########################################################################
#
# The tests...
#
###########################################################################
#
# set_value
#
class Test_SetValue():
    #
    # Basic Tests to perform when setting a value
    #
    def _set_valid(self, data=None, type=None, default=None):
        assert type
        assert default

        # Set value - with correct info
        _res = set_value(data=data, type=type, default=DEFAULT_NO_MATCH)
        if not data:
            assert not _res
        else:
            assert _res
            assert _res != DEFAULT_NO_MATCH


    def _set_invalid_type(self, data=None, type=None, default=None):
        assert type
        assert default
        _invalid_type = "Invalid type"

        # Set value - with incorrect type
        with pytest.raises(AssertionError):
            _res = set_value(data=data, type=_invalid_type, default=DEFAULT_NO_MATCH) # type: ignore


    def _set_invalid_data(self, data=None, type=None, default=None):
        assert type
        assert default

        # Set value - with invalid data
        _res = set_value(data=data, type=type, default=default)
        assert _res
        assert _res == default



    #
    # Tests for different data types
    #
    def test_string(self):
        _valid_dataset = ("a string", "", 14, 192.3, { "dict_key": "dict_value"}, "d5bf0b08-38a3-4116-8a7c-2655e6b54b64",)
        _invalid_dataset = ()
        _default = "Default String"
        _typeset = (DataType.STRING, DataType.STR)

        for _type in _typeset:
            for _entry in _valid_dataset:
                self._set_valid(data=_entry, type=_type, default=_default)
                self._set_invalid_type(data=_entry, type=_type, default=_default)

            for _entry in _invalid_dataset:
                self._set_invalid_data(data=_entry, type=_type, default=_default)


    def test_integer(self):
        _valid_dataset = (14, 192.3,)
        _invalid_dataset = ("a string", "", { "dict_key": "dict_value"}, "d5bf0b08-38a3-4116-8a7c-2655e6b54b64",)
        _default = 7
        _typeset = (DataType.INTEGER, DataType.INT)

        for _type in _typeset:
            for _entry in _valid_dataset:
                self._set_valid(data=_entry, type=_type, default=_default)
                self._set_invalid_type(data=_entry, type=_type, default=_default)

            for _entry in _invalid_dataset:
                self._set_invalid_data(data=_entry, type=_type, default=_default)


    def test_dict(self):
        _valid_dataset = ({ "dict_key": "dict_value"}, "")
        _invalid_dataset = ("a string", 14, 192.3, "d5bf0b08-38a3-4116-8a7c-2655e6b54b64",)
        _default = "Doesn't really matter"
        _typeset = (DataType.DICTIONARY, DataType.DICT)

        for _type in _typeset:
            for _entry in _valid_dataset:
                self._set_valid(data=_entry, type=_type, default=_default)
                self._set_invalid_type(data=_entry, type=_type, default=_default)

            for _entry in _invalid_dataset:
                self._set_invalid_data(data=_entry, type=_type, default=_default)


    def test_uuid4(self):
        _valid_dataset = ("d5bf0b08-38a3-4116-8a7c-2655e6b54b64",)
        _invalid_dataset = ("a string", "", 14, 192.3, { "dict_key": "dict_value"},)
        _default = "1420a26b-b4c1-4345-ba0a-d42a94569fc9"
        _typeset = (DataType.UUID4,)

        for _type in _typeset:
            for _entry in _valid_dataset:
                self._set_valid(data=_entry, type=_type, default=_default)
                self._set_invalid_type(data=_entry, type=_type, default=_default)

            for _entry in _invalid_dataset:
                self._set_invalid_data(data=_entry, type=_type, default=_default)
