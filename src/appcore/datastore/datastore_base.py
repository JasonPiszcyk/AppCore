#!/usr/bin/env python3
'''
Datastore - Base Class

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
import crypto_tools
from crypto_tools.constants import ENCODE_METHOD

# Local app modules
from appcore.appcore_base import AppCoreModuleBase
from appcore.conversion import to_json
import appcore.datastore.exception as exception

# Imports for python variable type hints
from typing import Any
from multiprocessing.managers import DictProxy


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
# DataStoreBaseClass Class Definition
#
###########################################################################
class DataStoreBaseClass(AppCoreModuleBase):
    '''
    The base class to be use for all datastore classeses

    Attributes:
        dot_names (bool) [ReadOnly]: If true, dots in item names indicate a
            hierachy.
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            password: str = "",
            salt: bytes = b"",
            security: str = "high",
            dot_names: bool = False,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            password: (str): Password used to derive the encryption key - A
                random password will be used if none provided
            salt: (bytes): Binary string containing the salt - A default
                salt will be used in none provided
            security (str): Determines the computation time of the key.  Must
                be one of "low", "medium", or "high"
            dot_names (bool): If True, use dot names to create a hierarchy of
                values for this data store.  If False, dots in names are
                treated as normal characters
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        super().__init__(*args, **kwargs)

        # Private Attributes
        if not salt:
            salt = b"a%Z\xe9\xc3N\x96\x82\xc5|#e\xfd1b&"

        self.logger.debug("Creating Encryption Key")
        self._salt, self._key = crypto_tools.fernet.derive_key(
            salt=salt, password=password, security=security
        )
        self.logger.debug("Encryption Key has been created")

        self._dot_names = dot_names

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # dot_names
    #
    @property
    def dot_names(self) -> bool:
        ''' If True, dots in names are used to create hierarchy '''
        return self._dot_names


    ###########################################################################
    #
    # Storage Methods
    #
    ###########################################################################
    #
    # _encrypt
    #
    def _encrypt(
            self,
            value: str = ""
    ) -> str:
        '''
        Encrypt the value
            
        Args:
            value (str): A value to be encrypted. Should generally be a JSON
                string.
        
        Returns:
            string: The encrypted string

        Raises:
            None
        '''
        # Check the type of the value provided
        if not isinstance(value, str):
            raise TypeError(
                f"Cannot encrypt data type: {type(value)}"
            )

        _byte_data = str(value).encode(ENCODE_METHOD)
        _encrypted_string = crypto_tools.fernet.encrypt(
            data=_byte_data,
            key=self._key
        ).decode()

        if not _encrypted_string:
            return ""
        else:
            return _encrypted_string


    #
    # _decrypt
    #
    def _decrypt(
            self,
            value: str = ""
    ) -> str:
        '''
        Decrypt the value
            
        Args:
            value (str): A value to be decrypted
        
        Returns:
            string: The decrypted string

        Raises:
            None
        '''    
        _byte_data = str(value).encode(ENCODE_METHOD)
        _decrypted_string = crypto_tools.fernet.decrypt(
            data=_byte_data,
            key=self._key
        )

        if not _decrypted_string:
            return ""
        else:
            return str(_decrypted_string)

    ###########################################################################
    #
    # Dot Name Handling
    #
    ###########################################################################
    def _check_dot_name(
            self,
            keys: list = [],
            name: str = ""
    ) -> bool:
        '''
        Check the Dot name to ensure a value isn't going to be stored in a
        sub-level name
            
        Args:
            keys (list): A list of keys in the datastore
            name (str): The name to check
        
        Returns:
            bool: True if the name is OK, False otherwise

        Raises:
            None
        '''
        assert isinstance(keys, list), "Keys must be a list of key names"
        assert name, "A name is required to check"

        # Go through the whole list looking for the name
        for _key in sorted(keys):
            if name == _key: continue

            # Look for a name trying to add a branch where a value is stored
            if str(name).find(f"{_key}.") == 0:
                return False

            # Look for a name trying to add a value where a branch is
            if str(_key).find(f"{name}.") == 0:
                return False


        return True


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
