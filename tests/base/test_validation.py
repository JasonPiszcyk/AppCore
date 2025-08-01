#!/usr/bin/env python3
'''
PyTest - Test of validation functions

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
from appcore.validation import is_valid_log_level_string


#
# Globals
#


###########################################################################
#
# The tests...
#
###########################################################################
#
# is_valid_log_level
#
class Test_IsValidLogLevel():
    #
    # Tests the log level string
    #
    def test_valid_log_level(self):
        # The list of valid strings
        _valid_log_levels = [
            "critical",
            "fatal",
            "error",
            "warning",
            "warn",
            "info",
            "debug",
            "notset",
        ]

        for _log_level in _valid_log_levels:
            assert is_valid_log_level_string(_log_level)


    def test_invalid_log_level(self):
        # Test invalid log levels
        assert not is_valid_log_level_string()
        assert not is_valid_log_level_string("")
        assert not is_valid_log_level_string(None) # type: ignore
        assert not is_valid_log_level_string(log_level="")
        assert not is_valid_log_level_string(0) # type: ignore
        assert not is_valid_log_level_string("no level")
        assert not is_valid_log_level_string(self) # type: ignore
