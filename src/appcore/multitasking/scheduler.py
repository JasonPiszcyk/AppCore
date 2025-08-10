#!/usr/bin/env python3
'''
Scheduler - Module to run the scheduler

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
import enum
from datetime import datetime, timezone

# Local app modules
from appcore.appcore_base import AppCoreModuleBase
from appcore.multitasking.task import Task as TaskType
from appcore.conversion import set_value, DataType

# Imports for python variable type hints
from typing import Any
from multiprocessing.managers import DictProxy
from threading import Event as EventType
from appcore.multitasking.task import Task as TaskType


###########################################################################
#
# Module Specific Items
#
###########################################################################
#
# Types
#
class JobInterval(enum.Enum):
    SECONDS         = "seconds"
    MINUTES         = "minutes"
    HOURS           = "hours"
    DAYS            = "days"


#
# Constants
#
SHUTDOWN_TIMEOUT = 5.0

#
# Global Variables
#


###########################################################################
#
# _ScheduleDescription Class Definition
#
###########################################################################
class _ScheduleDescription():
    '''
    Class to describe a schedule

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            scheduler: Scheduler | None = None,
            schedule_type: str = "once",
            interval: int = 0,
            time: str = "",
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            scheduler (Scheduler): The instance o the scheduler
            schedule_type (str): The type of schedule for this job
                One of: "once", "interval", "at"
            interval (int): For interval schedule type, how oftern to run
                the job (in seconds)
            time (str): Time in format HH:MM:SS (24 hour)
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            AssertionError:
                when scheduler is not provided
                when interval is not an integer or not positive
                when time is not a string or correct format
        '''
        assert isinstance(scheduler, Scheduler), "a scheduler must be provided"
        assert isinstance(interval, int), "interval must be an integer"
        assert interval >= 0, "interval must be positive"

        # Check the time format is valid
        if not time:
            self.__at_timestamp = 0
            self.__time = ""

        else:
            self.__at_timestamp = self._timestamp_from_time(time=time)
            self.__time = time

        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__scheduler = scheduler
        self.__interval = interval
        self.__interval_unit = JobInterval.HOURS

        if schedule_type == "interval":
            self.__schedule_type = "interval"
        elif schedule_type == "at":
            self.__schedule_type = "at"
        else:
            self.__schedule_type = "once"

        # Attributes


    ###########################################################################
    #
    # Properties used to set the schedule
    #
    ###########################################################################
    #
    # seconds
    #
    @property
    def seconds(self) -> _ScheduleDescription:
        ''' Set the interval in seconds '''
        self.__interval_unit = JobInterval.SECONDS
        return self

    #
    # minutes
    #
    @property
    def minutes(self) -> _ScheduleDescription:
        ''' Set the interval in minutes '''
        self.__interval_unit = JobInterval.MINUTES
        return self


    #
    # hours
    #
    @property
    def hours(self) -> _ScheduleDescription:
        ''' Set the interval in hours '''
        self.__interval_unit = JobInterval.HOURS
        return self


    #
    # Alias for singular of above
    #
    second = seconds
    minute = minutes
    hour = hours

    ###########################################################################
    #
    # Schedule Creation
    #
    ###########################################################################
    #
    # _timestamp_from_time
    #
    def _timestamp_from_time(
            self,
            time: str = "",
    ) -> int:
        '''
        Create a timestamp from the time string

        Args:
            time (str): Time as a string in the format HH:MM

        Returns:
            None

        Raises:
            AssertionError:
                time is not a string or is invalid
        '''
        assert isinstance(time, str), "time must be a string"
        assert time, "time cannot be empty"

        _date = datetime.strftime(
            datetime.now(timezone.utc),
            "%Y-%m-%d"
        )
        try:
            _at = datetime.strptime(f"{_date} {time}", "%Y-%m-%d %H:%M")
        
        except:
            assert False, "time must be in format HH:MM"

        _now_timestamp = AppCoreModuleBase.timestamp()
        _at_timestamp = _at.timestamp()

        # If the timestamp is in the past, set it for same time a day later
        if _now_timestamp > _at_timestamp:
            _at_timestamp = _at_timestamp + 86400

        return int(_at_timestamp)


    #
    # every
    #
    def every(
            self,
            interval: int = 1,
    ) -> _ScheduleDescription:
        '''
        Create an interval based schedule

        Args:
            interval (int): The interval to run the task

        Returns:
            None

        Raises:
            AssertionError:
                interval is not an int or not positive
        '''
        assert isinstance(interval, int), "interval must be an integer"
        assert interval > 0, "interval must be positive"

        self.__interval = interval

        return self


    #
    # at
    #
    def at(
            self,
            time: str = "",
    ) -> _ScheduleDescription:
        '''
        Create a schedule at a specific time

        Args:
            interval (int): The interval to run the task

        Returns:
            None

        Raises:
            AssertionError:
                time is not a string or is empty
        '''
        assert isinstance(time, str), "time must be a string"
        assert time, "time must be a string in format HH:MM"

        self.__at_timestamp = self._timestamp_from_time(time=time)
        self.__time = time

        return self


    ###########################################################################
    #
    # Calculate the number of seconds until the next run
    #
    ###########################################################################
    #
    # calc_next_run
    #
    def calc_next_run(self) -> int:
        '''
        Calculate the number of seconds until the next run

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__schedule_type == "interval":
            if self.__interval_unit == JobInterval.SECONDS:
                return self.__interval

            if self.__interval_unit == JobInterval.MINUTES:
                return self.__interval * 60

            if self.__interval_unit == JobInterval.HOURS:
                return self.__interval * 3600

        if self.__schedule_type == "at":
            _now_timestamp = AppCoreModuleBase.timestamp()
            return self.__at_timestamp - _now_timestamp

        # For all other type of schedule return 0
        return 0


    #
    # run
    #
    def run(
            self,
            task: TaskType | None = None,
    ):
        '''
        Add a scheduled job (Usually at the end of a schedule chain)

        Args:
            task (Task): The task to run on a schedule

        Returns:
            None

        Raises:
            AssertionError:
                When the task is not an AppCore Task
        '''
        assert isinstance(task, TaskType), "Job must be a Task"

        # Calculate the number of seconds till the next run
        _next_run = self.calc_next_run()

        # Append the name to a timestamp to prevent duplicate keys/timestamps
        _timestamp = AppCoreModuleBase.timestamp(offset=_next_run)
        _job_name = f"{_timestamp}__{task.name}"

        self.__scheduler._add(
            jobname=_job_name,
            task=task,
            schedule_type=self.__schedule_type,
            interval=_next_run
        )


