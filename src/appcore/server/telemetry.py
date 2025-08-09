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
from http.server import HTTPServer
from functools import partial

# Local app modules
from appcore.server.web import SimplePage

# Imports for python variable type hints
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
                streo the telemetry in
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
            "A system datastore instance must be provided"
        assert isinstance(hostname, str), "Hostname must be a string"
        assert isinstance(port, int), "Port must be an integer"
        assert port > 0 and port < 65536, "Port must be between 1 and 65536"

        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__datastore = datastore
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
# In case this is run directly rather than imported...
#
###########################################################################
'''
Handle case of being run directly rather than imported
'''
if __name__ == "__main__":
    pass
