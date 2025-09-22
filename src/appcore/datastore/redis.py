#!/usr/bin/env python3
'''
Datastore - Redis

Datastore stores information in a shared SyncManager dictionary.

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
from __future__ import annotations

# Shared variables, constants, etc

# System Modules
from redis import Redis

# Local app modules
from appcore.datastore.datastore_base import DataStoreBaseClass
import appcore.datastore.exception as exception
from appcore.conversion import to_json, from_json

# Imports for python variable type hints
from typing import Any


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
# DataStoreRedis Class Definition
#
###########################################################################
class DataStoreRedis(DataStoreBaseClass):
    '''
    Class to describe the Redis datastore.

    The data is stored in Redis

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
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
        # Extract the args for the redis connection (prefixed with 'redis_')
        _redis_args = {}
        _new_kwargs = {}

        for _key, _value in kwargs.items():
            if _key.find("redis_") == 0:
                _new_key = _key.replace("redis_", "")
                _redis_args[_new_key] = _value

            else:
                # Add this to the remaining kwargs
                _new_kwargs[_key] = _value

        super().__init__(*args, **_new_kwargs)

        if not "port" in _redis_args: _redis_args["port"] = 6379
        _redis_args["decode_responses"] = True

        # Private Attributes
        self.__redis_args = _redis_args
        self.__redis: Redis | None = None

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # connected
    #
    @property
    def connected(self) -> bool:
        ''' Indicator if connected to Redis '''
        return True if self.__redis else False


    ###########################################################################
    #
    # Redis Connectivity
    #
    ###########################################################################
    #
    # connect
    #
    def connect(self):
        '''
        Connect to a redis datastore

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self.__redis: Redis | None = Redis(**self.__redis_args)

        # Try an action on redis to see if connection works
        # Should raise an exception if connection doesn't work
        self.__redis.exists("__connection_test__")


    #
    # disconnect
    #
    def disconnect(self):
        '''
        Disconnect from a redis datastore

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self.__redis: Redis | None = None


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
        Perform maintenance on items

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Nothing to do as Redis handles item expiry
        pass


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
            DataStoreRedisNotConnected
                When not connected
        '''
        if not self.__redis:
            raise exception.DataStoreRedisNotConnected(
                "A connection has not been established to Redis"
            )

        self.__item_maintenance()

        # 'exists' returns a number and our return is boolean, so be explicit
        if self.__redis.exists(name):
            return True
        else:
            return False


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
            DataStoreRedisNotConnected
                When not connected
        '''
        if not self.__redis:
            raise exception.DataStoreRedisNotConnected(
                "A connection has not been established to Redis"
            )

        self.__item_maintenance()
        if not self.has(name): return default

        # Check the type of the value
        _value_type = self.__redis.type(name)
        if _value_type == "string":
            # String
            _value = str(self.__redis.get(name))

        else:
            raise TypeError(f"Redis variable type not supported: {_value_type}")

        if decrypt:
            _decrypted_value = self._decrypt(_value)
        else:
            _decrypted_value = _value

        return from_json(_decrypted_value)


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
            DataStoreRedisNotConnected
                When not connected
            DataStoreDotNameError:
                When the dot name is a low part of a hierarchy
        '''
        assert isinstance(timeout, int), "Timeout value must be an integer"
        assert timeout >= 0, "Timeout value must be a positive integer"

        if not self.__redis:
            raise exception.DataStoreRedisNotConnected(
                "A connection has not been established to Redis"
            )

        self.__item_maintenance()

        # Check on dot names
        if self._dot_names:
            _keys = list(self.__redis.scan_iter())
            if not self._check_dot_name(keys=_keys, name=name):
                raise exception.DataStoreDotNameError(
                    "Value cannot be stored in a intermediate dot level name"
                )

        # Always store values in JSON format
        _json_value = to_json(value)

        # Encrypt the value if required
        if encrypt:
            # Convert to JSON, Encrypt
            _encrypted_value = self._encrypt(_json_value)

        else:
            _encrypted_value = _json_value

        self.__redis.set(name, _encrypted_value)

        # Set the expiry value
        if timeout: 
            self.__redis.expire(name, timeout)


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
            DataStoreRedisNotConnected
                When not connected
        '''
        if not self.__redis:
            raise exception.DataStoreRedisNotConnected(
                "A connection has not been established to Redis"
            )

        self.__item_maintenance()
        if not self.has(name): return

        # 'delete' should raise an exception if there is a problem
        self.__redis.delete(name)


    #
    # list
    #
    def list(
            self,
            prefix: str = ""
    ) -> list:
        '''
        Return a list of keys in the datastore

        Args:
            prefix (str): Will try to match any keys beginning with this str.

        Returns:
            list: The list of items

        Raises:
            DataStoreRedisNotConnected
                When not connected
       '''
        if not self.__redis:
            raise exception.DataStoreRedisNotConnected(
                "A connection has not been established to Redis"
            )

        self.__item_maintenance()

        _key_list = []

        for _key in self.__redis.scan_iter(match=f"{prefix}*"):
            _key_list.append(_key)

        return _key_list


    ###########################################################################
    #
    # Export Functions
    #
    ###########################################################################
    #
    # export_to_json
    #
    def export_to_json(self) -> str:
        '''
        Export the data store to JSON

        Args:
            None

        Returns:
            str: The JSON string

        Raises:
            None
        '''
        # Convert to JSON
        raise NotImplementedError(
            "Export to JSON not support for Redis Datastore"
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
