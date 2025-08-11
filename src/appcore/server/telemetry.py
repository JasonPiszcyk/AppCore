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
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import urllib3

# Local app modules

# Imports for python variable type hints
from typing import Any, Callable
from multiprocessing.managers import DictProxy
from threading import Event as EventType
from appcore.datastore.system import DataStoreSystem
from appcore.multitasking.scheduler import Scheduler as SchedulerClass


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
def _update_telemetry_value(ds=None, name="", func=None):
    if not isinstance(ds, DataStoreSystem): return
    if not name: return
    if not callable(func): return

    ds.set(name=name, value=func())


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
            scheduler: SchedulerClass | None = None,
            hostname: str = "localhost",
            port: int = 8180,
            stop_event: EventType | None = None,
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
            scheduler (SchedulerClass): A scheduler to use for updating items
                based on an interval
            hostname (str): Used to identify interface to bind to
            port (int): The TCP port to listen on
            stop_event (Event): Event to signal the web server to stop
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            AssertionError:
                when a datastore is not provided
                when a dict is not provided to store jobs
                when a scheduler is not provided
                when the hostname is not a string
                when the port is not valid
                when an event is not provided

        '''
        assert isinstance(datastore, DataStoreSystem), \
            "A system datastore instance must be provided for the data"
        assert isinstance(jobdict, DictProxy), \
            f"A SyncManager dict must be provided for job information"
        assert isinstance(scheduler, SchedulerClass), \
            f"A scheduler must be provided for item updates"
        assert isinstance(hostname, str), "Hostname must be a string"
        assert isinstance(port, int), "Port must be an integer"
        assert port > 0 and port < 65536, "Port must be between 1 and 65536"
        assert stop_event, "stop_event must be provided"

        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__datastore = datastore
        self.__jobdict = jobdict
        self.__scheduler = scheduler
        self.__hostname= hostname or "localhost"
        self.__port = port
        self.__stop_event = stop_event
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
        _data_export = self.__datastore.export_to_json

        # Define a class to handle the web requests
        #####################################################################
        # WebServer Class
        #####################################################################
        class WebServer(BaseHTTPRequestHandler):
            ''' Class to return a single HTTP page with information '''
            #
            # do_GET
            #
            def do_GET(self) -> None:
                ''' Perform the get action '''
                # Only allow request to the root path
                if self.path != "/":
                    self.send_response(405)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    return

                # Create the response
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                _data = ""
                try:
                    _data = _data_export(container=False)
                    self.wfile.write(bytes(_data, "utf-8"))

                except:
                    pass

        #####################################################################
        # END -> WebServer Class
        #####################################################################

        self.__webserver = HTTPServer(
            (self.__hostname, self.__port),
            WebServer
        )

        while not self.__stop_event.is_set():
            self.__webserver.handle_request()

        self.__stop_event.clear()
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
        # Set the event to end the scheduler
        self.__stop_event.set()

        # Make a request so the event can be checked!
        _req_headers = {
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json",
        }

        # 'quit' on end not important.  Sends a request but doesn't perform
        # the esxport to provide data
        _uri = f"http://{self.__hostname}:{self.__port}/quit"
        urllib3.disable_warnings()
        try:
            _ = requests.get(
                _uri,
                headers=_req_headers,
                params={},
                verify=False
            )
        except:
            pass


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
        assert callable(func), "A Function is required to update the value"
        assert isinstance(interval, int), "Interval must be an integer"
        assert interval > 0 and interval < 86401, \
            "Interval must be between 1 and 86400"

        # Create the entry with an empty value 
        self.__datastore.set(name=name, value=None)

        # Create a function to update the value
        _kwargs = {
            "ds": self.__datastore,
            "name": name,
            "func": func
        }

        # Schedule the function to update the value
        _job = self.__scheduler.every(interval).seconds.run(
            func=_update_telemetry_value,
            kwargs=_kwargs
        )

        # Update the value now
        # _task.start()

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
            self.__scheduler.cancel(self.__jobdict[name])
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
