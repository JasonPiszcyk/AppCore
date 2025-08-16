#!/usr/bin/env python3
'''
Watchdog - Ensure Tasks are running

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
from threading import enumerate as enumerate_threads
import traceback
import uuid

# Local app modules
from appcore.appcore_base import AppCoreModuleBase
from appcore.typing import TaskStatus

# Imports for python variable type hints
from typing import Any
from threading import Event as EventType
from multiprocessing.managers import DictProxy
from appcore.multitasking.task import TaskType


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
WATCHDOG_JOIN_TIMEOUT = 5.0
WATCHDOG_SHUTDOWN_TIMEOUT = 5.0

#
# Global Variables
#


###########################################################################
#
# Watchdog Class Definition
#
###########################################################################
class Watchdog(AppCoreModuleBase):
    '''
    Class to describe a watchdog.

    The watchdog looks after a group of tasks and ensures they are running

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            task_start_dict: DictProxy[Any, Any] | None = None,
            task_stop_dict: DictProxy[Any, Any] | None = None,
            task_restart_dict: DictProxy[Any, Any] | None = None,
            stop_event: EventType | None = None,
            shutdown_event: EventType | None = None,
            interval_event: EventType | None = None,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            task_start_dict (dict): SyncManger dict to store the tasks to start
            task_stop_dict (dict): SyncManger dict to store the tasks to stop
            task_restart_dict (dict): SyncManger dict to store the tasks to
                watch and restart if required
            stop_event (Event): A SyncManager event to signal the watchdog to 
                stop
            shutdown_event (Event): A SyncManager event to signal the watchdog
                has finished shutting down 
            interval_event (Event): A SyncManager event to signal the watchdog
                to skip waiting during the interval
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        assert isinstance(task_start_dict, DictProxy), \
            f"A SyncManager dict is required to store tasks to be started"
        assert isinstance(task_stop_dict, DictProxy), \
            f"A SyncManager dict is required to store tasks to be stopped"
        assert isinstance(task_restart_dict, DictProxy), \
            f"A SyncManager dict is required to store tasks to be restarted"
        assert stop_event, "An event is required to stop the watchdog"
        assert shutdown_event, "An event is required to sync watchdog shutdown"
        assert interval_event, "An event is required manage watchdog intervals"

        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__task_start_dict = task_start_dict
        self.__task_stop_dict = task_stop_dict
        self.__task_restart_dict = task_restart_dict
        self.__stop_event = stop_event
        self.__shutdown_event = shutdown_event
        self.__interval_event = interval_event

        # Attributes
        self.task_id: str = ""


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################


    ###########################################################################
    #
    # The watchdog processing
    #
    ###########################################################################
    #
    # loop
    #
    def loop(
            self,
            interval: float = 30.0
    ):
        '''
        The watchdog processing loop

        Args:
            interval (float): How often the watchdog (in seconds) wakes up
                and checks the tasks

        Returns:
            None

        Raises:
            None
        '''
        self.logger.debug("Watchdog: Starting")

        # Check the stop event
        while not self.__stop_event.is_set():
            # Catch everything to keep this running
            try:
                #
                # Tasks to be stopped
                #
                _task_list = self.__task_stop_dict.keys()
                for _key in _task_list:
                    _task: TaskType = self.__task_stop_dict[_key]
                    self.logger.info(
                        f"Watchdog: Task ({_key}): [id={_task.id}] " +
                        "Stop has been requested"
                    )
                    _task.stop()

                    # Remove the key from all of the dicts
                    if _key in self.__task_start_dict:
                        del self.__task_start_dict[_key]

                    if _key in self.__task_restart_dict:
                        del self.__task_restart_dict[_key]

                    del self.__task_stop_dict[_key]

                #
                # Tasks to be started
                #
                _task_list = self.__task_start_dict.keys()
                for _key in _task_list:
                    _task: TaskType = self.__task_start_dict[_key]
                    self.logger.info(
                        f"Watchdog: Task ({_key}): Start has been requested"
                    )
                    _task.start()

                    # Move the task to the restart dict
                    self.__task_restart_dict[_key] = _task
                    del self.__task_start_dict[_key]

                #
                # Tasks to be watched and restarted if necessary
                #
                _task_list = self.__task_restart_dict.keys()
                for _key in _task_list:
                    _task: TaskType = self.__task_restart_dict[_key]

                    _restart_task = False
                    if _task.status != TaskStatus.RUNNING.value:
                        _restart_task = True
                        self.logger.warning(
                            f"Watchdog: Task ({_key}: [id={_task.id}] " +
                            f"{_task.name}) not running.  Status: " +
                            f"{_task.status}"
                        )

                    elif not _task.is_alive:
                        _restart_task = True
                        self.logger.warning(
                            f"Watchdog: Task ({_key}: [id={_task.id}] " +
                            f"{_task.name}) not running.  Task not alive"
                        )

                    if _restart_task:
                        _task.cleanup()
                        _task.start()
                        self.logger.info(
                            f"Watchdog: Task ({_key}: {_task.name}) " +
                            "restarted"
                        )

            except:
                self.logger.error("Watchdog has failed")
                _exception_stack = traceback.format_exc()
                self.logger.error(_exception_stack)

            # Pause for the interval - Can be woken up if needed
            if self.__interval_event.wait(timeout=interval):
                # Got woken up - Reset the event
                self.__interval_event.clear()


        # Set all tasks to be stopped
        self.logger.debug("Stopping registered tasks")

        _task_list = self.__task_start_dict.keys()
        for _key in _task_list:
            _task: TaskType = self.__task_start_dict[_key]
            self.logger.debug(f"Setting stop (start): {_task.name}")
            self.__task_stop_dict[_key] = _task
            del self.__task_start_dict[_key]

        _task_list = self.__task_restart_dict.keys()
        for _key in _task_list:
            _task: TaskType = self.__task_restart_dict[_key]
            self.logger.debug(f"Setting stop (restart): {_task.name}")
            self.__task_stop_dict[_key] = _task
            del self.__task_restart_dict[_key]

        _task_list = self.__task_stop_dict.keys()
        for _key in _task_list:
            _task: TaskType = self.__task_stop_dict[_key]
            self.logger.debug(f"Stopping: {_task.name}")
            _task.stop()
            del self.__task_stop_dict[_key]

        # Indicate the shutdown is complete
        self.logger.debug("Shutdown done")
        self.__shutdown_event.set()

        # Reset the events
        self.__stop_event.clear()
        self.__interval_event.clear()
        self.logger.debug("Watchdog: Ending")


    #
    # loop_stop
    #
    def loop_stop(self):
        '''
        Stop the watchdog processing loop

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self.logger.debug("Request to stop Watchdog")

        # Set the events to exit the loop
        self.__interval_event.set()
        self.__stop_event.set()

        # Let the watchdog stop
        self.__shutdown_event.wait(timeout=WATCHDOG_SHUTDOWN_TIMEOUT)

        # Join the watchdog thread to clean it up
        for _thread in enumerate_threads():
            if _thread.name == self.task_id:
                self.logger.debug("Found Thread - Joining")
                _thread.join(timeout=WATCHDOG_JOIN_TIMEOUT)

        self.logger.debug("Request to stop Watchdog completed")


    ###########################################################################
    #
    # Add/Remove tasks to watch
    #
    ###########################################################################
    #
    # register
    #
    def register(
            self,
            task: TaskType | None = None,
            label: str = ""
    ) -> str:
        '''
        Register a task with the watchdog

        Args:
            task (Task): An AppCore task to be watched
            label (str): A label for the task within the watchdog.  If empty,
                a UUID will be allocated.

        Returns:
            str: The label of the task in the watchdog

        Raises:
            None
        '''
        assert task, "A task is required to register with the watchdog"
        assert isinstance(label, str), "Label must be a string"

        # If the label is empty, generate a uuid as a label
        if not label: label = str(uuid.uuid4())

        self.logger.debug(f"Registering Task: {label}")

        # Add the entry to the start task dict
        self.__task_start_dict[label] = task

        # Don't wait for the watchdog interval - Do this immediately
        self.__interval_event.set()

        return label


    #
    # deregister
    #
    def deregister(
            self,
            label: str = ""
    ):
        '''
        Register a task with the watchdog

        Args:
            label (str): The label for the task within the watchdog.

        Returns:
            None

        Raises:
            None
        '''
        assert isinstance(label, str), "Label must be a string"

        self.logger.debug(f"Deregistering Task: {label}")

        # Set the task to be stopped
        if label in self.__task_start_dict:
            self.__task_stop_dict[label] = self.__task_start_dict[label]

        elif label in self.__task_restart_dict:
            self.__task_stop_dict[label] = self.__task_restart_dict[label]

        self.__interval_event.set()


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
