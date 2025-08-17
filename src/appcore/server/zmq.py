#!/usr/bin/env python3
'''
ZMQ Interface

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
import uuid
import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator

# Local app modules
from appcore.appcore_base import AppCoreModuleBase

# Imports for python variable type hints


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
CONTROL_ADDR_ = "ipc:///tmp/_local_receiver_control"


#
# Global Variables
#


###########################################################################
#
# ZMQInterface Class Definition
#
###########################################################################
class ZMQInterface(AppCoreModuleBase):
    '''
    Class to describe an interface to ZMQ.

    Creates a ZMQ connection server or client

    Attributes:
        None
    '''

    #
    # __init__
    #
    def __init__(
            self,
            *args,
            cert_dir: str = "",
            key_name: str = "",
            control_addr: str = "",
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            cert_dir (str): Specifies the directory for the certs for CURVE
                auth.  If not specified, auth is not used
            key_name (str): Name of the key to use for auth.  If not specified
                auth is not used
            control_addr (str): Address for the Control IPC Q 
            **kwargs (Undef): Keyword arguments to be passed to the constructor
                of the inherited process

        Returns:
            None

        Raises:
            None
        '''
        super().__init__(*args, **kwargs)

        # Private Attributes
        self.__zmq = zmq.Context()
        self.__cert_dir = cert_dir
        self.__key_name = key_name
        self.__control_addr = control_addr or \
                f"ipc:///tmp/_zmq-{str(uuid.uuid4())}"

        self.__auth = True if self.__cert_dir and self.__key_name else False

        # Attributes


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################


    ###########################################################################
    #
    # Server
    #
    ###########################################################################
    #
    # server
    #
    def server(self) -> None:
        '''
        A ZMQ 'Server' to receive requests and respond

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Connect to control channel (to allow exit of server)
        _control = self.__zmq.socket(zmq.PULL)
        _control.connect(self.__control_addr)

        # Configure the receiver
        _receiver = self.__zmq.socket(zmq.REP)

        # If cert_dir is set, configure auth
        if self.__auth:
            _auth = ThreadAuthenticator(self.__zmq, log=_logger)
            _auth.start()
            # auth.allow('127.0.0.1')
            _auth.configure_curve(domain='*', location=self.__cert_dir)
            _secret_key = f"{self.__cert_dir}/{self.__key_name}.key_secret"
            _public, _secret = zmq.auth.load_certificate(_secret_key)
            _receiver.curve_secretkey = _secret
            _receiver.curve_publickey = _public

    _listen = system_ds.get("LocalReceiver.listen", default="*")
    _port = system_ds.get("LocalReceiver.port", default="8155")
    _receiver.curve_server = True
    _receiver.bind(f"tcp://{_listen}:{_port}")

    # Initialize poll set
    poller = zmq.Poller()
    poller.register(_control, zmq.POLLIN)
    poller.register(_receiver, zmq.POLLIN)

    # Poll the ZMQ sockets and process info
    _logger.debug("Starting local receiver")

    _processing = True
    while _processing:
        _sockets = dict(poller.poll())
        if _control in _sockets and _sockets[_control] == zmq.POLLIN:
            message = _control.recv_string()
            if message == SHUTDOWN_MESSAGE:
                _logger.debug("Shutdown message received")
                _processing = False

        if _receiver in _sockets and _sockets[_receiver] == zmq.POLLIN:
            message = _receiver.recv_string()
            print(f"\nGot Message: {message}")
            _receiver.send_string(f"OK -> {message}")

    # Stop Auth
    _auth.stop()
    _logger.debug("Ending local receiver")





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
