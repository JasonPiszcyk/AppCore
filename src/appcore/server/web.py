#!/usr/bin/env python3
'''
Web - Basic web server

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
from http.server import BaseHTTPRequestHandler

# Local app modules

# Imports for python variable type hints
from typing import Callable

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
# SimplePage Class Definition
#
###########################################################################
class SimplePage(BaseHTTPRequestHandler):
    '''
    Class to return a single page with information

    A very basic web server

    Attributes:
        content_type (str): The content type header - This information is
            not validated so be careful
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            data_func: Callable | None = None,
            content_type: str = "text/html",
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            data_func (Callable): Function to return the data to be 
                displayed on the page
            content_type (str): The content type header
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__data_func = data_func

        # Attributes
        self.content_type = content_type


    #
    # do_GET
    #
    def do_GET(self) -> None:
        '''
        Perform the get action

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Only allow request to the root path
        if self.path != "/":
            self.send_response(405)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            return

        # Create the response
        self.send_response(200)
        self.send_header("Content-type", self.content_type)
        self.end_headers()

        _data = ""
        try:
            if callable(self.__data_func):
                _data = str(self.__data_func())

        except:
            pass

        self.wfile.write(bytes(_data, "utf-8"))


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
