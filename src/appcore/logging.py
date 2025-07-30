#!/usr/bin/env python3
'''
logging - Logging functions

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
from logging import Logger
import logging.handlers
import datetime

# Local app modules

# Imports for python variable type hints
from appcore.typing import LoggingLevel


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
# Module
#
###########################################################################
#
# configure_logger
#
def configure_logger(
        name: str = "",
        log_level: str = "info",
        log_file: str = "",
        to_console: bool = True,
) -> Logger:
    '''
    Configure the logging instance

    Args:
        name (str): A label for the logger
        log_level (str): The log level to use when configuring logging
        log_file (str): Path of file to log to.  If not set, will not log
            to file
        to_console (bool): Write the logging out to the standard output 
            device (usually stdout)

    Returns:
        Logger

    Raises:
        None
    '''
    # If the name is not configureed, log as an unknown logger
    if not name: name = "UNKNOWN"

    # Make sure the log level is valid
    _log_levels: list = list([_entry.value for _entry in LoggingLevel])
    assert log_level in _log_levels, f"'{log_level}' is not in {_log_levels}"

    # Set up the logger
    _logger = logging.getLogger(name)

    # Remove existing handlers (eg stderr)
    for _handler in _logger.handlers.copy():
        _logger.removeHandler(_handler)

    # Log level
    _logger.setLevel(LoggingLevel(log_level).level)

    if log_file:
        # Set up the log format for writing to a file
        _log_format = logging.Formatter(
            "%(asctime)s: %(levelname)s: %(message)s"
        )

        # Set up the handler to rotate log files
        _log_handler = logging.handlers.TimedRotatingFileHandler(
            log_file,
            when="W6",
            atTime=datetime.time(0, 0, 0),
            backupCount=5
        )

        # Set the log format and add the handler
        _log_handler.setFormatter(_log_format)
        _logger.addHandler(_log_handler)


    if to_console:
        # Set up the log format for logging to the screen/console
        _log_format = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")

        # Setup the handler to stdout
        # _log_handler = logging.StreamHandler(sys.stdout)
        _log_handler = logging.StreamHandler()

        # Set the log format and add the handler
        _log_handler.setFormatter(_log_format)
        _logger.addHandler(_log_handler)

    return _logger


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
