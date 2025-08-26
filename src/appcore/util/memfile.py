#!/usr/bin/env python3
'''
MemFile - Store a file like object in memory

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
import io
import codecs
import crypto_tools.constants as ctc
import crypto_tools.fernet as ct_fernet

# Local app modules

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
# MemFile Class Definition
#
###########################################################################
class MemFile():
    '''
    Class to implement a memory based file.

    Attributes:
        bin_fp (Any): File pointer to the binary access for the file
        text_fp (Any): File pointer to the text access for the file
    '''
    #
    # __init__
    #
    def __init__(self):
        '''
        Initialises the instance.

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # The memory file will always be stored in binary mode
        self.bin_fp = io.BytesIO()

        # Create file pointers for reading/writing in text mode
        _writer = codecs.getwriter('utf-8')
        _reader = codecs.getreader('utf-8')
        self.text_fp = codecs.StreamReaderWriter(
            self.bin_fp,
            _reader,
            _writer
        )


    ###########################################################################
    #
    # Encryption/Decryption
    #
    ###########################################################################
    #
    # encrypt
    #
    def encrypt(
            self,
            key: bytes = b"",
            password: str = ""
    ) -> Any:
        '''
        Return a file pointer to an encrypted version of the file

        If a key is provided, that will be used to encrypt the file.  It must
        be a fernet encryption key.

        If a password is provided, an encryption key will be derived using 
        the password and the salt will be provided in the encryption file.

        If both a key and a password are provided, the key will be used, and
        the password will be ignored.

        If neither the key or password is provided, the key will be derived
        using an empty password and the salt will be provided in the
        encryption file.

        Args:
            key (bytes): Encryption key to use
            password (bytes): Password to use to derive a key

        Returns:
            Any: File pointer to encrypted version of the file

        Raises:
            AssertionError
                when key is not of type bytes
                when password is not of type string
        '''
        assert isinstance(password, str), "password must be a string"
        assert isinstance(key, bytes), "key must be bytes"

        # Create a new file
        _fp = io.BytesIO()

        # Save the current stream position, and read the file
        _current_seek = self.bin_fp.tell()
        self.bin_fp.seek(0)
        _data = self.bin_fp.read()
        self.bin_fp.seek(_current_seek)

        if key:
            _enc_key = key
        else:
            _salt, _enc_key = ct_fernet.derive_key(password=password)
            _fp.write(_salt)

        # Encrypt the data
        _enc_data = ct_fernet.encrypt(data=_data, key=_enc_key)

        # Write the data to the file
        _fp.write(_enc_data)

        # Reset to the start of the file so any reads will come from there
        _fp.seek(0)

        # Return a file pointer to the encrypted file
        return _fp


    #
    # decrypt
    #
    def decrypt(
            self,
            file: Any = None,
            key: bytes = b"",
            password: str = ""
    ) -> bool:
        '''
        Decrypt a file into the memory file

        If a key is provided, that will be use to decrypt the file.  It must be a 
        fernet encryption key.

        If a password is provided, a decryption key will be derived using the password
        and the salt will be assumed to be the header of the encrypted file.

        If both a key and a password are provided, the key will be used, and the password will
        be ignored.

        If neither the key or password is provided, the key will be derived using an empty 
        password and the salt will be assumed to be the header of the encrypted file.

        Args:
            file (Any): Pointer to file to decrypt - Must be opened in binary
                    read capable mode
            key (bytes): Encryption key to use
            password (bytes): Password to use to derive a key

        Returns:
            bool: True if successful, False otherwise or raise exception

        Raises:
            AssertionError
                when file is not provided
                when key is not of type bytes
                when password is not of type string

        '''
        assert file, "a binary file pointer must be provided"
        assert isinstance(password, str), "password must be a string"
        assert isinstance(key, bytes), "key must be bytes"

        # Read in the file contents
        _file_data = file.read()

        if key:
            _enc_data = _file_data
            _enc_key = key
        else:
            # Extract the salt from the start of the file
            if not (len(_file_data) > ctc.SALT_SIZE):
                return False

            _salt = _file_data[:ctc.SALT_SIZE]
            _enc_data = _file_data[ctc.SALT_SIZE:]

            _, _enc_key = ct_fernet.derive_key(salt=_salt, password=password)

        _data = str(ct_fernet.decrypt(data=_enc_data, key=_enc_key))

        # Go to the start of our file so we overwrite it
        self.bin_fp.seek(0)

        # fernet.decrypt decodes the data so we use the text writer
        self.text_fp.write(_data)

        # Reset to the start of the file so any reads will come from there
        self.bin_fp.seek(0)

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
