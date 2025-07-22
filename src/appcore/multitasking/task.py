#!/usr/bin/env python3
'''
Task Class

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

def debug(msg):
    with open("/tmp/jpp.txt", "at") as f:
        f.write(f"{msg}\n")


###########################################################################
#
# Imports
#
###########################################################################
# Shared variables, constants, etc
from appcore.multitasking.shared import AppGlobal

# System Modules
import sys
import time
import enum
import traceback
import uuid
from threading import Thread, BrokenBarrierError
from multiprocessing import Process, current_process

# Local app modules
from appcore.shared import BasicDict
from appcore.multitasking.queue import TaskQueue
from appcore.multitasking import exception
from appcore.multitasking.shared import TaskAction
from appcore.multitasking.shared import TASK_ID_MULTITASKING_PROCESS
from appcore.multitasking.shared import TASK_ID_PARENT_PROCESS
from appcore.multitasking.shared import TASK_ID_QUEUE_LOOP
from appcore.multitasking.shared import TASK_ID_WATCHDOG
from appcore.multitasking.queue_message import MessageFrameBase


# Imports for python variable type hints
from typing import Any, Callable
from threading import Event as EventClass
from appcore.shared import BasicDict
from multiprocessing.managers import SyncManager
from threading import Barrier as BarrierClass

###########################################################################
#
# Module variables/constants/types
#
###########################################################################
type TaskDict = dict[str, Task]

# Task timeouts
BARRIER_WAIT: float = 1.0
TASK_START_TIMEOUT: float = 5.0
TASK_STOP_TIMEOUT: float = 15.0

# The process startup needs a small delay to allow for info to sync
PROCESS_STARTUP_DELAY: float = 0.1

# When joining a thread/process, it may be terminating - wait for it to finish
JOIN_THREAD_TIMEOUT: float = 10.0
JOIN_PROCESS_TIMEOUT: float = 10.0

STATUS_UPDATE_TIMEOUT: float = 5.0

class TaskStatus(enum.Enum):
    NOT_STARTED     = "Not Started"
    RUNNING         = "Running"
    STOPPED         = "Stopped"
    ERROR           = "Error"
    COMPLETED       = "Completed"


# A set of the management tasks
MGMT_TASKS = ( TASK_ID_PARENT_PROCESS, TASK_ID_QUEUE_LOOP, TASK_ID_WATCHDOG, )


###########################################################################
#
# MessageFrames - Different Frame types based on MessageFrameBase
#
###########################################################################
#
# Queue Message Frames derived from the MessageFrameBase class
#
class TaskMgmtMessageFrame(MessageFrameBase):
    ''' Message Frame for task management '''
    def __init__(
            self,
            action: TaskAction = TaskAction.ADD,
            task: Task | None = None,
            barrier: BarrierClass | None = None
        ):
        super().__init__()

        # Validate the args
        if action in TaskAction:
            self.action = action
        else:
            self.action = TaskAction.ADD

        self.task = task
        self.barrier = barrier


###########################################################################
#
# Task Class
#
###########################################################################
class Task():
    '''
    Class to describe a task

    Each instance of the class describes a task that the multitasking system
    can manage.

    Attributes:
        id (str): Task Identifier.  Will be set to a UUID if not provided.
        target (callable): The Function to run in the new thread/process.
        kwargs (dict): Arguments to pass the target function when starting.
        stop_function (callable): The Function to run to stop the
            thread/process.
        stop_kwargs (dict): Arguments to pass to the stop function.
        restart: (bool): If true, attempt to restart the task on completion or
            failure.
        runnable: (bool): If True the task can be started.  Should normally be
            set by the task system.  If modified directly and set to True, and
            restart is True, the watchdog will attempt to start the task. If
            modified directly and set to False, the watchdog will attempt to
            stop the task.
            
        in_manager (bool) [Readonly]: If true, the task has starrted by the
            manager process (so it should be a thread).  If false it has been
            by the parent process (so it shoudl be a process)
        as_thread (bool) [Readonly]: If true, the task is run as thread.  If
            False, the task is run as a process.
        thread_id (int) [Readonly]: The ID of the thread the task is using
            (None if no  thread in use).
        process_id (int) [Readonly]: The ID of the process the task is using
            (None if no process in use).
        is_alive (bool) [Readonly]: Indicator if the task is alive.
        is_process_alive (bool) [Readonly]:  Tries to query the process
            attached to this task.  Will not try to contact the parent
            process for the info, so is really only valid within the parent
            process.
        is_running (bool) [Readonly]: True if the status is "Running".
        is_ended (bool) [Readonly]: True if the task is no longer running.
        status (string) [Readonly]: The status of the task.  One of:
            Not Started: Task has been created but not started
            Running: Task is currently running
            Stopped: Task has been stopped and it's status is uncertain
            Error: Task has end with an error
            Completed: Task has ended without error
        send_to_task_queue (TaskQueue) [Readonly]: The queue to send data to
            the task.
        recv_from_task_queue (TaskQueue) [Readonly]: The queue to receive
            data from the task.
        stop_event (Event) [Readonly]: Event to signal the end of the task.
        task_info_status (dict) [Readonly]: The task info dict (status
            section) for this task
        task_info_results (dict) [Readonly]: The task info dict (results
            section) for this task
    '''

    #
    # __init__
    #
    def __init__(
            self, 
            id: str = "",
            target: Callable | None = None,
            kwargs: BasicDict = {},
            stop_function: Callable | None = None,
            stop_kwargs: BasicDict = {},
            restart: bool = False,
            as_thread: bool = True
    ):
        '''
        Initializes the instance.

        Args:
            id (str): An identifier for the task
            target (Callable): Function to run in the new thread/process
            kwargs (dict): Arguments to pass to the target function
            stop_function (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass the stop function
            restart: (bool): Restart the task if it stops (eg fails)
            as_thread (bool): Start the task as a thread (or a process)
        
        Returns:
            Task: An instance of the Task class

        Raises:
            None
        '''
        # Private properties used for managing the task
        self.__thread: Thread | None = None
        self.__process: Process | None = None
        self.__as_thread: bool = as_thread
        self.__send_to_task_queue: TaskQueue = TaskQueue(
            for_thread=as_thread
        )
        self.__recv_from_task_queue: TaskQueue = TaskQueue(
            for_thread=as_thread
        )

        # Get the manager
        if not AppGlobal.get("MultiProcessingManager", None):
            raise exception.MultiTaskingManagerNotFoundError(
                "Cannot create task without multiprocess manager"
            )

        _manager: SyncManager = AppGlobal["MultiProcessingManager"]

        self.__task_info = AppGlobal["TaskInfo"]
        self.__stop_event: EventClass = _manager.Event()

        # Attributes
        self.id: str = id if id else str(uuid.uuid4())
        self.target: Callable | None = target
        self.kwargs: BasicDict = kwargs
        self.stop_function: Callable | None = stop_function
        self.stop_kwargs: BasicDict = stop_kwargs
        self.restart: bool = restart
        self.runnable = False

        # Create the Task Info
        _status = _manager.dict()
        _status["status"] = TaskStatus.NOT_STARTED.value
        _status["is_alive"] = False
        _status["pid"] = 0

        _results = _manager.dict()
        _results["return_value"] = None
        _results["exception_name"] = ""
        _results["exception_desc"] = ""
        _results["exception_stack"] = ""

        self.__task_info["status"][self.id] = _status
        self.__task_info["results"][self.id] = _results


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # in_manager
    #
    @property
    def in_manager(self) -> bool:
        ''' Is the task instance in the manager or parent process? '''
        return current_process().name == TASK_ID_MULTITASKING_PROCESS


    #
    # as_thread
    #
    @property
    def as_thread(self) -> bool:
        ''' Identify if the task is run as a thread or process '''
        return self.__as_thread


    #
    # thread_id
    #
    @property
    def thread_id(self) ->  int | None:
        ''' The Thread ID property '''
        if self.__thread:
            return self.__thread.native_id
        else:
            return None


    #
    # process_id
    #
    @property
    def process_id(self) -> int | None:
        ''' The Process ID property '''
        _pid = self.__task_info["status"][self.id]["pid"]

        if _pid:
            return _pid
        else:
            return None


    #
    # is_alive
    #
    @property
    def is_alive(self) -> bool:
        ''' Indicate if the task is alive '''
        if self.__as_thread:
            _is_alive = self.__thread.is_alive() if self.__thread else False
            self.__task_info["status"][self.id]["is_alive"] = _is_alive
            return _is_alive

        # If this is one of the management processes, get it directly
        # as they are not running under the parent process
        if self.id in MGMT_TASKS:
            return self.__process.is_alive() if self.__process else False

        return self.__task_info["status"][self.id]["is_alive"]


    #
    # is_process_alive
    #
    @property
    def is_process_alive(self) -> bool:
        ''' Query the stored process for this task, skip remote checking '''
        if self.__as_thread:
            # Task is configured as a thread
            return False
        else:
            return self.__process.is_alive() if self.__process else False


    #
    # is_running
    #
    @property
    def is_running(self) -> bool:
        ''' Check if the task is running '''
        if self.__task_info["status"][self.id]["status"] == \
                TaskStatus.RUNNING.value:
            return True
        else:
            return False


    #
    # is_ended
    #
    @property
    def is_ended(self) -> bool:
        ''' Check if the task has finished running '''
        _status = self.__task_info["status"][self.id]["status"]

        if _status == TaskStatus.ERROR.value or \
                _status == TaskStatus.COMPLETED.value:
            return True
        else:
            return False


    #
    # status
    #
    @property
    def status(self) -> str:
        ''' The status of the task '''
        return self.__task_info["status"][self.id]["status"]


    #
    # send_to_task_queue
    #
    @property
    def send_to_task_queue(self) -> TaskQueue:
        ''' The queue for sending to the task '''
        return self.__send_to_task_queue


    #
    # recv_from_task_queue
    #
    @property
    def recv_from_task_queue(self) -> TaskQueue:
        ''' The queue for receiving from the task '''
        return self.__recv_from_task_queue


    #
    # stop_event
    #
    @property
    def stop_event(self) -> EventClass:
        ''' The event to stop the task '''
        return self.__stop_event


    #
    # task_info_status
    #
    @property
    def task_info_status(self) -> dict:
        ''' Pointer to the task_info dict (synced between processes) '''
        return self.__task_info["status"][self.id]


    #
    # task_info_results
    #
    @property
    def task_info_results(self) -> dict:
        ''' Pointer to the task_info dict (synced between processes) '''
        return self.__task_info["results"][self.id]


    ###########################################################################
    #
    # Convenience/helper functions
    #
    ###########################################################################
    #
    # run_task
    #
    def run_task(
            self,
            target: Callable | None = None,
            kwargs: BasicDict = {},
    ) -> None:
        '''
        Wrapper to run a task, and get return information

        Args:
            target (function): Function to run in the new thread/process
            kwargs (dict): Arguments to pass the target function

        Returns:
            None

        Raises:
            None
        '''
        debug(f"Running Task: {str(target)}")
        if callable(target):
            _return_value: Any = None
            _exception_name: str | None = None
            _exception_desc: str | None = None
            _exception_stack: str | None = None

            # Run the target, capturing any exceptions and the return value
            try:
                _return_value = target(**kwargs)
                self.__task_info["status"][self.id]["status"] = \
                    TaskStatus.COMPLETED.value
                self.__task_info["status"][self.id]["is_alive"] = False
                debug(f"Task finished OK: {str(target)}")

            except Exception:
                self.__task_info["status"][self.id]["status"] = \
                    TaskStatus.ERROR.value
                self.__task_info["status"][self.id]["is_alive"] = False
                _exception_stack = traceback.format_exc()
                debug(f"Task FAILED: {str(target)}")
                debug(_exception_stack)

                _exc_info = sys.exc_info()
                if _exc_info:
                    if _exc_info[0]:
                        _exception_name = _exc_info[0].__name__
                    if _exc_info[1]:
                        _exception_desc = str(_exc_info[1])

            # Set the return Value
            _results = self.__task_info["results"][self.id]
            _results["return_value"] = _return_value
            _results["exception_name"] = _exception_name
            _results["exception_desc"] = _exception_desc
            _results["exception_stack"] = _exception_stack


    ###########################################################################
    #
    # Thread Operations
    #
    ###########################################################################
    #
    # __thread_cleanup
    #
    def __thread_cleanup(self) -> None:
        '''
        Cleanup the thread once it has completed

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__thread:
            # Try to join the thread - Has to be done to clean it up
            if self.is_alive:
                self.__thread.join(timeout=JOIN_THREAD_TIMEOUT)

            # The thread should now be gone
            if self.is_alive:
                raise exception.MultiTaskingTaskIsRunningError(
                    f"Cleanup aborted on running task: {self.id}"
                )

            self.__thread: Thread | None = None


    #
    # __thread_start
    #
    def __thread_start(self) -> None:
        '''
        Start the thread

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Wrap the target function to gather information
        _kwargs: BasicDict = {
            "target": self.target,
            "kwargs": self.kwargs
        }

        if not self.__thread:
            if callable(self.target):
                # Start the thread
                self.__task_info["status"][self.id]["status"] = \
                    TaskStatus.RUNNING.value

                self.__thread = Thread(
                    target=self.run_task,
                    kwargs=_kwargs
                )
                self.__thread.start()


    #
    # __thread_stop
    #
    def __thread_stop(self) -> None:
        '''
        Stop the thread

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.is_alive:
            # Stop the thread
            if callable(self.stop_function):
                self.stop_function(**self.stop_kwargs)
            self.__thread_cleanup()


    ###########################################################################
    #
    # Process Operations
    #
    ###########################################################################
    #
    # __process_cleanup
    #
    def __process_cleanup(self) -> None:
        '''
        Cleanup the process once it has completed

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__process:
            # Try to join the process - Has to be done to clean it up
            if self.is_alive:
                self.__process.join(timeout=JOIN_PROCESS_TIMEOUT)

            if self.is_alive:
                raise exception.MultiTaskingTaskIsRunningError(
                    f"Cleanup aborted on running task: {self.id}"
                )

            self.__process.close()
            self.__process: Process | None = None


    #
    # __process_start
    #
    def __process_start(self) -> None:
        '''
        Start the process

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Wrap the target function to gather information
        _kwargs: BasicDict = {
            "target": self.target,
            "kwargs": self.kwargs
        }

        if not self.__process:
            # Start the process
            if callable(self.target):
                _task_info = self.__task_info["status"][self.id]
                # Start the process
                _task_info["status"] = TaskStatus.RUNNING.value
                _task_info["is_alive"] = True

                self.__process = Process(
                    target=self.run_task,
                    kwargs=_kwargs,
                    name=self.id
                )
                self.__process.start()
                _task_info["pid"] = self.__process.pid
                time.sleep(PROCESS_STARTUP_DELAY)


    #
    # __process_stop
    #
    def __process_stop(self) -> None:
        '''
        Stop the process

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.is_alive:
            # Stop the process
            if callable(self.stop_function):
                self.stop_function(**self.stop_kwargs)
            self.__process_cleanup()


    ###########################################################################
    #
    # Task Operations
    #
    ###########################################################################
    #
    # cleanup
    #
    def cleanup(self) -> None:
        '''
        Cleanup the task once it has completed

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Clean up the queues
        self.__send_to_task_queue.cleanup()
        self.__recv_from_task_queue.cleanup()

        # Cleanup the process/thread
        if self.__as_thread:
            self.__thread_cleanup()
        else:
            self.__process_cleanup()

        # Clear the event
        self.__stop_event.clear()


    #
    # start
    #
    def start(self, barrier: BarrierClass | None = None) -> None:
        '''
        Start the task

        Args:
            barrier (BarrierClass): If provided will trigger the barrier
                once the task has been started

        Returns:
            None

        Raises:
            MultiTaskingTaskIsRunningError:
                When Attempt to start an already running task
        '''
        if self.is_alive:
            raise exception.MultiTaskingTaskIsRunningError(
                f"Task is already running: {self.id}"
            )

        # Temp function to wait at the barrier if required
        def _barrier_wait():
            if not barrier: return
 
            try:
                barrier.wait(timeout=BARRIER_WAIT)
            except BrokenBarrierError:
                # Ignore this - The other process should be waiting
                # (and this is to let the caller know we are done)
                pass


        # Processes should be started via parent process (except MGMT tasks)
        if self.in_manager:
            if self.__as_thread:
                # It is a thread - Just start it
                self.__thread_start()
                _barrier_wait()
                return

            # If the is a MGMT task it can be started from here
            if self.id in MGMT_TASKS:
                self.__process_start()
                _barrier_wait()
                return

            # Pass this to the parent process
            if not AppGlobal.get("MultiTasking", None):
                raise exception.MultiTaskingNotFoundError(
                    "Unable to find the MultiTasking manager"
                )

            _multitasking = AppGlobal["MultiTasking"]
            if _multitasking.parent_process_task:
                _multitasking.parent_process_task.send_to_task_queue.send(
                    frame=TaskMgmtMessageFrame( 
                        action=TaskAction.START,
                        task=self,
                        barrier=barrier
                    )
                )
            
            return

        # In the parent process, so start the process
        if not self.__as_thread:
            self.__process_start()
            _barrier_wait()


    #
    # stop
    #
    def stop(self, barrier: BarrierClass | None = None) -> None:
        '''
        Stop the task

        Args:
            barrier (BarrierClass): If provided will trigger the barrier
                once the task has been stopped

        Returns:
            None

        Raises:
            MultiTaskingTaskIsNotRunningError:
                When attempting to stop a task that is not running
        '''
        if not self.is_alive:
            raise exception.MultiTaskingTaskIsNotRunningError(
                f"Task is not running: {self.id}"
            )

        def _barrier_wait():
            if not barrier: return
 
            try:
                barrier.wait(timeout=BARRIER_WAIT)
            except BrokenBarrierError:
                # Ignore this - The other process should be waiting
                # (and this is to let the caller know we are done)
                pass


        # Processes should be started via parent process (except MGMT tasks)
        if self.in_manager:
            if self.__as_thread:
                # It is a thread - Just stop it
                self.__thread_stop()
                _barrier_wait()
                return

            # If the is a MGMT task it can be stopped from here
            if self.id in MGMT_TASKS:
                self.__process_stop()
                _barrier_wait()
                return

            # Pass this to the parent process
            if not AppGlobal.get("MultiTasking", None):
                raise exception.MultiTaskingNotFoundError(
                    "Unable to find the MultiTasking manager"
                )

            _multitasking = AppGlobal["MultiTasking"]
            if _multitasking.parent_process_task:
                _multitasking.parent_process_task.send_to_task_queue.send(
                    frame=TaskMgmtMessageFrame( 
                        action=TaskAction.STOP,
                        task=self,
                        barrier=barrier
                    )
                )

            return

        # In the parent process, so stop the process
        if not self.__as_thread:
            self.__process_stop()
            _barrier_wait()



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
