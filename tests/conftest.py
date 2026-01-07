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
###########################################################################
#
# Imports
#
###########################################################################
# Shared variables, constants, etc
from tests.constants import *

# System Modules
import pytest

# Local app modules

# Imports for python variable type hints


###########################################################################
#
# Config
#
###########################################################################
def pytest_configure(config: pytest.Config):
    '''
    Global configuration for the PyTest session

    Args:
        config (pytest.Config): Configuration information

    Returns:
        None

    Raises:
        None
    '''
    pass


###########################################################################
#
# Fixtures
#
###########################################################################
