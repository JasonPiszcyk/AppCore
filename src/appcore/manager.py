#!/usr/bin/env python3
'''
The MultiTask task manager.  This should be used to create any resources.

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
from multiprocessing import get_context
import logging

# Local app modules
from appcore.appcore_base import AppCoreModuleBase
from appcore.validation import is_valid_log_level_string
from appcore.multitasking.task import Task, TaskType
from appcore.multitasking.task_queue import TaskQueue
from appcore.datastore.local import DataStoreLocal

# Imports for python variable type hints
from typing import Callable
from multiprocessing.context import SpawnContext as SpawnContextType
from multiprocessing.managers import SyncManager as SyncManagerType
from threading import Lock as LockType
from threading import Barrier as BarrierType
from threading import Event as EventType
from appcore.typing import KeywordDictType, LoggingLevel


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
# AppCoreManager Class Definition
#
###########################################################################
class AppCoreManager(AppCoreModuleBase):
    '''
    Class to describe the AppCore Manager.

    The AppCore Manager is used to create any required resources

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
        super().__init__(*args, **kwargs)

        # Private Attributes
        # Delay setting context/manager until they are used.
        self.__context: SpawnContextType | None = None
        self.__manager: SyncManagerType | None = None

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # context
    #
    @property
    def context(self) -> SpawnContextType | None:
        ''' The context used by the multiprocessing library '''
        return self.__context


    #
    # manager
    #
    @property
    def manager(self) -> SyncManagerType | None:
        ''' The multiprocessing SyncManger instance to use '''
        return self.__manager


    ###########################################################################
    #
    # Resource Creation Methods
    #
    ###########################################################################
    #
    # _get_manager
    #
    def _get_manager(self) -> SyncManagerType:
        '''
        Get the Multiprocessing manager (or create it if not set)

        Args:
            None

        Returns:
            SyncManagerType

        Raises:
            None
        '''
        if not self.__context:
            self.logger.debug(f"Context not set. Setting.")
            self.__context: SpawnContextType | None = get_context("spawn")

        if not self.__manager:
            self.logger.debug(f"Manager not yet created. Creating.")
            self.__manager: SyncManagerType | None = self.__context.Manager()

        return self.__manager


    #
    # Thread
    #
    def Thread(
            self,
            name: str = "",
            target: Callable | None = None,
            kwargs: KeywordDictType = {},
            stop_function: Callable | None = None,
            stop_kwargs: KeywordDictType = {},
     ) -> TaskType:
        '''
        Create a thread based Task

        Args:
            name (str): An identifier for the task
            target (Callable): Function to run in the new thread/process
            kwargs (dict): Arguments to pass to the target function
            stop_function (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass the stop function

        Returns:
            TaskType: The task created (as a thread based task)

        Raises:
            None
        '''
        self.logger.debug(f"Creating thread ({name})")

        # Ensure the multiprocessing manager has been created
        # Also ensures the instance attributes __context and __manager are set
        _ = self._get_manager()

        return Task(
            name=name,
            context=self.__context,
            manager=self.__manager,
            target=target,
            target_kwargs=kwargs,
            stop_function=stop_function,
            stop_kwargs=stop_kwargs,
            task_type="thread",
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console
        )


    #
    # Process
    #
    def Process(
            self,
            name: str = "",
            target: Callable | None = None,
            kwargs: KeywordDictType = {},
            stop_function: Callable | None = None,
            stop_kwargs: KeywordDictType = {},
     ) -> TaskType:
        '''
        Create a process based Task

        Args:
            name (str): An identifier for the task
            target (Callable): Function to run in the new thread/process
            kwargs (dict): Arguments to pass to the target function
            stop_function (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass the stop function

        Returns:
            TaskType: The task created (as a process based task)

        Raises:
            None
        '''
        self.logger.debug(f"Creating process ({name})")

        # Ensure the multiprocessing manager has been created
        # Also ensures the instance attributes __context and __manager are set
        _ = self._get_manager()

        return Task(
            name=name,
            context=self.__context,
            manager=self.__manager,
            target=target,
            target_kwargs=kwargs,
            stop_function=stop_function,
            stop_kwargs=stop_kwargs,
            task_type="process",
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console
        )


    #
    # Event
    #
    def Event(self) -> EventType:
        '''
        Create an event (using the multiprocessing manager)

        Args:
            None

        Returns:
            Event: An event

        Raises:
            None
        '''
        self.logger.debug(f"Creating event")

        # Ensure the multiprocessing manager has been created
        _manager = self._get_manager()

        return _manager.Event()


    #
    # Lock
    #
    def Lock(self) -> LockType:
        '''
        Create a Lock (using the multiprocessing manager)

        Args:
            None

        Returns:
            Lock: A lock

        Raises:
            None
        '''
        self.logger.debug(f"Creating lock")

        # Ensure the multiprocessing manager has been created
        _manager = self._get_manager()

        return _manager.Lock()


    #
    # Barrier
    #
    def Barrier(
            self,
            parties: int = 2,
            action: Callable | None = None,
            timeout: float = 5.0
    ) -> BarrierType:
        '''
        Create a Barrier (using the multiprocessing manager)

        Args:
            parties (int): Number of parties required to wait before the
                barrier is lifted
            action (Callable): Function to be executed (by one of the
                waiting parties) when the barrier is lifted
            timeout (float): Time to wait for the barrier to be lifted

        Returns:
            Barrier: A Barrier

        Raises:
            None
        '''
        self.logger.debug(f"Creating barrier")

        # Ensure the multiprocessing manager has been created
        _manager = self._get_manager()

        return _manager.Barrier(
            parties=parties,
            action=action,
            timeout=timeout
        )


    #
    # Queue
    #
    def Queue(
            self,
            message_handler: Callable | None = None
    ) -> TaskQueue:
        '''
        Create a Queue (using the multiprocessing manager)

        Args:
            message_handler (Callable): Callable to process the received
                message. The message handler should accept 1 parameter:
                    frame - An instance of MessageFrame
                The message handler can return a response.  This will be
                place on the queue specified as 'response_queue' in the frame
                properties.

        Returns:
            TaskQueue: An instance of a Taskqueue

        Raises:
            None
        '''
        self.logger.debug(f"Creating queue")

        # Ensure the multiprocessing manager has been created
        _manager = self._get_manager()

        return TaskQueue(
            queue=_manager.Queue(),
            stop_event=_manager.Event(),
            message_handler=message_handler
        )


    # 
    # Logger
    #
    def Logger(
            self,
            name: str = "",
            level: str = LoggingLevel.INFO.value,
            filename: str = "",
            to_console: bool = False,
    ) -> logging.Logger:
        '''
        Create a Queue (using the multiprocessing manager)

        Args:
            name: Name to use for the logger
            level (str): The log level to use when configuring logging
            filename (str): Path of file to log to.  If not set, will not log
                to file
            to_console (bool): Write the logging out to the standard output 
                device (usually stdout)

        Returns:
            Logger - An instance to use for logging

        Raises:
            None
        '''
        self.logger.debug(f"Creating logger")

        _logger: logging.Logger = logging.getLogger(name)
        self.logging_set_level(logger=_logger, log_level=level)

        # Remove existing handlers (eg stderr)
        for _handler in _logger.handlers.copy():
            _logger.removeHandler(_handler)

        # Log to a file if required
        if filename:
            _ = self.logging_set_file(
                logger=_logger,
                filename=filename
            )

        if to_console:
            _ = self.logging_to_console(logger=_logger)

        # Return the logger
        return _logger


    #
    # LocalDataStore
    #
    def LocalDataStore(
            self,
            password: str = "",
            salt: bytes = b"",
            security: str = "high"
    ) -> DataStoreLocal:
        '''
        Create a Local Datastore (using the multiprocessing manager)

        Args:
            password: (str): Password used to derive the encryption key - A
                random password will be used if none provided
            salt: (bytes): Binary string containing the salt - A default
                salt will be used in none provided
            security (str): Determines the computation time of the key.  Must
                be one of "low", "medium", or "high"

        Returns:
            DataStoreLocal: An instance of a Local Datastore

        Raises:
            None
        '''
        self.logger.debug(f"Creating local datastore")

        # Ensure the multiprocessing manager has been created
        _manager = self._get_manager()

        return DataStoreLocal(
            lock=_manager.Lock(),
            password=password,
            salt=salt,
            security=security,
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console
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
