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
import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator

# Local app modules
from appcore.appcore_base import AppCoreModuleBase
from appcore.conversion import ENCODE_METHOD, set_value
import appcore.exception as exception

# Imports for python variable type hints
from typing import Callable
from zmq import SyncSocket
from appcore.typing import DataType


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
SHUTDOWN_MESSAGE = "__SHUTDOWN_NOW__"
CLIENT_RESPONSE_TIMEOUT = 60

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
            address: str = "",
            port: int | str = "8155",
            cert_dir: str = "",
            server_key_name: str = "",
            client_key_name: str = "",
            control_addr: str = "",
            message_handler: Callable | None = None,
            **kwargs
    ):
        '''
        Initialises the instance.

        Args:
            *args (Undef): Unnamed arguments to be passed to the constructor
                of the inherited process
            address (str): The address to listen on or connect to
            port (str): Port used for the connection
            cert_dir (str): Specifies the directory for the certs for CURVE
                auth.  If not specified, auth is not used
            server_key_name (str): Name of the server key to use for auth.  If
                not specified auth is not used
            client_key_name (str): Name of the client key to use for auth.  If
                not specified auth is not used for the client
            control_addr (str): Address for the Control IPC Q
            message_handler (Callable): Callable to handle each received
                message.  Takes one parameter, the message of type 'bytes' and
                returns a 'bytes' value to be sent as a reponse to the request
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

        self.__address = address
        self.__port = port
        self.__cert_dir = cert_dir
        self.__server_key_name = server_key_name
        self.__client_key_name = client_key_name
        self.__control_addr = control_addr or "ipc:///tmp/_zmq-default-control"
        self.__message_handler = message_handler
        self.__client: SyncSocket | None = None

        if self.__cert_dir and self.__server_key_name:
            self.__auth = True
        else:
            self.__auth = False 

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
    def server(
            self,
            ) -> None:
        '''
        A ZMQ 'Server' to receive requests and respond

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError
                When port is not int or str and not between 1 and 65535
                When message handler is not a callable
        '''
        _port_int = set_value(
            data=self.__port,
            type=DataType.INT,
            default=0
        )
        if _port_int < 1 or _port_int > 65535:
            raise AssertionError("port must be between 1 and 65535")

        assert callable(self.__message_handler), \
            "A message handler callable must be provided"

        # Connect to control channel (to allow exit of server)
        _control = self.__zmq.socket(zmq.PULL)
        _control.connect(self.__control_addr)

        # Configure the receiver
        _receiver = self.__zmq.socket(zmq.REP)

        # If cert_dir is set, configure auth
        _auth = None
        if self.__auth:
            _auth = ThreadAuthenticator(self.__zmq, log=self.logger)
            _auth.start()
            # auth.allow('127.0.0.1')
            _auth.configure_curve(domain='*', location=self.__cert_dir)
            _secret_key = f"{self.__cert_dir}/" + \
                    f"{self.__server_key_name}.key_secret"
            _public, _secret = zmq.auth.load_certificate(_secret_key)
            _receiver.curve_secretkey = _secret # type: ignore
            _receiver.curve_publickey = _public
            _receiver.curve_server = True

        if not self.__address: self.__address = "*"
        _receiver.bind(f"tcp://{self.__address}:{_port_int}")

        # Initialize poll set
        _poller = zmq.Poller()
        _poller.register(_control, zmq.POLLIN)
        _poller.register(_receiver, zmq.POLLIN)

        # Poll the ZMQ sockets and process info
        self.logger.debug("Starting ZMQ listening server")

        _polling = True
        while _polling:
            _sockets = dict(_poller.poll())
            if _control in _sockets and _sockets[_control] == zmq.POLLIN:
                _msg = _control.recv_string()
                if _msg == SHUTDOWN_MESSAGE:
                    self.logger.debug("Shutdown message received")
                    _polling = False

            if _receiver in _sockets and _sockets[_receiver] == zmq.POLLIN:
                _msg = _receiver.recv()
                _resp = self.__message_handler(_msg)
                _receiver.send(_resp)

        # Stop the ZMQ receiver
        if _auth: _auth.stop()
        self.logger.debug("ZMQ listening server stopped")


    #
    # server_stop
    #
    def server_stop(self) -> None:
        '''
        Stop a ZMQ 'Server' to receive requests and respond

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self.logger.debug("Shutdown requested for listening server")

        # Create the control queue for the local receiver (to shut it down)
        _control = self.__zmq.socket(zmq.PUSH)
        _control.bind(self.__control_addr)
        _control.send_string(SHUTDOWN_MESSAGE)


    ###########################################################################
    #
    # Client
    #
    ###########################################################################
    #
    # client
    #
    def client(self) -> None:
        '''
        A ZMQ 'Client' to send requests and receive responses

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError
                When port is not int or str and not between 1 and 65535
        '''
        _port_int = set_value(
            data=self.__port,
            type=DataType.INT,
            default=0
        )
        if _port_int < 1 or _port_int > 65535:
            raise AssertionError("port must be between 1 and 65535")

        # Configure the client
        self.__client = self.__zmq.socket(zmq.REQ)

        if self.__auth:
            _client_key = f"{self.__cert_dir}/" + \
                    f"{self.__client_key_name}.key_secret"
            _public, _secret = zmq.auth.load_certificate(_client_key)
            self.__client.curve_secretkey = _secret # type: ignore
            self.__client.curve_publickey = _public

            _server_public_key = f"{self.__cert_dir}/" + \
                    f"{self.__server_key_name}.key"
            _server_public, _ = zmq.auth.load_certificate(_server_public_key)
            self.__client.curve_serverkey = _server_public

        if not self.__address: self.__address = "127.0.0.1"
        self.__client.connect(f"tcp://{self.__address}:{_port_int}")


    #
    # request
    #
    def request(
            self,
            data: bytes = b""
    ) -> bytes:
        '''
        Send a request to a ZMQ 'Client' 

        Args:
            data: (bytes): The data to send

        Returns:
            bytes - The response from the server

        Raises:
            ZMQClientNotConfiguredError:
                When the ZMQ client is not configured
        '''
        # Make sure the client has been configure
        if not self.__client:
            raise exception.ZMQClientNotConfiguredError(
                "ZMQ client not configured"
            )

        if isinstance(data, str):
            _byte_data = data.encode(ENCODE_METHOD)
        elif isinstance(data, bytes):
            _byte_data = data
        else:
            raise exception.MessageFormatInvalidError(
                "Data format is invalid"
            )

        self.__client.send(_byte_data)

        if self.__client.poll(CLIENT_RESPONSE_TIMEOUT):
            _resp = self.__client.recv()
            if not isinstance(_resp, bytes):
                raise exception.MessageFormatInvalidError(
                    "Response format is invalid"
                )

            return _resp

        raise exception.ZMQClientConnectionError(
            "Connection to ZMQ server failed"
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
