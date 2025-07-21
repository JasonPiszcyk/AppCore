#!/usr/bin/env python3
'''
Multitasking module

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
from appcore.multitasking.shared import AppGlobal

# System Modules
from threading import Lock
import enum

# Local app modules
from appcore.multitasking.task import Task
from appcore.multitasking.queue import MessageFrameBase
from appcore.multitasking.exception import MultiTaskingTaskNotFoundError

# Imports for python variable type hints
from typing import Callable
from multiprocessing.managers import SyncManager
from appcore.shared import BasicDict


###########################################################################
#
# Module variables/constants/types
#
###########################################################################
TaskDict = dict[str, Task]

# How often should the watchdog check the tasks
WATCHDOG_WAIT_TIME: float = 1.0

# The message types
class TaskAction(enum.Enum):
    START           = "__task_start__"
    STOP            = "__task_stop__"
    ADD             = "__task_add__"
    DELETE          = "__task_delete__"
    STATUS          = "__task_status__"


###########################################################################
#
# MessageFrames - Different Frame types based on MessageFrameBase
#
###########################################################################
#
# Queue Message Frames derived from the MessageFrameBase class
#
class TaskMgmtMessageFrame(MessageFrameBase):
    ''' Message Frame for task mamagement'''
    def __init__(
            self,
            action: TaskAction = TaskAction.ADD,
            task: Task | None = None
        ):
        super().__init__()

        # Validate the args
        if action in TaskAction:
            self.action = action
        else:
            self.action = TaskAction.ADD

        self.task = task


###########################################################################
#
# MultiTasking Class
#
###########################################################################
class MultiTasking():
    '''
    Class to handle multi-processing/multi-threading

    Attributes:
        tasks (list) [Readonly]: A list of the current task IDs
        running_tasks (list) [Readonly]: A list of the current running task IDs
        parent_process_is_alive (bool) [Readonly]: Indicator if the 'parent
            process' process is alive
        watchdog_is_alive (bool) [Readonly]: Indicator if the watchdog thread 
            is alive
        queue_loop_is_alive (bool) [Readonly]: Indicator if the queue loop
            thread is alive
    '''

    #
    # __init__
    #
    def __init__(
            self,
            parent_process_task: Task | None = None,
            watchdog_task: Task | None = None,
            queue_loop_task: Task | None = None,
    ):
        '''
        Initializes the instance.

        Args:
            parent_process_task (Task): The parent process Task that was
                created by 'start'
            watchdog_task (Task): The watchdog Task that was created by 'start'
            queue_loop_task (Task): The queue loop Task that was created
                by 'start'
        
        Returns:
            None

        Raises:
            None
        '''
        # Private properties
        self.__task_dict: TaskDict = {}
        self.__task_dict_lock: Lock = Lock()

        # Attributes
        self.parent_process_task: Task | None = parent_process_task
        self.watchdog_task: Task | None = watchdog_task
        self.queue_loop_task: Task | None = queue_loop_task



    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # tasks
    #
    @property
    def tasks(self) -> list:
        ''' List of current task ID's '''
        _task_list: list = []

        for _task in self.__task_dict.values():
            _task_list.append(_task.id)

        return _task_list


    #
    # tasks
    #
    @property
    def running_tasks(self) -> list:
        ''' List of running task ID's '''
        _task_list: list = []

        for _task in self.__task_dict.values():
            if _task.is_alive: _task_list.append(_task.id)

        return _task_list


    #
    # parent_process_is_alive
    #
    @property
    def parent_process_is_alive(self) -> bool:
        ''' Check if the parent_process process is alive '''
        if self.parent_process_task:
            return self.parent_process_task.is_alive
        else:
            return False


    #
    # watchdog_is_alive
    #
    @property
    def watchdog_is_alive(self) -> bool:
        ''' Check if the watchdog thread is alive '''
        if self.watchdog_task:
            return self.watchdog_task.is_alive
        else:
            return False


    #
    # queue_loop_is_alive
    #
    @property
    def queue_loop_is_alive(self) -> bool:
        ''' Check if the queue loop thread is alive '''
        if self.queue_loop_task:
            return self.queue_loop_task.is_alive
        else:
            return False


    #
    # manager
    #
    @property
    def manager(self) -> SyncManager | None:
        ''' The multiprocessing manager to enable resource sharing'''
        _manager = AppGlobal.get("MultiProcessingManager", None)
        if not _manager:
            return None
        else:
            return _manager


    ###########################################################################
    #
    # Management Functions for the Multitasking System
    #
    ###########################################################################
    #
    # parent_process
    #
    # def parent_process(self):
    #     '''
    #     Create a separate process as a parent for other processes.

    #     If we fork/spawn from this process, it copies across any threads
    #     that may have been started.

    #     This process is started before any other threads or processes in
    #     the Task Management system

    #     Args:
    #         None
        
    #     Returns:
    #         None

    #     Raises:
    #         None
    #     '''
    #     if not self.parent_process_task:
    #         raise RuntimeError(
    #             "INTERNAL: Parent Process task has not been stored"
    #         )

    #     #
    #     # Define the call back functions for the processing loop
    #     #
    #     def _parent_process_on_invalid(frame):
    #         # Invalid packet or unknown message type - Ignore it
    #         pass


    #     def _parent_process_on_recv(frame):
    #         # Should be message frames of type: TaskMgmtMessageFrame
    #         if not isinstance(frame, TaskMgmtMessageFrame):
    #             # We are going to ignore this message - Invalid frame
    #             # May want to log this at some stage?
    #             pass

    #         else:
    #             # Make sure there is a task to deal with
    #             if not frame.task or not isinstance(frame.task, Task):
    #                 return

    #             elif frame.action == TaskAction.START:
    #                 # Make sure we are starting a process
    #                 if not frame.task.as_thread:
    #                     if not frame.task.is_alive: frame.task.start()

    #             elif frame.action == TaskAction.STOP:
    #                 # Stop the task
    #                 if not frame.task.as_thread:
    #                     if frame.task.is_alive: frame.task.stop()


    #     # Process the queue (will loop until stopped)
    #     self.parent_process_task.send_to_task_queue.listener(
    #         on_recv = _parent_process_on_recv,
    #         on_invalid = _parent_process_on_invalid,
    #         on_msg_ok = None,
    #         on_msg_error = None,
    #         on_msg_exit = None,
    #         on_msg_refresh = None,
    #     )


    #
    # watchdog
    #
    def watchdog(self):
        '''
        Check on the status of the processes and threads

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Make sure the watchdog and queue loop tasks have been stored
        # Really big problem if they have not been created
        if not self.watchdog_task:
            raise RuntimeError("INTERNAL: Watchdog task has not been stored")

        if not self.queue_loop_task:
            raise RuntimeError("INTERNAL: Queue Loop task has not been stored")

        # Disable signal processing (Signals handled in queue_loop)
        # ignore_signals()

        # Get the event from the task
        _watchdog_ending = self.watchdog_task.stop_event

        # Get the 'to task' queue from the task
        _send_queue = self.queue_loop_task.send_to_task_queue

        # Keep doing this until we receive the vent to exit
        while not _watchdog_ending.is_set():
            # Process the tasks to make sure they are OK
            for _task in self.__task_dict.values():
                # Is the task alive?
                if not _task.is_alive:
                    if _task.runnable:
                        # Clean up the dead task
                        _task.cleanup()

                        # Send a message to restart it if needed
                        if _task.restart:
                            _send_queue.send(
                                frame=TaskMgmtMessageFrame(
                                    action=TaskAction.START,
                                    task=_task
                                )
                            )

                else:
                    if not _task.runnable:
                        # Task is running, but marked not runnable.  Stop it
                        _send_queue.send(
                            frame=TaskMgmtMessageFrame(
                                action=TaskAction.STOP,
                                task=_task
                            )
                        )

            # Pause, ending early if the stop event occurs
            _watchdog_ending.wait(timeout=WATCHDOG_WAIT_TIME)


    #
    # queue_loop
    #
    def queue_loop(self):
        '''
        Process messsage sent to the queue

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        # Make sure the queue loop task has been stored
        # Really big problem if it has not been created
        if not self.queue_loop_task:
            raise RuntimeError("INTERNAL: Queue Loop task has not been stored")

        # Get the 'to task' queue from the task
        _listen_queue = self.queue_loop_task.send_to_task_queue

        #
        # Define the call back functions for the processing loop
        #
        def _queue_loop_on_invalid(frame):
            # Invalid packet or unknown message type - Ignore it
            pass


        def _queue_loop_on_recv(frame):
            # Should be message frames of type: TaskMgmtMessageFrame
            if not isinstance(frame, TaskMgmtMessageFrame):
                # We are going to ignore this message - Invalid frame
                # May want to log this at some stage?
                pass

            else:
                # Make sure there is a task to deal with
                if not frame.task or not isinstance(frame.task, Task):
                    return

                if frame.action == TaskAction.ADD:
                    # Add the task if not in the task dict
                    if not frame.task.id in self.__task_dict:
                        with self.__task_dict_lock:
                            self.__task_dict[frame.task.id] = frame.task
    
                elif frame.action == TaskAction.DELETE:
                    # Delete the task from the frame dict
                    if frame.task.id in self.__task_dict:
                        with self.__task_dict_lock:
                            del self.__task_dict[frame.task.id]

                elif frame.action == TaskAction.START:
                    # Start the task
                    if frame.task.id in self.__task_dict:
                        frame.task.runnable = True

                        # If task is a process pass off to parent process
                        if frame.task.as_thread:
                            if not frame.task.is_alive: frame.task.start()
                        elif self.parent_process_task:
                            self.parent_process_task.send_to_task_queue.send(
                                frame=frame
                            )

                elif frame.action == TaskAction.STOP:
                    # Stop the task if it is in the task dict
                    if frame.task.id in self.__task_dict:
                        frame.task.runnable = False

                        # If task is a process pass off to parent process
                        if frame.task.as_thread:
                            if frame.task.is_alive: frame.task.stop()
                        elif self.parent_process_task:
                            self.parent_process_task.send_to_task_queue.send(
                                frame=frame
                            )


        # Process the queue (will loop until stopped)
        _listen_queue.listener(
            on_recv = _queue_loop_on_recv,
            on_invalid = _queue_loop_on_invalid,
            on_msg_ok = None,
            on_msg_error = None,
            on_msg_exit = None,
            on_msg_refresh = None,
        )


    ###########################################################################
    #
    # Management Functions for tasks
    #
    ###########################################################################
    #
    # task_add
    #
    def task_add(
            self,
            id: str = "",
            target: Callable | None = None,
            kwargs: BasicDict = {},
            stop_function: Callable | None = None,
            stop_kwargs: BasicDict = {},
            restart: bool = False,
            as_thread: bool = True
    ) -> str:
        '''
        Adds a task to the system

        Args:
            id (str): An identifier for the task
            target (function): Function to run in the new thread/process
            kwargs (dict): Arguments to pass the target function
            stop_function (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass to the stop function.
            restart: (bool): Restart the task if it stops (eg fails)
            as_thread (bool): Start the task as a thread (or a process)
        
        Returns:
            string: The ID of the task that has been created

        Raises:
            None
        '''
        _task = Task(
            id=id,
            target=target,
            kwargs=kwargs,
            stop_function=stop_function,
            stop_kwargs=stop_kwargs,
            restart=restart,
            as_thread=as_thread
        )

        # Add the task if not in the task dict
        if not _task.id in self.__task_dict:
            with self.__task_dict_lock:
                self.__task_dict[_task.id] = _task

        return _task.id


    #
    # task_delete
    #
    def task_delete(
            self,
            id: str = "",
    ) -> None:
        '''
        Deletes a task from the system

        Args:
            id (str): An identifier for the task
        
        Returns:
            None

        Raises:
            MultiTaskingTaskNotFoundError:
                When the task ID cannot be found in the task dict
        '''
        # Check if the task is in the task dict
        if not id in self.__task_dict:
            raise MultiTaskingTaskNotFoundError (
                f"ID = {id}"
            )

        with self.__task_dict_lock:
            del self.__task_dict[id]


    #
    # task_start
    #
    def task_start(
            self,
            id: str = "",
    ) -> None:
        '''
        Starts a task

        Args:
            id (str): An identifier for the task
        
        Returns:
            None

        Raises:
            MultiTaskingTaskNotFoundError:
                When the task ID cannot be found in the task dict
        '''
        # Check if the task is in the task dict
        if not id in self.__task_dict:
            raise MultiTaskingTaskNotFoundError (
                f"ID = {id}"
            )

        if self.queue_loop_task:
            self.queue_loop_task.send_to_task_queue.send(
                frame=TaskMgmtMessageFrame( 
                    action=TaskAction.START,
                    task=self.__task_dict[id]
                )
            )


    #
    # task_stop
    #
    def task_stop(
            self,
            id: str = "",
    ) -> None:
        '''
        Stops a task

        Args:
            id (str): An identifier for the task
        
        Returns:
            None

        Raises:
            MultiTaskingTaskNotFoundError:
                When the task ID cannot be found in the task dict
        '''
        # Check if the task is in the task dict
        if not id in self.__task_dict:
            raise MultiTaskingTaskNotFoundError (
                f"ID = {id}"
            )

        # If the task is already stopped, ignore it
        if not self.__task_dict[id].is_alive:
            return

        if self.queue_loop_task:
            self.queue_loop_task.send_to_task_queue.send(
                frame=TaskMgmtMessageFrame( 
                    action=TaskAction.STOP,
                    task=self.__task_dict[id]
                )
            )


    #
    # task_status
    #
    def task_status(
            self,
            id: str = "",
    ) -> None:
        '''
        Update the volatile status info for a task

        Args:
            id (str): An identifier for the task
        
        Returns:
            None

        Raises:
            MultiTaskingTaskNotFoundError:
                When the task ID cannot be found in the task dict
        '''
        # Check if the task is in the task dict
        if not id in self.__task_dict:
            raise MultiTaskingTaskNotFoundError (
                f"ID = {id}"
            )

        if not self.__task_dict[id].as_thread:
            # Get the parent process to perform the update
            # 'is_alive' will update info for the thread
            if self.parent_process_task:
                self.parent_process_task.send_to_task_queue.send(
                    frame=TaskMgmtMessageFrame( 
                        action=TaskAction.STATUS,
                        task=self.__task_dict[id]
                    )
                )

            # Wait for the update
            self.__task_dict[id].status_barrier.wait()


    #
    # task_stop_all
    #
    def task_stop_all(self) -> None:
        '''
        Stops all tasks

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        for _task in self.__task_dict.values():
            self.task_stop(_task.id)


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