###########################################################################
#
# Scheduler Class Definition
#
###########################################################################
class Scheduler(AppCoreModuleBase):
    '''
    Class to describe the scheduler.

    A class to schedule jobs to run at specific times/intervals

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            jobs: DictProxy[Any, Any] | None = None,
            stop_event: EventType | None = None,
            interval_event: EventType | None = None,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            jobs (DictProxy): The dict of scheduled jobs
            stop_event (Event): Event to signal the scheduler to stop
            interval_event (Event): Event to wait on between running jobs.
                Wait can be interrupted if something has changed
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            AssertionError:
                When a SyncManager dict is not provided
        '''
        assert isinstance(jobs, DictProxy), \
            f"A SyncManager dict is required to implement the scheduler"
        assert stop_event, "stop_event must be provided"
        assert interval_event, "interval_event must be provided"

        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__jobs = jobs
        self.__stop_event = stop_event
        self.__interval_event = interval_event

        # Attributes


    ###########################################################################
    #
    # Scheduler
    #
    ###########################################################################
    #
    # run_scheduler
    #
    def run_scheduler(self) -> None:
        '''
        Run the scheduler tasks

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        while not self.__stop_event.is_set():
            self.logger.debug(f"Checking jobs")

            # Run any pending scheduled tasks
            _now = self.timestamp()
            _interval = 3600.0

            # Go through all of the jobs looking for jobs to be run
            _sorted_job_list = sorted(self.__jobs.keys())

            for _entry in _sorted_job_list:
                self.logger.debug(f"Entry: {_entry}")
                # Extract the timestamp from the key
                _timestamp_str, _, _ = _entry.partition("__")
                _timestamp = set_value(_timestamp_str, DataType.INT, default=0)            

                # Stop processing if the timestamp is in the future
                self.logger.debug(f"Now: {_now}, Timestamp: {_timestamp}")
                if _now < _timestamp:
                    # Set the interval to wake up for the next timestamp
                    # if this is less than the current interval
                    _diff = _timestamp - _now
                    if _interval > _diff: _interval = _diff
                    break

                # Run the job
                self.logger.debug(f"Scheduler: Task={self.__jobs[_entry]['task'].name}")
                self.__jobs[_entry]['task'].start()
                self.logger.debug(f"Started: Task={self.__jobs[_entry]['task'].name}")

                # Calculate when the job is due again
                if self.__jobs[_entry]['schedule_type'] == "interval":
                    _next_run = self.__jobs[_entry]['interval']

                else:
                    _next_run = 0

                # Append the name to a timestamp to prevent duplicate
                # keys/timestamps
                if _next_run > 0:
                    _timestamp = self.timestamp(offset=_next_run)
                    _job_name = f"{_timestamp}__" \
                        + f"{self.__jobs[_entry]['task'].name}"

                    # Create a new job / delete the old one
                    self.__jobs[_job_name] = self.__jobs[_entry]
                    del self.__jobs[_entry]

                    # If this is before the current interval, set the interval
                    if _next_run < _interval:
                        _interval = _next_run


            # Wait until the next job is due (or the event is set)
            if self.__interval_event.wait(timeout=_interval):
                # Event was set, clear it
                self.__interval_event.clear()

        self.logger.debug(f"Exiting scheduler loop")
        self.__stop_event.clear()
        self.__interval_event.clear()


    #
    # stop_scheduler
    #
    def stop_scheduler(self) -> None:
        '''
        Stop the scheduler

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError:
                When a stop event is not supplied
        '''
        self.logger.debug(f"Sending stop events")

        # Set the event to end the scheduler
        self.__stop_event.set()
        self.__interval_event.set()


    ###########################################################################
    #
    # Schedule Creation
    #
    ###########################################################################
    #
    # every
    #
    def every(
            self,
            interval: int = 1,
    ) -> _ScheduleDescription:
        '''
        Create an interval based schedule

        Args:
            interval (int): The interval to run the task

        Returns:
            None

        Raises:
            AssertionError:
                interval is not an int or not positive
        '''
        assert isinstance(interval, int), "interval must be an integer"
        assert interval > 0, "interval must be positive"

        return _ScheduleDescription(
            scheduler=self,
            schedule_type="interval",
            interval=interval
        )


    #
    # at
    #
    def at(
            self,
            time: str = "",
    ) -> _ScheduleDescription:
        '''
        Create a schedule at a specific time

        Args:
            interval (int): The interval to run the task

        Returns:
            None

        Raises:
            AssertionError:
                time is not a string or is empty
        '''
        assert isinstance(time, str), "time must be a string"
        assert time, "time must be a string in format HH:MM:SS"

        return _ScheduleDescription(
            scheduler=self,
            schedule_type="at",
            time=time
        )


    ###########################################################################
    #
    # Scheduler Job Management
    #
    ###########################################################################
    #
    # _add
    #
    def _add(
            self,
            jobname: str = "",
            task: TaskType | None = None,
            schedule_type: str = "interval",
            interval: int = 0,
    ) -> None:
        '''
        Add a scheduled job

        Args:
            name: (str): The job name generated by the schedule
            task (Task): The task to run
            schedule_type (str): The type of schedule for this job
                One of: "once", "interval", "at"

        Returns:
            None

        Raises:
            AssertionError:
                When jobname is not a string or empty
                When the task provided is not of type Task
        '''
        assert isinstance(jobname, str), "jobname must be a string"
        assert jobname, "jobname cannot be empty"
        assert isinstance(task, TaskType), "Job must be a Task"

        self.__jobs[jobname] ={
            "task": task,
            "schedule_type": schedule_type,
            "interval": interval
        }

        # Let the scheduler know about the new job
        self.__interval_event.set()


    #
    # cancel
    #
    def cancel(
            self,
            name: str = "",
    ) -> None:
        '''
        Remove scheduled jobs for a task

        Args:
            name (string): The name of the task to be removed

        Returns:
            None

        Raises:
            AssertionError:
                When name is not a string or empty
        '''
        assert isinstance(name, str), "Name must be a string"
        assert name, "A name is required to remove a job"

        # We have to look through the list of jobs as the job name
        # includes a timestamp
        _sorted_job_list = sorted(self.__jobs.keys())
        for _entry in _sorted_job_list:
            # Extract the timestamp from the key
            _, _, _task_name = _entry.partition("__")

            if name == _task_name:
                del self.__jobs[_entry]


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
