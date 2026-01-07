# AppCore
Copyright (c) 2025 Jason Piszcyk

Core Components for other 'App*' modules

<!-- 
Not yet Published to PyPi
[![PyPI version](https://badge.fury.io/py/appcore.svg)](https://pypi.org/project/appcore/)
[![Build Status](https://github.com/JasonPiszcyk/AppCore/actions/workflows/python-app.yml/badge.svg)](https://github.com/JasonPiszcyk/AppCore/actions)
 -->

## Overview

**AppCore** provides reusable core components for the 'App' series of modules.

## Features

**AppCore** consists of a number of sub-modules, being:
- Conversion
  - A collection of conversion functions
    - set_value - Ensure a value is set to the specific DataType
    - get_value_type - Get the data type of a value
    - to_json, from_json - Convert data to and from JSON
    - from_base64, from_base64 - Convert data to and from base 64
- Helpers
  - A collection of general functions
    - timestamp - Generate a timestamp


## Installation

Module has not been published to PyPi yet.  Install via:
```bash
pip install "appcore @ git+https://github.com/JasonPiszcyk/AppCore"
```

## Requirements

- Python >= 3.8

## Dependencies

- pytest
- "crypto_tools @ git+https://github.com/JasonPiszcyk/CryptoTools"

## Usage

```python
import appcore
# Example usage of AppCore components
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
