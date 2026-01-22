# AppCore
Copyright (c) 2025 Jason Piszcyk

Core Components for other 'App*' modules

<!-- 
Not yet Published to PyPi
[![PyPI version](https://badge.fury.io/py/appcore.svg)](https://pypi.org/project/appcore/)
[![Build Status](https://github.com/JasonPiszcyk/AppCore/actions/workflows/python-app.yml/badge.svg)](https://github.com/JasonPiszcyk/AppCore/actions)
 -->


## Overview


**AppCore** provides core components for the 'App' series of modules.


## Features


**AppCore** consists of a number of sub-modules, being:
- [Conversion](#conversion-usage)
  - A collection of conversion functions
    - set_value - Ensure a value is set to the specific DataType
    - get_value_type - Get the data type of a value
    - to_pickle, from_pickle - Convert data to and from python Pickle
    - to_json, from_json - Convert data to and from JSON
    - from_base64, from_base64 - Convert data to and from base 64
- [Helpers](#helpers-usage)
  - A collection of general functions
    - timestamp - Generate a timestamp
- [MemFile](#memfile-usage)
  - An implementation of a 'file' in memory


## Installation

Module has not been published to PyPi yet.  Install via:
```bash
pip install "appcore @ git+https://github.com/JasonPiszcyk/AppCore"
```

## Requirements

Python >= 3.8

> [!NOTE]
> The module has been tested against Python 3.8 and 3.14.


## Dependencies

- pytest
- "crypto_tools @ git+https://github.com/JasonPiszcyk/CryptoTools"


## Usage

### DataTypes

An enumeration (Enum) of data types is defined containing the following datatypes:

| DataType | Python Datatype |
| - | - |
| DataType.NONE | *NOT SET* |
| DataType.INT | int |
| DataType.INTEGER | int |
| DataType.FLOAT | float |
| DataType.STR | str |
| DataType.STRING | str |
| DataType.BOOL | bool |
| DataType.BOOLEAN | bool |
| DataType.DICT | dict |
| DataType.DICTIONARY | dict |
| DataType.LIST | list |
| DataType.TUPLE | tuple/set |
| DataType.UUID | UUID |
| DataType.UUID1 | UUID Version 1 |
| DataType.UUID3 | UUID Version 2 |
| DataType.UUID4 | UUID Version 3 |
| DataType.UUID5 | UUID Version 4 |

The value of the DataType Enum is the name in lower case. This can be used to store additional type information when converting to JSON.


### <a id="conversion-usage"></a>Conversion


**set_value(** data=None, type=DataType.STRING, default=None **)**

> Convert data to the specified type, using the default value if the conversion fails.

> | Argument | Description |
> | - | - |
> | **data** (Any) | The data to be converted. |
> | **type** (Any) | The type to convert 'data' to. Default is DataType.STRING (a python 'str'). |
> | **default** (Any) | The value to return of the conversion fails. Defaults to None to make it possible to determine if the conversion failed. |


**get_value_type(** data=None, json_only=False **)**

> Return the Datatype of the supplied value. Will raise 'TypeError' if the DataType is invalid or cannot be identified.

> | Argument | Description |
> | - | - |
> | **data** (Any) | The data to be 'typed'. |
> | **json_only** (bool) | If True, the valid data types are restricted to typesw supported by JSON. |


**to_pickle(** data=None, protocol=5, fix_imports=True **)**

> Return the data converted to a python pickle.

> | Argument | Description |
> | - | - |
> | **data** (Any) | The data to be converted |
> | **protocol** (int) | The pickle protocol to use.  Default = 5 (highest supported protocol). |
> | **fix_imports** (bool) | If protocol is less than 3, pickle will try to map the new Python 3 names to the old module names used in Python 2, so that the pickle data stream is readable with Python 2.  Default = True. |


**from_pickle(** data=None, fix_imports=True, encoding="ASCII, errors="strict" **)**

> Return the data converted from a python pickle.

> | Argument | Description |
> | - | - |
> | **data** (Any) | The data to be converted |
> | **fix_imports** (bool) | If protocol is less than 3, pickle will try to map the new Python 3 names to the old module names used in Python 2, so that the pickle data stream is readable with Python 2.  Default = True. |
> | **encoding** (str) | Used to determine how to decode 8-bit string instances pickled by Python 2.  Default = "ASCII". |
> | **errors** (str) | Used to determine how to decode 8-bit string instances pickled by Python 2.  Default = "strict". |


**to_json(** data=None, skip_invalid=False, container=False **)**

> Return the data converted to JSON.

> | Argument | Description |
> | - | - |
> | **data** (Any) | The data to be converted |
> | **skip_invalid** (bool) | Skip objects that cannot be serialised rather than raising TypeError.  Default = False. |
> | **fixcontainer_imports** (bool) | If true, the export contains an outer container identifying the top level data type.  Default = False |


**from_json(** data=None, container=False **)**

> Return the data converted from JSON.

> | Argument | Description |
> | - | - |
> | **data** (Any) | The data to be converted |
> | **fixcontainer_imports** (bool) | If true, the import expects an outer container identifying the top level data type.  Default = False |


**to_base64(** data=b"" **)**

> Return a base64 encoded string from a byte array

> | Argument | Description |
> | - | - |
> | **data** (Any) | The data (in byte format) to be converted to a base64 encoded string |


**from_base64(** data="" **)**

> Return a byte array from a base64 encoded string

> | Argument | Description |
> | - | - |
> | **data** (Any) | The data (as a base64 encoded string) to be converted to a byte array |


### <a id="helpers-usage"></a>Helpers


**timestamp(** offset=0 **)**

> Return a timestamp (in seconds) since the epoch to now, with an optional offset.

> | Argument | Description |
> | - | - |
> | **offset** (int) | Number of seconds to offset the timestamp by. Default = 0. |


### <a id="memfile-usage"></a>MemFile

#### *class* AppCore.**MemFile**()

Class to implement a memory based file.


| Property | Description |
| - | - |
| **text_fp** (Any) | Pointer to the memory file to read/write in 'text' mode |
| **bin_fp** (Any) | Pointer to the memory file to read/write in 'binary' mode |

**encrypt(** key=b"", password="" **)**

> Return a file pointer to an encrypted version of the file. The file pointer will be opened in binary read/write mode.
> If a key is provided, that will be used to encrypt the file.  It must be a fernet encryption key.
> If a password is provided, an encryption key will be derived using the supplied password.
> If both a key and a password are provided, the key will be used, and the password will be ignored.
> If neither the key or password is provided, the key will be derived using an empty password.
> [!IMPORTANT]
> The memfile should only be written in binary format if it is going to be encrypted.  The encryption process reads the file in binary mode so additional characters may be included in the encrypted file if text mode has been used.

> | Argument | Description |
> | - | - |
> | **key** (bytes) | Encryption key to use. Default = b"". |
> | **password** (str) | assword to use to derive a key. Default = "". |


**decrypt(** file=None, key=b"", password="" **)**

> Decrypt the provided file. Return True if OK. The file is then available via the MemFile 'text_fp', and 'bin_fp' file pointers.
> If a key is provided, that will be used to decrypt the file.  It must be a fernet encryption key.
> If a password is provided, a decryption key will be derived using the password and the salt will be assumed to be in the header of the encrypted file.
> If both a key and a password are provided, the key will be used, and the password will be ignored.
> If neither the key or password is provided, the key will be derived using an empty password and the salt will be assumed to be the header of the encrypted file.

> | Argument | Description |
> | - | - |
> | **file** (Any) | File pointer to encrypted version of the file. |
> | **key** (bytes) | Encryption key to use. Default = b"". |
> | **password** (str) | assword to use to derive a key. Default = "". |

```python
# Example useage of MemFile
from appcore.memfile import MemFile

# Create a text file in memory
text_file = MemFile()

text_file.text_fp.write("A basic line of text\n")
text_file.text_fp.write("Another line of text\n")

# Set the pointer to the start of the file and read the file (text mode)
text_file.text_fp.seek(0)
line = text_file.text_fp.readline()   # line = "A basic line of text\n"

# Create a binary file in memory
bin_file = MemFile()

bin_file.bin_fp.write(b"basic binary info")

# Set the pointer to the start of the file and read the file (binary mode)
bin_file.bin_fp.seek(0)
file_bytes = bin_file.bin_fp.read()  # file_bytes = b"basic binary info"

# Get a filepointer to an encrypted version of the file
enc_fp = bin_file.encrypt(password="somepassword")

# Set the pointer to the start of the file and read the file (binary mode)
enc_fp.seek(0)
enc_bytes = enc_fp.read()  # enc_bytes = <encrypted bytes>

# Create a new memfile
new_file = MemFile()

# Set the pointer to the start of the file and read the file (text mode)
new_file.bin_fp.seek(0)
new_line = new_file.bin_fp.readline()   # new_line = b""

# Set the pointer to the start and decrypt the encrypted file into new_file
enc_fp.seek(0)
new_file.decrypt(file=enc_fp, password="somepassword")

# Set the pointer to the start of the file and read the file (text mode)
new_file.bin_fp.seek(0)
new_bytes = new_file.bin_fp.read()   # new_bytes = b"basic binary info"
```


## Development

1. Clone the repository:
    ```bash
    git clone https://github.com/JasonPiszcyk/AppCore.git
    cd AppCore
    ```
2. Install dependencies:
    ```bash
    pip install -e .[dev]
    ```

## Running Tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please submit issues or pull requests via [GitHub Issues](https://github.com/JasonPiszcyk/AppCore/issues).

## License

GNU General Public License

## Author

Jason Piszcyk  
[Jason.Piszcyk@gmail.com](mailto:Jason.Piszcyk@gmail.com)

## Links

- [Homepage](https://github.com/JasonPiszcyk/AppCore)
- [Bug Tracker](https://github.com/JasonPiszcyk/AppCore/issues)
