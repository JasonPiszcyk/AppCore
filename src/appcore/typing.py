#!/usr/bin/env python3
'''
Constants

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
import logging

# Local app modules

# Imports for python variable type hints
from typing import Any


###########################################################################
#
# Types
#
###########################################################################
type KeywordDictType = dict[str, Any]


###########################################################################
#
# Enums
#
###########################################################################
#
# DataType
#
class DataType(enum.Enum):
    NONE            = "none"
    INT             = "int"
    INTEGER         = "integer"
    FLOAT           = "float"
    STR             = "str"
    STRING          = "string"
    BOOL            = "bool"
    BOOLEAN         = "boolean"
    DICT            = "dict"
    DICTIONARY      = "dictionary"
    LIST            = "list"
    TUPLE           = "tuple"
    UUID            = "uuid"
    UUID1           = "uuid1"
    UUID3           = "uuid3"
    UUID4           = "uuid4"
    UUID5           = "uuid5"


#
# TaskStatus
#
class TaskStatus(enum.Enum):
    UNKNOWN         = "Unknown"
    NOT_STARTED     = "Not Started"
    RUNNING         = "Running"
    ERROR           = "Error"
    COMPLETED       = "Completed"


#
# TaskAction
#
class TaskAction(enum.Enum):
    START           = "Start"
    STOP            = "Stop"
    RESTART         = "Restart"
    IGNORE          = "Ignore"


#
# LoggingLevel
#
class LoggingLevel(enum.Enum):
    CRITICAL        = "critical", logging.CRITICAL
    FATAL           = "fatal", logging.CRITICAL
    ERROR           = "error", logging.ERROR
    WARNING         = "warning", logging.WARNING
    WARN            = "warn", logging.WARNING
    INFO            = "info", logging.INFO
    DEBUG           = "debug", logging.DEBUG
    NOTSET          = "notset", logging.NOTSET

    # Additional info
    def __init__(self, value, level):
        self._value_ = value
        self.level = level

    def __new__(cls, value, level):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.level = level
        return obj


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

