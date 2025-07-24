#!/usr/bin/env python3
'''
PyTest - Testing Config

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

import pytest
from appcore.multitasking.task_manager import TaskManager


###########################################################################
#
# Config
#
###########################################################################
def pytest_configure(config):
    pass

###########################################################################
#
# Fixtures
#
###########################################################################
#
# manager (multitasking maanger)
#
@pytest.fixture(scope="function")
def manager():
    return TaskManager()
