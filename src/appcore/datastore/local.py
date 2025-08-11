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
import appcore.datastore.exception as exception
from appcore.conversion import to_json, from_json, set_value, DataType


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

    The data is stored in a dictionary that is made available globally
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
            lock (Lock): A SyncManager lock use to protect the dict
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            AssertionError:
                When a SyncManager lock is not supplied
        '''
        assert lock, f"A lock is required to implement the local datastore"

        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__data: dict = {}
        self.__data_expiry: list = []

        self.__lock: LockType = lock

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################


    ###########################################################################
    #
    # Maintenance Functions
    #
    ###########################################################################
    #
    # __item_maintenance
    #
    def __item_maintenance(self):
        '''
        Perform maintenance on items (such as expiry)

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Process the expiry list
        _now = self.timestamp()
        _sorted_expiry_list = sorted(self.__data_expiry)

        # Use a copy of the expiry list so we can change it during processing
        for _entry in _sorted_expiry_list:
            # Extract the timestamp from the key
            _timestamp_str, _, _name = _entry.partition("__")
            _timestamp = set_value(_timestamp_str, DataType.INT, default=0)            

            # Stop processing if the timestamp is in the future
            if _now < _timestamp: break

            # Remove the entry (and the expiry record)
            self.__lock.acquire()
            if _name in self.__data: del self.__data[_name]
            self.__data_expiry.remove(_entry)
            self.__lock.release()


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
            name: str = ""
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
        self.__item_maintenance()
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
        self.__item_maintenance()
        if not self.has(name): return default

        _value = self.__data[name]

        if decrypt:
            # Decrypt, convert from JSON
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
            encrypt: bool = False,
            timeout: int = 0
    ) -> None:
        '''
        Set a value for an item

        Args:
            name (str): The name of the item to set
            value (Any): Value to set the item to
            encrypt (bool): If True, attempt to encrypt the value
            timeout (int): The number of seconds before the item should be
                deleted (0 = never delete)

        Returns:
            None

        Raises:
            AssertionError:
                When timeout is not zero or a positive integer
            DataStoreDotNameError:
                When the dot name is a low part of a hierarchy
        '''
        assert isinstance(timeout, int), "Timeout value must be an integer"
        assert timeout >= 0, "Timeout value must be a postive integer"

        self.__item_maintenance()

        # Check on dot names
        if self._dot_names:
            _keys = list(self.__data.keys())
            if not self._check_dot_name(keys=_keys, name=name):
                raise exception.DataStoreDotNameError(
                    "Value cannot be stored in a intermediate dot level name"
                )

        # Encrypt the value if required
        if encrypt:
            # Convert to JSON, Encrypt
            _json_value = to_json(value)
            value = self._encrypt(_json_value)

        # Set the value
        self.__lock.acquire()
        self.__data[name] = value

        # Set the expiry info for the item if required
        if timeout > 0:
            _timestamp = self.timestamp(offset=timeout)

            # Append the item name to prevent duplicate keys/timestamps
            self.__data_expiry.append(f"{_timestamp}__{name}")

        self.__lock.release()


    #
    # delete
    #
    def delete(
            self,
            name: str = ""
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
        self.__item_maintenance()

        if self.has(name):
            self.__lock.acquire()
            del self.__data[name]
            self.__lock.release()


    ###########################################################################
    #
    # Export Functions
    #
    ###########################################################################
    #
    # export_to_json
    #
    def export_to_json(
            self,
            container: bool = True
    ) -> str:
        '''
        Export the data store to JSON

        Args:
            container (bool): If true, the export contains an outer layer:
                {
                    "value": { The export values },
                    "type": "dictionary"
                }

        Returns:
            str: The JSON string

        Raises:
            None
        '''
        # Convert to JSON
        self.logger.debug("Exporting Datastore to JSON")
        _export_data = {}

        # Transform the data to a straight dict
        _key_list = sorted(self.__data.keys())

        for _key in _key_list:
            # If dot names, handle the hierarchy
            if self._dot_names:
                _rest = _key
                _cur_level = _export_data

                while _rest:
                    # Split the name to get the first level (and the rest)
                    # If no dot in the name, then _rest will be empty
                    (_level, _, _rest) = _rest.partition(".")

                    if not _rest:
                        # This is the item name
                        _cur_level[_level] = self.get(_key)
                        continue

                    elif not _level in _cur_level:
                        _cur_level[_level] = {}

                    # Move on to the next level
                    _cur_level = _cur_level[_level]

            else:
                _export_data[_key] = self.get(_key)

        return to_json(
            data=_export_data,
            skip_invalid=True,
            container=container
        )


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
