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
from appcore.multitasking.task import Task
from appcore.multitasking.watchdog import Watchdog as WatchdogClass
from appcore.multitasking.task_queue import TaskQueue
from appcore.datastore.local import DataStoreLocal
from appcore.datastore.system import DataStoreSystem
from appcore.datastore.redis import DataStoreRedis
from appcore.datastore.inifile import DataStoreINIFile
from appcore.multitasking.scheduler import Scheduler as SchedulerClass
from appcore.server.telemetry import TelemetryServer as TelemetryServerClass

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
APPCORE_WATCHDOG_INTERVAL = 10.0
SERVER_TIMEOUT = 1.0

LABEL_SCHEDULER = "Scheduler Server"
LABEL_TELEMETRY_WEB = "Telemetry Web Server"


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

        # Don't create a watchdog until needed
        self.__watchdog: WatchdogClass | None = None

        # Don't create a scheduler until needed
        self.__scheduler: SchedulerClass | None = None

        # Don't create a telemetry server until requested
        self.__telemetry_server: TelemetryServerClass | None = None

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


    #
    # watchdog
    #
    @property
    def watchdog(self) -> WatchdogClass | None:
        ''' The manager watchdog instance '''
        return self._get_watchdog()


    ###########################################################################
    #
    # Functions to manage internal resources
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
    # _get_watchdog
    #
    def _get_watchdog(self) -> WatchdogClass:
        '''
        Get the internal watchdog for AppCore

        Args:
            None

        Returns:
            WatchdogClass

        Raises:
            None
        '''
        if not self.__watchdog:
            self.__watchdog = self.Watchdog(interval=APPCORE_WATCHDOG_INTERVAL)

        return self.__watchdog


    #
    # shutdown
    #
    def shutdown(self) -> None:
        '''
        Shutdown any servers started by the manager

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self.logger.debug(f"Shutting Down")

        # See if a telemetry server is running
        if self.__telemetry_server:
            self.StopTelemetryServer()
            self.__telemetry_server = None

        # See if a scheduler is running
        if self.__scheduler:
            self.StopScheduler()
            self.__scheduler = None

        # Give things a chance to finish
        # time.sleep(1)

        # See if a watchdog is running
        if self.__watchdog:
            self.__watchdog.loop_stop()
            self.__watchdog = None


    ###########################################################################
    #
    # Resource Creation Methods
    #
    ###########################################################################
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
     ) -> Task:
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
            Task: The task created (as a thread based task)

        Raises:
            None
        '''
        self.logger.debug(f"Creating thread ({name})")

        # Ensure the multiprocessing manager has been created
        # Also ensures the instance attributes __context and __manager are set
        _manager = self._get_manager()

        return Task(
            name=name,
            context=self.__context,
            info_dict=_manager.dict(),
            results_dict=_manager.dict(),
            start_event=_manager.Event(),
            stop_event=_manager.Event(),
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
     ) -> Task:
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
            Task: The task created (as a process based task)

        Raises:
            None
        '''
        self.logger.debug(f"Creating process ({name})")

        # Ensure the multiprocessing manager has been created
        # Also ensures the instance attributes __context and __manager are set
        _manager = self._get_manager()

        return Task(
            name=name,
            context=self.__context,
            info_dict=_manager.dict(),
            results_dict=_manager.dict(),
            start_event=_manager.Event(),
            stop_event=_manager.Event(),
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
    # Watchdog
    #
    def Watchdog(
            self,
            interval: float = 30.0,
            thread_only: bool = False
    ) -> WatchdogClass:
        '''
        Create a watchdog to monitor tasks

        Args:
            interval (float): How often the watchdog (in seconds) wakes up
                and checks the tasks
            thread_only (bool): If True, use local dicts to store task info
                (rather than SyncManager dicts).  Allows for greater
                flexibility in task arguments

        Returns:
            Watchdog: An instance of the Watchdog

        Raises:
            None
        '''
        self.logger.debug(f"Creating watchdog")

        # Ensure the multiprocessing manager has been created
        # Also ensures the instance attributes __context and __manager are set
        _manager = self._get_manager()

        if thread_only:
            _watchdog = WatchdogClass(
                stop_event=_manager.Event(),
                shutdown_event=_manager.Event(),
                interval_event=_manager.Event(),
                thread_only=True,
                log_level=self._log_level,
                log_file=self._log_file,
                log_to_console=self.log_to_console
            )

        else:
            _watchdog = WatchdogClass(
                task_start_dict=_manager.dict(),
                task_stop_dict=_manager.dict(),
                task_restart_dict=_manager.dict(),
                stop_event=_manager.Event(),
                shutdown_event=_manager.Event(),
                interval_event=_manager.Event(),
                thread_only=False,
                log_level=self._log_level,
                log_file=self._log_file,
                log_to_console=self.log_to_console
            )

        _kwargs = {
            "interval": interval
        }

        _watchdog_task = self.Thread(
            name = f"Watchdog",
            target = _watchdog.loop,
            kwargs = _kwargs,
        )

        _watchdog_task.start()

        # Store the Task ID (so the thread can be cleaned up later)
        _watchdog.task_id = _watchdog_task.task_id

        return _watchdog


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
            security: str = "high",
            dot_names: bool = False
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
            dot_names (bool): If True, use dot names to create a hierarchy of
                values for this data store.  If False, dots in names are
                treated as normal characters

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
            dot_names=dot_names,
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console
        )


    #
    # SystemDataStore
    #
    def SystemDataStore(
            self,
            password: str = "",
            salt: bytes = b"",
            security: str = "high",
            dot_names: bool = False
    ) -> DataStoreSystem:
        '''
        Create a System Datastore (using the multiprocessing manager)

        Args:
            password: (str): Password used to derive the encryption key - A
                random password will be used if none provided
            salt: (bytes): Binary string containing the salt - A default
                salt will be used in none provided
            security (str): Determines the computation time of the key.  Must
                be one of "low", "medium", or "high"
            dot_names (bool): If True, use dot names to create a hierarchy of
                values for this data store.  If False, dots in names are
                treated as normal characters

        Returns:
            DataStoreSystem: An instance of a System Datastore

        Raises:
            None
        '''
        self.logger.debug(f"Creating system datastore")

        # Ensure the multiprocessing manager has been created
        _manager = self._get_manager()

        return DataStoreSystem(
            data=_manager.dict(),
            data_expiry=_manager.list(),
            password=password,
            salt=salt,
            security=security,
            dot_names=dot_names,
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console
        )


    #
    # RedisDataStore
    #
    def RedisDataStore(
            self,
            password: str = "",
            salt: bytes = b"",
            security: str = "high",
            dot_names: bool = False,
            **kwargs: KeywordDictType
    ) -> DataStoreRedis:
        '''
        Create a System Datastore (using the multiprocessing manager)

        Args:
            password: (str): Password used to derive the encryption key - A
                random password will be used if none provided
            salt: (bytes): Binary string containing the salt - A default
                salt will be used in none provided
            security (str): Determines the computation time of the key.  Must
                be one of "low", "medium", or "high"
            dot_names (bool): If True, use dot names to create a hierarchy of
                values for this data store.  If False, dots in names are
                treated as normal characters
            kwargs (dict): List of redis parameters to be pass to the redis
                connection

        Returns:
            DataStoreRedis: An instance of a Redis Datastore

        Raises:
            None
        '''
        self.logger.debug(f"Creating redis datastore")

        # Ensure the multiprocessing manager has been created
        _manager = self._get_manager()

        return DataStoreRedis(
            password=password,
            salt=salt,
            security=security,
            dot_names=dot_names,
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console,
            **kwargs
        )


    #
    # INIFileDataStore
    #
    def INIFileDataStore(
            self,
            filename: str = "",
            password: str = "",
            salt: bytes = b"",
            security: str = "high"
    ) -> DataStoreINIFile:
        '''
        Create an INIFile Datastore

        Args:
            filename (str): The path for the INI file
            password: (str): Password used to derive the encryption key - A
                random password will be used if none provided
            salt: (bytes): Binary string containing the salt - A default
                salt will be used in none provided
            security (str): Determines the computation time of the key.  Must
                be one of "low", "medium", or "high"

        Returns:
            DataStoreINIFile: An instance of a INI File Datastore

        Raises:
            None
        '''
        self.logger.debug(f"Creating INI File datastore")

        # Ensure the multiprocessing manager has been created
        _manager = self._get_manager()

        return DataStoreINIFile(
            filename=filename,
            lock=_manager.Lock(),
            data_expiry=_manager.list(),
            password=password,
            salt=salt,
            security=security,
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console
        )


    #
    # StartScheduler
    #
    def StartScheduler(self) -> SchedulerClass: 
        '''
        Start a thread to run any scheduled tasks

        Args:
            None

        Returns:
            Scheduler - A scheduler instance

        Raises:
            None
        '''
        if self.__scheduler: return self.__scheduler

        self.logger.debug(f"Starting Scheduler")

        # Ensure the multiprocessing manager has been created
        _manager = self._get_manager()

        # Create a scheduler
        self.__scheduler = SchedulerClass(
            jobs=_manager.dict(),
            stop_event=_manager.Event(),
            interval_event=_manager.Event(),
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console
        )

        # Create a thread to run the scheduler
        _scheduler_task = Task(
            name=LABEL_SCHEDULER,
            context=self.__context,
            info_dict=_manager.dict(),
            results_dict=_manager.dict(),
            start_event=_manager.Event(),
            stop_event=_manager.Event(),
            target=self.__scheduler.run_scheduler,
            target_kwargs={},
            stop_function=self.__scheduler.stop_scheduler,
            stop_kwargs={},
            task_type="thread",
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console
        )

        # Add the tasks to the watchdog
        _watchdog = self._get_watchdog()
        _watchdog.register(
            task=_scheduler_task,
            label=LABEL_SCHEDULER
        )

        return self.__scheduler


    #
    # StopScheduler
    #
    def StopScheduler(self) -> None: 
        '''
        Stop the scheduler

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self.logger.debug(f"Stopping Scheduler")

        # Remove the task from the watchdog
        _watchdog = self._get_watchdog()
        _watchdog.deregister(
            label=LABEL_SCHEDULER
        )


    #
    # StartTelemetryServer
    #
    def StartTelemetryServer(
            self,
            hostname: str = "localhost",
            port: int = 8180,
    ) -> TelemetryServerClass: 
        '''
        Create a telemetry server

        Args:
            hostname (str): Used to identify interface to bind to
            port (int): The TCP port to listen on

        Returns:
            TelemetryServerClass: An instance of the Telemetry Server Class
            Task: A task running the web server

        Raises:
            None
        '''
        if self.__telemetry_server: return self.__telemetry_server

        self.logger.debug(f"Starting Telemetry Server")

        # Ensure the multiprocessing manager has been created
        _manager = self._get_manager()

        _datastore = DataStoreSystem(
            data=_manager.dict(),
            data_expiry=_manager.list(),
            security="low",
            dot_names=True,
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console
        )

        # If the scheduler isn't running, start it
        _scheduler = self.StartScheduler()

        self.__telemetry_server = TelemetryServerClass(
            datastore=_datastore,
            jobdict=_manager.dict(),
            scheduler=_scheduler,
            hostname=hostname,
            port=port,
            stop_event=_manager.Event()
        )

        # Create a thread to run the web server
        _web_server_task = Task(
            name=LABEL_TELEMETRY_WEB,
            context=self.__context,
            info_dict=_manager.dict(),
            results_dict=_manager.dict(),
            start_event=_manager.Event(),
            stop_event=_manager.Event(),
            target=self.__telemetry_server.run_web_server,
            target_kwargs={},
            stop_function=self.__telemetry_server.shutdown_web_server,
            stop_kwargs={},
            task_type="thread",
            log_level=self._log_level,
            log_file=self._log_file,
            log_to_console=self.log_to_console
        )

        # Add the tasks to the watchdog
        _watchdog = self._get_watchdog()
        _watchdog.register(
            task=_web_server_task,
            label=LABEL_TELEMETRY_WEB
        )

        return self.__telemetry_server


    #
    # StopTelemetryServer
    #
    def StopTelemetryServer(self) -> None: 
        '''
        Stop the telemetry server

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self.logger.debug(f"Stopping Telemetry Server")

        # Remove the task from the watchdog
        _watchdog = self._get_watchdog()
        _watchdog.deregister(
            label=LABEL_TELEMETRY_WEB
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
