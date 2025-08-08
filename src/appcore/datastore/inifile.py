#!/usr/bin/env python3
'''
Datastore - INI File

Datastore stores information in an INI File.

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
import os
import configparser

# Local app modules
from appcore.datastore.datastore_base import DataStoreBaseClass
from appcore.conversion import to_json, from_json, set_value, DataType

# Imports for python variable type hints
from typing import Any
from threading import Lock as LockType
from multiprocessing.managers import ListProxy


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
# DataStoreINIFile Class Definition
#
###########################################################################
class DataStoreINIFile(DataStoreBaseClass):
    '''
    Class to describe the INI file datastore.

    The data is stored in an INI file.  This implementation is not efficient
    for many reads/writes as the file is read/written on each operation

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            filename: str = "",
            lock: LockType | None = None,
            data_expiry: ListProxy[Any] | None = None,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            filename (str): The path for the INI file
            lock (Lock): A SyncManager lock use to make actions atomic
            data_expiry (list): SyncManger List to store the expiry info
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            AssertionError:
                When a filename is not supplied
                When a SyncManager list is not provided to handle expiry
        '''
        assert filename, f"A file name is required for the INI file"
        assert lock, f"A lock is required to implement the INIFile datastore"
        assert isinstance(data_expiry, ListProxy), \
            f"A SyncManager list is required to implement the INIFile datastore"

        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__filename: str = filename
        self.__data_expiry: ListProxy[Any] = data_expiry
        self.__lock: LockType = lock

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # filename
    #
    @property
    def filename(self) -> str:
        ''' The path to the INI File '''
        return self.__filename


    ###########################################################################
    #
    # Maintenance Functions
    #
    ###########################################################################
    #
    # __read_ini
    #
    def __read_ini(self) -> configparser.ConfigParser:
        '''
        Read in the INI file

        Args:
            None

        Returns:
            configparser.ConfigParser: An instance of the config

        Raises:
            None
        '''
        _config = configparser.ConfigParser()
        _config.read(self.filename)
        return _config


    #
    # __write_ini
    #
    def __write_ini(
            self,
            config: configparser.ConfigParser | None = None
    ):
        '''
        Write in the INI file

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError:
                When a ConfigParser instance is not provided
        '''
        assert config, "A config must be supplied to write to INI file"
        assert isinstance(config, configparser.ConfigParser), \
            f"Config must be an instance of configparser.ConfigParser"

        with open(self.__filename, 'w') as configfile:
            config.write(configfile)


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

        # Begin the lock here - as we need to read/write the file
        self.__lock.acquire()

        _config = self.__read_ini()

        # Use a copy of the expiry list so we can change it during processing
        _changes = False
        for _entry in _sorted_expiry_list:
            # Extract the timestamp from the key
            _timestamp_str, _, _item = _entry.partition("__")
            _section, _, _name = _item.partition("__")
            _timestamp = set_value(_timestamp_str, DataType.INT, default=0)            

            # Stop processing if the timestamp is in the future
            if _now < _timestamp: break

            # Remove the entry
            if _config.has_option(_section, _name):
                _changes = True
                _config.remove_option(_section, _name)

            # If the section is empty, remove it
            if len(_config.options(_section)) == 0:
                _changes = True
                _config.remove_section(_section)

            # Remove the expiry entry
            self.__data_expiry.remove(_entry)

        if _changes: self.__write_ini(_config)

        # Release the lock
        self.__lock.release()


    ###########################################################################
    #
    # Data Access
    #
    ###########################################################################
    #
    # has_section
    #
    def has_section(
            self,
            section: str = ""
    ) -> bool:
        '''
        Check if the sectiom exists in the datastore

        Args:
            section (str): The section in which the item appears

        Returns:
            bool: True if the item exists, False otherwise

        Raises:
            None
        '''
        self.__item_maintenance()

        _config = self.__read_ini()
        return _config.has_section(section)


    #
    # has
    #
    def has(
            self,
            section: str = "",
            name: str = ""
    ) -> bool:
        '''
        Check if the item exists in the datastore

        Args:
            section (str): The section in which the item appears
            name (str): The name of the item to check

        Returns:
            bool: True if the item exists, False otherwise

        Raises:
            None
        '''
        self.__item_maintenance()

        _config = self.__read_ini()
        return _config.has_option(section, name)


    #
    # get
    #
    def get(
            self,
            section: str = "",
            name: str = "",
            default: Any = None,
            decrypt: bool = False
    ) -> Any:
        '''
        Get a value

        Args:
            section (str): The section in which the item appears
            name (str): The name of the item to get
            default (Any): Value to return if the item cannot be found
            decrypt (bool): If True, attempt to decrypt the value

        Returns:
            Any: The value of the item

        Raises:
            None
        '''
        self.__item_maintenance()

        _config = self.__read_ini()
        _value = _config.get(section, name, fallback=default)

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
            section: str = "",
            name: str = "",
            value: Any = None,
            encrypt: bool = False,
            timeout: int = 0
    ) -> None:
        '''
        Set a value for an item

        Args:
            section (str): The section in which the item appears
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
        '''
        assert isinstance(timeout, int), "Timeout value must be an integer"
        assert timeout >= 0, "Timeout value must be a postive integer"

        self.__item_maintenance()

        # Encrypt the value if required
        if encrypt:
            # Convert to JSON, Encrypt
            _json_value = to_json(value)
            value = self._encrypt(_json_value)

        # Set the value
        self.__lock.acquire()
        _config = self.__read_ini()
        if not section in _config:
            _config[section] = {}

        _config[section][name] = value
        self.__write_ini(_config)

        # Set the expiry info for the item if required
        if timeout > 0:
            _timestamp = self.timestamp(offset=timeout)

            # Append the item name to prevent duplicate keys/timestamps
            self.__data_expiry.append(f"{_timestamp}__{section}__{name}")

        self.__lock.release()


    #
    # delete
    #
    def delete(
            self,
            section: str = "",
            name: str = ""
    ) -> None:
        '''
        Delete an item from the datastore

        Args:
            section (str): The section in which the item appears
            name (str): The name of the item to delete

        Returns:
            Any: The value of the item

        Raises:
            None
        '''
        self.__item_maintenance()

        self.__lock.acquire()

        _config = self.__read_ini()
        _changes = False

        # Remove the entry
        if _config.has_option(section, name):
            _changes = True
            _config.remove_option(section, name)

        # If the section is empty, remove it
        if len(_config.options(section)) == 0:
            _changes = True
            _config.remove_section(section)

        # Write the config file if necessary
        if _changes: self.__write_ini(_config)

        self.__lock.release()


    #
    # delete_file
    #
    def delete_file(self ) -> None:
        '''
        Delete the INI File

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Remove any Expiry Data
        _sorted_expiry_list = sorted(self.__data_expiry)
        for _entry in _sorted_expiry_list:
            self.__data_expiry.remove(_entry)

        # Check if the INI File exists and delete it
        if os.path.exists(self.__filename):
            os.remove(self.__filename)


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
