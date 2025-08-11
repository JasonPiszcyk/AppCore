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
import web_request as WebRequest
from appcore.manager import AppCoreManager


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
# manager (AppCore manager)
#
@pytest.fixture(scope="session")
def manager():
    return AppCoreManager(log_file="/tmp/appcore.log", log_level="debug")


#
# Access to scheduler
#
@pytest.fixture(scope="session")
def scheduler(manager):
    _scheduler = manager.StartScheduler()

    yield _scheduler

    manager.shutdown()


#
# The telemetry server
#
@pytest.fixture(scope="session")
def telemetry_server(manager):
    _ts = manager.StartTelemetryServer()

    yield _ts

    manager.shutdown()


#
# A web request
#
@pytest.fixture(scope="function")
def web_request():
    return WebRequest.Web_Request()
