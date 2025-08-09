#!/usr/bin/env python3
'''
Telemetry - Module to share app telemetry via a web server

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
from threading import Thread
from http.server import HTTPServer
from functools import partial
import schedule

# Local app modules
from appcore.server.web import SimplePage

# Imports for python variable type hints
from typing import Any, Callable
from multiprocessing.managers import DictProxy
from appcore.datastore.system import DataStoreSystem


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
# TelemetryServer Class Definition
#
###########################################################################
class TelemetryServer():
    '''
    Class to describe a telemetry server.

    The telemetry server share telemetry info about an app

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            datastore: DataStoreSystem | None = None,
            jobdict: DictProxy | None = None,
            hostname: str = "localhost",
            port: int = 8180,
            *args,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            datastore (DataStoreSystem): A system datastore instance to 
                store the telemetry in
            jobdict (DictProxy): A SyncManager dict to store job information
            hostname (str): Used to identify interface to bind to
            port (int): The TCP port to listen on
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        assert isinstance(datastore, DataStoreSystem), \
            "A system datastore instance must be provided for the data"
        assert isinstance(jobdict, DictProxy), \
            f"A SyncManager dict must be provided for job information"
        assert isinstance(hostname, str), "Hostname must be a string"
        assert isinstance(port, int), "Port must be an integer"
        assert port > 0 and port < 65536, "Port must be between 1 and 65536"

        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__datastore = datastore
        self.__jobdict = jobdict
        self.__hostname= hostname or "localhost"
        self.__port = port
        self.__webserver: HTTPServer | None = None

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################


    ###########################################################################
    #
    # Web Server Functions (for thread start/stop)
    #
    ###########################################################################
    #
    # run_web_server
    #
    def run_web_server(self) -> None:
        '''
        Run the web server

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        _telemetry_web_server = partial(
            SimplePage,
            data_func=self.__datastore.export_to_json,
            content_type="application/json"
        )

        self.__webserver = HTTPServer(
            (self.__hostname, self.__port),
            _telemetry_web_server
        )

        try:
            self.__webserver.serve_forever()
        except KeyboardInterrupt:
            pass

        self.__webserver.server_close()


    #
    # shutdown_web_server
    #
    def shutdown_web_server(self) -> None:
        '''
        Shut down the web server

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Try to end the web server
        if isinstance(self.__webserver, HTTPServer):
            self.__webserver.shutdown()


    ###########################################################################
    #
    # Manage status info
    #
    ###########################################################################
    #
    # run_thread
    #
    @staticmethod
    def run_thread(func=None):
        '''
        Quick and dirty thread to run the value update task

        Args:
            func (callable): Callable to run in the thread

        Returns:
            None

        Raises:
            None
        '''
        assert isinstance(func, Callable)
        assert callable(func)

        _thread = Thread(target=func)
        _thread.start()


    ###########################################################################
    #
    # Manage status info
    #
    ###########################################################################
    #
    # set_static
    #
    def set_static(
            self,
            name: str = "",
            value: Any = None
    ) -> None:
        '''
        Set a static telemetry entry

        Args:
            name (str): The name of the item to set
            value (Any): Value to set the item to

        Returns:
            None

        Raises:
            None
        '''
        assert name, "A name is required to set a value"

        self.__datastore.set(name=name, value=value)


    #
    # set_interval
    #
    def set_interval(
            self,
            name: str = "",
            func: Callable | None = None,
            interval: int = 3600
    ) -> None:
        '''
        Set a telemetry entry via a function run on an interval

        Args:
            name (str): The name of the item to set
            func (callable): Callable that returns the value to set
            interval (int): Interval, in seconds, of how often to update the
                value

        Returns:
            None

        Raises:
            None
        '''
        assert name, "A name is required to set a value"
        assert isinstance(func, Callable), \
            "A Function is required to update the value"
        assert isinstance(interval, int), "Interval must be an integer"
        assert interval > 0 and interval < 86401, \
            "Interval must be between 1 and 86400"

        # Create the entry with an empty value 
        self.__datastore.set(name=name, value=None)

        # Create a function to update the value
        def _update_telemetry_value():
            self.__datastore.set(name=name, value=func())

        # Schedule the function to update the value
        _job = schedule.every(interval).seconds.do(
            self.run_thread,
            _update_telemetry_value
        )

        _job.run()
        self.__jobdict[name] = _job


    #
    # get
    #
    def get(
            self,
            name: str = "",
            default: Any = None
    ) -> Any:
        '''
        Get a telemetry entry

        Args:
            name (str): The name of the item to get
            default (Any): A default value to use if the item not found

        Returns:
            Any: The value of the item (or a default)

        Raises:
            None
        '''
        assert name, "A name is required to get a value"
        
        return self.__datastore.get(name=name, default=default)


    #
    # delete
    #
    def delete(
            self,
            name: str = "",
            subtree: bool = False
    ) -> Any:
        '''
        Delete a telemetry entry

        Args:
            name (str): The name of the item to delete
            subtree (bool): If True, delete any child entries of name

        Returns:
            None

        Raises:
            None
        '''
        assert name, "A name is required to delete a value"

        # Remove any schedules
        if name in self.__jobdict:
            schedule.cancel_job(self.__jobdict[name])
            del self.__jobdict[name]

        self.__datastore.delete(name=name)


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
