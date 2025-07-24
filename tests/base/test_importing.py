#!/usr/bin/env python3
'''
PyTest - Test of module importing

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
import sys


#
# Globals
#
MODULE_APPCORE = "appcore"
MODULE_MULTITASKING = "appcore.multitasking"

DEFAULT_ATTR = "__doc__"

###########################################################################
#
# The tests...
#
###########################################################################
#
# set_value
#
class Test_Importing():
    def _check_module_imported(self, module_name=""):
        assert module_name
        assert module_name in sys.modules


    def _check_module_attr(self, module_name="", attr=""):
        assert module_name
        assert attr
        assert hasattr(module_name, attr)


    def _check_module_dict(self, module_name="", attr=""):
        assert module_name
        assert attr
        assert attr in sys.modules[module_name].__dict__.keys()


    #
    # Test the modules import correctly
    #
    def test_import_appcore(self):
        ''' import appcore '''
        _module_name = MODULE_APPCORE

        # straight import
        exec(f"import {_module_name}")
        self._check_module_imported(_module_name)


    def test_import_multitasking(self):
        ''' import multitasking module '''
        _module_name = MODULE_MULTITASKING
        _short_module_name = MODULE_MULTITASKING.rpartition('.')[2]

        # Straight Import
        exec(f"import {_module_name}")
        self._check_module_imported(_module_name)

        # Import as
        exec(f"import {_module_name} as {_short_module_name}")
        self._check_module_imported(_module_name)
        self._check_module_attr(_short_module_name, DEFAULT_ATTR)
        self._check_module_dict(_module_name, "TaskManager")
