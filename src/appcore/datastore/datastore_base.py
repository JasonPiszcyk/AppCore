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
# DataStoreBaseClass Class Definition
#
###########################################################################
class DataStoreBaseClass(AppCoreModuleBase):
    '''
    The base class to be use for all datastore classeses

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            password: str = "",
            salt: bytes = b"",
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

        self._salt, self._key = crypto_tools.fernet.derive_key(
            salt=salt, password=password
        )

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################


    ###########################################################################
    #
    # Storage Methods
    #
    ###########################################################################
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
# In case this is run directly rather than imported...
#
###########################################################################
'''
Handle case of being run directly rather than imported
'''
if __name__ == "__main__":
    pass
