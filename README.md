# AppCore
Copyright (c) 2025 Jason Piszcyk

Core Components used to create an application.

To Be done -> ~~[![PyPI version](https://badge.fury.io/py/appcore.svg)](https://pypi.org/project/appcore/)~~
[![Build Status](https://github.com/JasonPiszcyk/AppCore/actions/workflows/python-app.yml/badge.svg)](https://github.com/JasonPiszcyk/AppCore/actions)

## Overview

**AppCore** provides reusable core components to help you build robust Python applications. It is designed to be used with multi-process and/or multithreaded apps, by providing access to resources that operate in these environments.

## Features

**AppCore** consists of a number of sub-modules, being:
- Multiprocessing
  - A generalised Task interface proving multiprocessing via Process and Threads
    - Task Lifecycle management including starting, stopping and watchdog processing to ensure task state
  - Support for communication between Tasks via:
    - Queues
  - Support for Task synchronisation via:
    - Events
    - Barriers
  - Support for shared locking between tasks via:
    - Locks
- Logging
  - Simplified logging interface
- Datastores
  - Local - Data is available in process via shared global variables
  - System - Data is shareable amongst multiple tasks
  - Redis - Data is shareable via the external datastore Redis
  - INIFile - Data is shareable via INI Files
- Scheduler
  - A task scheduler, supporting:
    - Scheduling of tasks on a regular interval (eg every 60 seconds)
    - Scheduling of tasks at a specific time (eg at 12:30 pm)
- Telemetry
  - A telemetry module that exposes information via a web server

## Installation

Module has not been published to PyPi yet.  Install via:
```bash
pip install "appcore @ git+https://github.com/JasonPiszcyk/AppCore
```

## Requirements

- Python >= 3.12

## Dependencies

- requests
- urllib3
- pytest
- redis

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
