#!/usr/bin/env python3
'''
Shared information (eg variables, etc)

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

# System Modules
import enum

# Local app modules

# Imports for python variable type hints


###########################################################################
#
# Variables / Constants
#
###########################################################################
AppGlobal = {
    # The Multitasking class instance
    "MultiTasking": None,

    # Multiprocessing Manager object to share resource between tasks
    "MultiProcessingManager": None,

    # The shared Task Info (updatable by all)
    "TaskInfo": {}
}


# Unique IDs for the Parent process, watchdog and queue tasks
TASK_ID_MULTITASKING_PROCESS: str = "2999169d-0bf2-4d6f-85bd-f4d404d219f1"
TASK_ID_PARENT_PROCESS: str = "01964d35-f692-476f-b8e8-de4b9958c102"
TASK_ID_WATCHDOG: str = "ee232fe7-5cbc-43b7-aa7f-43445f75bc2b"
TASK_ID_QUEUE_LOOP: str = "103fa334-0afa-4404-b2fb-d6180a20cda0"


# The message types
class TaskAction(enum.Enum):
    START           = "__task_start__"
    STOP            = "__task_stop__"
    ADD             = "__task_add__"
    DELETE          = "__task_delete__"
    STATUS          = "__task_status__"


###########################################################################
#
# Types
#
###########################################################################


###########################################################################
#
# Enums
#
###########################################################################


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

