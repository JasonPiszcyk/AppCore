#!/usr/bin/env python3
'''
Module Initialisation

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
# Configure logging for the module
from appcore.logging import configure_logger
# _log_level = "info"
_log_level = "debug"
LOG = configure_logger(
        name="TaskManager",
        log_file="/tmp/appcore.log",
        log_level=_log_level,
        to_console=False
)

# What to import when 'import * from module'
__all__ = [ "TaskManager", ]


# What to import as part of the the module (import module)
from appcore.multitasking.task_manager import TaskManager




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

