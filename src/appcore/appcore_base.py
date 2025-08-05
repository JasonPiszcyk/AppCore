#!/usr/bin/env python3
'''
AppCore module base class

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
from appcore.validation import is_valid_log_level_string

# Imports for python variable type hints
from logging import Handler as HandlerType
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
CONSOLE_HANDLER_NAME = "TO_CONSOLE"

###########################################################################
#
# AppCoreModuleBase Class Definition
#
###########################################################################
class AppCoreModuleBase():
    '''
    The base class for AppCore modules.

    Modules can use this as a base class to provide common functionality    

    Attributes:
        log_level (str): The log level to use when configuring logging
        log_file (str): Path of file to log to.  If not set, will not log
            to file
        log_to_console (bool): Write the logging out to the standard output 
            device (usually stdout)
    '''

    #
    # __init__
    #
    def __init__(
            self,
            log_level: str = LoggingLevel.INFO.value,
            log_file: str = "",
            log_to_console: bool = False,
    ):
        '''
        Initialises the instance.

        Args:
            log_level (str): The log level to use when configuring logging
            log_file (str): Path of file to log to.  If not set, will not log
                to file
            log_to_console (bool): Write the logging out to the standard output 
                device (usually stdout)

        Returns:
            None

        Raises:
            None
        '''
        # Private Attributes
        self._log_level: str = LoggingLevel.INFO.value
        self._log_file: str = ""
        self._log_to_console: bool = False

        # Attributes

        #
        # Set up Logging
        #
        self.logger: Logger = logging.getLogger(self.__class__.__name__)

        # Remove existing handlers (eg stderr)
        for _handler in self.logger.handlers.copy():
            self.logger.removeHandler(_handler)

        # Set the log properties (will update logging config)
        self.log_level = log_level
        self.log_file = log_file
        self.log_to_console = log_to_console


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # log_level
    #
    @property
    def log_level(self) -> str:
        ''' The log level for the module '''
        return self._log_level


    @log_level.setter
    def log_level(self, value: str = "") -> None:
        ''' The log level for the module '''
        self.logging_set_level(logger=self.logger, log_level=value)
        self._log_level = value


    #
    # log_file
    #
    @property
    def log_file(self) -> str:
        ''' The log file for the module '''
        return self._log_file


    @log_file.setter
    def log_file(self, value: str = "") -> None:
        ''' The log file for the module '''
        assert isinstance(value, str), f"'{value}' must be a string"

        _old_handler_name = self._log_file
        self._log_file = value

        if not self._log_file and _old_handler_name:
            # Remove the old handler if it exists
            for _handler in self.logger.handlers.copy():
                if _handler.name == _old_handler_name:
                    self.logger.removeHandler(_handler)

        if self._log_file:
            _ = self.logging_set_file(
                logger=self.logger,
                filename=self._log_file
            )


    #
    # log_to_console
    #
    @property
    def log_to_console(self) -> bool:
        ''' Should log output be sent to console '''
        return self._log_to_console


    @log_to_console.setter
    def log_to_console(self, value: bool = False) -> None:
        ''' Should log output be sent to console '''
        assert isinstance(value, bool), f"'{value}' must be a boolean"

        self._log_to_console = value
        if not self._log_to_console:
            # Remove the old handler if it exists
            for _handler in self.logger.handlers.copy():
                if _handler.name == CONSOLE_HANDLER_NAME:
                    self.logger.removeHandler(_handler)

        else:
            _ = self.logging_to_console(
                logger=self.logger
            )


    ###########################################################################
    #
    # Logging resource methods
    #
    ###########################################################################
    #
    # logging_set_level
    #
    @staticmethod
    def logging_set_level(
            logger: Logger | None = None,
            log_level: str = "info"
    ) -> None:
        '''
        Validate the log level and set it in the logger

        Args:
            logger (Logger): The logging instance to update
            log_level (str): The log level to set on the logger

        Returns:
            None

        Raises:
            AssertionError:
                When a logger instance has not been supplied
                When the log level is not valid
        '''
        assert logger, f"Logging instance not supplied."

        assert is_valid_log_level_string(log_level), \
            f"'{log_level}' is not in {list([_e.value for _e in LoggingLevel])}"

        logger.setLevel(LoggingLevel(log_level).level)


    #
    # logging_set_file
    #
    @staticmethod
    def logging_set_file(
            logger: Logger | None = None,
            filename: str = ""
    ) -> HandlerType:
        '''
        Set the logger to output to a file

        Args:
            logger (Logger): The logging instance to update
            filename (str): The name of the file to log to

        Returns:
            Handler: The handler for log file

        Raises:
            AssertionError:
                When a logger instance has not been supplied
                When the log file name has not been supplied
        '''
        assert logger, f"Logging instance not supplied."
        assert filename, f"Logging file name not supplied."

        _log_format = logging.Formatter(
            "%(asctime)s: [%(name)s] %(levelname)s: %(message)s"
        )

        # Set up the handler to rotate log files
        _log_file_handler = logging.handlers.TimedRotatingFileHandler(
            filename,
            when="W6",
            atTime=datetime.time(0, 0, 0),
            backupCount=5
        )

        # Set the log format and add the handler
        _log_file_handler.setFormatter(_log_format)
        _log_file_handler.name=filename
        logger.addHandler(_log_file_handler)

        # Return the handler in case it needs to be stored
        return _log_file_handler


    #
    # logging_to_console
    #
    @staticmethod
    def logging_to_console(
            logger: Logger | None = None,
    ) -> HandlerType:
        '''
        Set the logger to output to the console

        Args:
            logger (Logger): The logging instance to update

        Returns:
            Handler: The handler for output stream

        Raises:
            AssertionError:
                When a logger instance has not been supplied
        '''
        assert logger, f"Logging instance not supplied."

        # Set up the log format for logging to the screen/console
        _log_format = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
        )

        # Setup the handler to stdout
        _log_console_handler = logging.StreamHandler()

        # Set the log format and add the handler
        _log_console_handler.setFormatter(_log_format)
        _log_console_handler.name = CONSOLE_HANDLER_NAME
        logger.addHandler(_log_console_handler)

        # Return the handler in case it needs to be stored
        return _log_console_handler


    ###########################################################################
    #
    # Generic Helper Functions
    #
    ###########################################################################
    #
    # timestamp
    #
    @staticmethod
    def timestamp(offset: int = 0):
        '''
        Create a timestamp (in seconds) since the epoch to now

        Args:
            offset (int): Number of seconds to offset the timestamp by

        Returns:
            int: The number of seconds since the epoch to now, +/- offset

        Raises:
            AssertionError:
                When the offset is not an integer value
        '''
        assert isinstance(offset, int)

        # Get the current time
        _now = datetime.datetime.now(datetime.timezone.utc)

        # Return the timestamp
        return int(_now.timestamp()) + offset


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
