#!/usr/bin/env python3
'''
Datastore - Local

Datastore stores information locally in a shared dictionary.

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

# Local app modules
from appcore.datastore.datastore_base import DataStoreBaseClass
from appcore.conversion import to_json, from_json

# Imports for python variable type hints
from typing import Any
from threading import Lock as LockType


###########################################################################
#
# Module Specific Items
#
###########################################################################
#
# Types
#


#
# Constants
#


#
# Global Variables
#


###########################################################################
#
# DataStoreLocal Class Definition
#
###########################################################################
class DataStoreLocal(DataStoreBaseClass):
    '''
    Class to describe the local datastore.

    The data is store in a dictionary that is made available globally
    throughout the application

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            lock: LockType | None = None,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        assert lock, f"A lock is required to implement the local datastore"

        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__data: dict = {}
        self.__lock: LockType = lock

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################


    ###########################################################################
    #
    # Data Access
    #
    ###########################################################################
    #
    # has
    #
    def has(
            self,
            name: str = "",
    ) -> bool:
        '''
        Check if the item exists in the datastore

        Args:
            name (str): The name of the item to check

        Returns:
            bool: True if the item exists, False otherwise

        Raises:
            None
        '''
        return name in self.__data


    #
    # get
    #
    def get(
            self,
            name: str = "",
            default: Any = None,
            decrypt: bool = False
    ) -> Any:
        '''
        Get a value

        Args:
            name (str): The name of the item to get
            default (Any): Value to return if the item cannot be found
            decrypt (bool): If True, attempt to decrypt the value

        Returns:
            Any: The value of the item

        Raises:
            None
        '''
        if not self.has(name): return default

        _value = self.__data[name]

        if decrypt:
            # Decrypt, covert from JSON
            _decrypted_value = self._decrypt(_value)
            _value = from_json(_decrypted_value)

        return _value


    #
    # set
    #
    def set(
            self,
            name: str = "",
            value: Any = None,
            encrypt: bool = False
    ) -> None:
        '''
        Set a value for an item

        Args:
            name (str): The name of the item to set
            value (Any): Value to set the item to
            encrypt (bool): If True, attempt to encrypt the value

        Returns:
            None

        Raises:
            None
        '''
        # Encrypt the value if required
        if encrypt:
            # Convert to JSON, Encrypt
            _json_value = to_json(value)
            value = self._encrypt(_json_value)

        # Set the value
        self.__lock.acquire()
        self.__data[name] = value
        self.__lock.release()


    #
    # delete
    #
    def delete(
            self,
            name: str = "",
    ) -> None:
        '''
        Delete an item from the datastore

        Args:
            name (str): The name of the item to delete

        Returns:
            Any: The value of the item

        Raises:
            None
        '''
        if self.has(name):
            self.__lock.acquire()
            del self.__data[name]
            self.__lock.release()


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
