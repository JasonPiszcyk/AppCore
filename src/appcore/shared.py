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

# Local app modules

# Imports for python variable type hints
from typing import Any, Callable


###########################################################################
#
# Types
#
###########################################################################
type KeywordDict = dict[str, Any]


###########################################################################
#
# Enums
#
###########################################################################
#
# DataType
#
class DataType(enum.Enum):
    INT             = "int"
    INTEGER         = "integer"
    STR             = "str"
    STRING          = "string"
    BOOL            = "bool"
    BOOLEAN         = "boolean"
    DICT            = "dict"
    DICTIONARY      = "dictionary"
    UUID1           = "uuid1"
    UUID3           = "uuid3"
    UUID4           = "uuid4"
    UUID5           = "uuid5"


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

