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
from __future__ import annotations

# Shared variables, constants, etc

# System Modules
import uuid
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
CLIENT_RESPONSE_TIMEOUT = 30000

# Internal Query type
QUERY = b"QUERY"
REQUEST = b"REQUEST"

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
        message_handler (Callable): Callable to handle each received
            message.  Takes two parameters - the client id and the message.
            Returns a 'bytes' value
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
            query_handler: Callable | None = None,
            request_handler: Callable | None = None,
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
            query_handler (Callable): Callable to handle queries. The response
                is created and sent back immediately.
                Takes one parameter - The message.
                Returns a 'bytes' value
            request_handler (Callable): Callable to handle requests. The
                response is returned via the 'response' method which can be
                called separately to the handler.
                Takes three parameters - A ZMQ instance, the client id and the
                    message.
                Returns nothing
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
        self.__thread_auth: ThreadAuthenticator | None = None

        self.__address = address
        self.__port = port
        self.__cert_dir = cert_dir
        self.__server_key_name = server_key_name
        self.__client_key_name = client_key_name
        self.__control_addr = control_addr or "ipc:///tmp/_zmq-default-control"
        self.__control: SyncSocket | None = None
        self.__server: SyncSocket | None = None
        self.__client: SyncSocket | None = None

        if self.__cert_dir and self.__server_key_name:
            self.__auth = True
        else:
            self.__auth = False 

        # Attributes
        self.query_handler = query_handler
        self.request_handler = request_handler


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

        # Connect to control channel (to allow exit of server)
        self.__control = self.__zmq.socket(zmq.PULL)
        self.__control.connect(self.__control_addr)

        # Configure the receiver
        self.__server = self.__zmq.socket(zmq.ROUTER)

        # If cert_dir is set, configure auth
        if self.__auth:
            self.__thread_auth = ThreadAuthenticator(
                self.__zmq,
                log=self.logger
            )
            self.__thread_auth.start()
            # auth.allow('127.0.0.1')
            self.__thread_auth.configure_curve(
                domain='*',
                location=self.__cert_dir
            )
            _secret_key = f"{self.__cert_dir}/" + \
                    f"{self.__server_key_name}.key_secret"
            _public, _secret = zmq.auth.load_certificate(_secret_key)
            self.__server.curve_secretkey = _secret # type: ignore
            self.__server.curve_publickey = _public
            self.__server.curve_server = True

        if not self.__address: self.__address = "*"
        self.__server.bind(f"tcp://{self.__address}:{_port_int}")


    #
    # response
    #
    def response(
            self,
            client_id: bytes = b"",
            data: bytes = b"",
    ):
        '''
        Send a response to a request.  The response is out of band to allow
        the server to continue processing if the request was slow.

        For ZMQ this is a response to a previous request

        Args:
            _client_id: (bytes): The client being responded to
            data: (bytes): The data to send

        Returns:
            None

        Raises:
            ZMQServerNotConfiguredError:
                When the ZMQ server is not configured
         '''
        # Make sure the server has been configured
        if not self.__server:
            raise exception.ZMQServerNotConfiguredError(
                "ZMQ server not configured"
            )

        if not isinstance(client_id, bytes):
            raise exception.MessageFormatInvalidError(
                "Request ID must be in byte format"
            )

        if not isinstance(data, bytes):
            raise exception.MessageFormatInvalidError(
                "Message must be in byte format"
            )

        # Send the response
        self.__server.send_multipart([client_id, data])


    #
    # listen
    #
    def listen(
            self,
    ) -> None:
        '''
        Begin listening for messages

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError
                When port is not int or str and not between 1 and 65535
        '''
        # Make sure the server has been configured
        if not self.__server or not self.__control:
            raise exception.ZMQServerNotConfiguredError(
                "ZMQ server not configured"
            )

        # Initialize poll set
        _poller = zmq.Poller()
        _poller.register(self.__control, zmq.POLLIN)
        _poller.register(self.__server, zmq.POLLIN)

        # Poll the ZMQ sockets and process info
        self.logger.debug("Starting ZMQ listening server")

        _polling = True
        while _polling:
            _sockets = dict(_poller.poll())
            if self.__control in _sockets and \
                        _sockets[self.__control] == zmq.POLLIN:
                _msg = self.__control.recv_string()
                if _msg == SHUTDOWN_MESSAGE:
                    self.logger.debug("Shutdown message received")
                    _polling = False

            if self.__server in _sockets and \
                        _sockets[self.__server] == zmq.POLLIN:
                _msg = self.__server.recv_multipart()
                if len(_msg) != 4:
                    self.logger.error(
                        "Server: Incorrect message format. Discarding"
                    )
                    continue

                # Extract the message info (2nd entry is a null)
                _client_id = _msg[0]
                _msg_type = _msg[2]
                _data = _msg[3]

                if _msg_type == QUERY:
                    # In band query - Send response immediately
                    if callable(self.query_handler):
                        _resp = self.query_handler(_data)
                    else:
                        _resp = b""

                    self.__server.send_multipart([_client_id, _resp])
                    continue

                if _msg_type == REQUEST:
                    if callable(self.request_handler):
                        # Response is sent via a call to the 'response'
                        # method in the handler
                        self.request_handler(self, _client_id, _data)

                    continue

                self.logger.error(
                    "Server: Unknown query type. Discarding"
                )


        # Stop the ZMQ receiver
        if self.__thread_auth: self.__thread_auth.stop()
        self.logger.debug("ZMQ listening server stopped")


    #
    # listen_stop
    #
    def listen_stop(self) -> None:
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
    # _connect_client
    #
    def _connect_client(
            self,
            identity: bytes = b""
    ) -> SyncSocket:
        '''
        Create a client connection

        Args:
            identity (bytes): The identity for the socket

        Returns:
            SyncSocket: The connected socket

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
        _socket = self.__zmq.socket(zmq.DEALER)
        if identity: _socket.identity = identity

        if self.__auth:
            _client_key = f"{self.__cert_dir}/" + \
                    f"{self.__client_key_name}.key_secret"
            _public, _secret = zmq.auth.load_certificate(_client_key)
            _socket.curve_secretkey = _secret # type: ignore
            _socket.curve_publickey = _public

            _server_public_key = f"{self.__cert_dir}/" + \
                    f"{self.__server_key_name}.key"
            _server_public, _ = zmq.auth.load_certificate(_server_public_key)
            _socket.curve_serverkey = _server_public

        if not self.__address: self.__address = "127.0.0.1"
        _socket.connect(f"tcp://{self.__address}:{_port_int}")

        return _socket


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
            None
       '''
        self.__client = self._connect_client()


    #
    # query
    #
    def query(
            self,
            data: bytes = b""
    ) -> bytes:
        '''
        Send a query to a ZMQ Server - Response is immediate

        Args:
            data: (bytes): The query to send

        Returns:
            bytes - The response from the server

        Raises:
            ZMQClientNotConfiguredError:
                When the ZMQ client is not configured
            ZMQClientConnectionError:
                When the connection fails
            MessageFormatInvalidError
                When the message data is not valid
        '''
        # Make sure the client has been configured
        if not self.__client:
            raise exception.ZMQClientNotConfiguredError(
                "ZMQ client not configured"
            )

        if not isinstance(data, bytes):
            raise exception.MessageFormatInvalidError(
                "Message must be in byte format"
            )

        self.__client.send_multipart([b"", QUERY, data])

        if self.__client.poll(CLIENT_RESPONSE_TIMEOUT):
            _msg = self.__client.recv_multipart()
            if len(_msg) != 1:
                raise exception.MessageFormatInvalidError(
                    "Response format invalid"
                )

            # Extract the messge info
            if not isinstance(_msg[0], bytes):
                    raise exception.MessageFormatInvalidError(
                        "Response must be in byte format"
                    )

            return _msg[0]

        raise exception.ZMQClientConnectionError(
            "Connection to ZMQ server failed"
        )


    #
    # request
    #
    def request(
            self,
            data: bytes = b"",
            timeout: int = 0
    ) -> bytes:
        '''
        Send a request to a ZMQ Server.  The response is sent out of band
        to allow the server to continue processing if the request is slow.

        This function will block until the response is received or the timeout
        occurs.

        Args:
            data: (bytes): The data to send
            timeout (int): Number of seconds to wait for the response

        Returns:
            bytes - The response from the server

        Raises:
            ZMQClientNotConfiguredError:
                When the ZMQ client is not configured
            ZMQRequestTimeOut:
                When the connection timeout is reached
        '''
        # Make sure the client has been configured
        if not self.__client:
            raise exception.ZMQClientNotConfiguredError(
                "ZMQ client not configured"
            )

        if not isinstance(data, bytes):
            raise exception.MessageFormatInvalidError(
                "Message must be in byte format"
            )

        if not isinstance(timeout, int): timeout = 0

        # Create a request ID
        _request_id = uuid.uuid4().bytes

        # Poll timeout is in milliseconds (so modify the timeout)
        _poll_timeout = None
        if timeout > 0: _poll_timeout = timeout * 1000

        # Create a transient connection to wait indefinitely for the response
        _transient = self._connect_client(identity=_request_id)

        # Send a request for the session response
        _transient.send_multipart([_request_id, REQUEST, data])

        if _transient.poll(timeout=_poll_timeout):
            _resp = _transient.recv_multipart()
            if len(_resp) != 1:
                raise exception.MessageFormatInvalidError(
                    "Response format invalid"
                )

            # Extract the messge info
            if not isinstance(_resp[0], bytes):
                    raise exception.MessageFormatInvalidError(
                        "Response must be in byte format"
                    )

            _transient.disconnect(f"tcp://{self.__address}:{self.__port}")
            return _resp[0]

        raise exception.ZMQRequestTimeOut(
            "Request has timed out"
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
