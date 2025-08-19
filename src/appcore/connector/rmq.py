#!/usr/bin/env python3
'''
Rabbit MQ interface

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
import pika
import pika.channel
import pika.frame
import pika.adapters.blocking_connection
from pika.exchange_type import ExchangeType
import ssl
import os.path
import uuid
import sys
import signal

# Local app modules
import appcore.exception as exception

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
MAX_MSG_SIZE = 104857600

#
# Global Variables
#


###########################################################################
#
# RMQInterface Class Definition
#
###########################################################################
class RMQInterface():
    '''
    Class to describe the interface to RabbitMQ.

    A wrapper around Rabbit MQ

    Attributes:
        vhost (str): vhost to use
        queue (str): Name of the queue to use for this connection
        queue_ttl (int): If > 0, creat an ephemeral queue that will
            disappear after queue_ttl seconds
        message_handler (Callable): Function to run when message
            received in the listener
    '''

    #
    # __init__
    #
    def __init__(
            self, 
            username: str = "",
            password: str = "",
            host: str = "locahost",
            port: int = 0,
            vhost: str = "/",
            ca_cert: str = "",
            cert_pub: str ="",
            cert_key: str = "",
            connection_name: str = "appcore_default",
            exchange: str = "",
            routing_key: str = "",
            queue: str = "",
            queue_ttl: int = 0,
            message_handler: Callable | None = None
    ):
        '''
        Initialises the instance.

        Args:
            username (str): Username for connection to RMQ server
            password (str): Password for connection to RMQ server
            host (str): Rabbit MQ server to connect to
            port (int): Port to connect to RMQ server on.  If not set will be
                set to the default port for the connection type
            vhost (str): vhost to use
            ca_cert (str): If set along with cert_pub and cert_key then a
                secure connection will be established
            cert_pub (str): If set along with ca_cert and cert_key then a
                secure connection will be established
            cert_key (str): If set along with ca_cert and cert_pub then a
                secure connection will be established
            connection_name (str): A name for the connection,
            exchange (str): If set an exchange will be created with this name
            routing_key (str): If defined use this routing key
            queue (str): Name of the queue to use for this connection
            queue_ttl (int): If > 0, creat an ephemeral queue that will
                disappear after queue_ttl seconds
            message_handler (Callable): Function to run when message
                received in the listener

        Returns:
            None

        Raises:
            None
        '''
        # Private Attributes
        self.__username = username
        self.__password = password
        self.__host = host

        self.__ca_cert = ca_cert
        self.__cert_pub = cert_pub
        self.__cert_key = cert_key
        self.__connection_name = connection_name
        self.__exchange = exchange
        self.__routing_key = routing_key

        if not isinstance(port, int) and port < 1 or port > 65535:
            if self.__ca_cert and self.__cert_pub and self.__cert_key:
                # Default to secure
                self.__port = 5671
            else:
                # Default to normal
                self.__port = 5672
        else:
            # User supplied port
            self.__port = port

        # Connection management attributes
        self.__connection: \
            None | pika.BlockingConnection | pika.SelectConnection = None
        self.__channel:  pika.channel.Channel | \
            pika.adapters.blocking_connection.BlockingChannel | None = None

        self.__use_select_connection = False
        self.__closing = False
        self.__consuming = False

        # Attributes
        self.vhost = vhost
        self.queue = queue
        self.queue_ttl = queue_ttl
        self.message_handler = message_handler




    ###########################################################################
    #
    # Properties
    #
    ###########################################################################



    ###########################################################################
    #
    # Usage receipes
    #
    ###########################################################################
    #
    # listen
    #
    def listen(
            self,
            use_select: bool = False):
        '''
        Set up the connection and start listening for messages

        Args:
            use_select (bool): True = Use Select Connection Adapter, False = 
                Use Blocking Connection Adapter

        Returns:
            None

        Raises:
            AssertionError
                When port is not int or str and not between 1 and 65535
                When message handler is not a callable
        '''
        self.__use_select_connection = use_select

        self.connect()

        if self.__use_select_connection:
            self.__connection.ioloop.start()
        else:
            self.open_channel()
            self.setup_exchange()
            self.setup_queue()
            self.start_consuming()


    #
    # stop
    #
    def stop(self):
        '''
        Stop and shutdown the connection to RabbitMQ

        Parameters:
            None

        Return Value:
            None
        '''
        if not self.__closing:
            self.__closing = True
            if self.__consuming:
                self.stop_consuming()

            if self.__use_select_connection: 
                if self.__connection: self.__connection.ioloop.stop()


    #
    # send
    #
    def send(self, msg_frame=None, privkey_callback=None, enc_key=None):
        '''
        Send a message

        Parameters:
            msg_frame: An instance of the Rabbit_Frame class
            private_key: The private key to use for signing
            enc_key: Encryption key to encrypt the message

        Return Value:
            None
        '''
        if not msg_frame: raise RMQ_Error("Send: No message frame provided. Discarding")
        if not self.queue:
            raise RMQ_Error(f"Send: No queue identified for sending message (ID={msg_frame.message_id}). Discarding.")
        
        if not privkey_callback:
            raise RMQ_Error(f"Send: No credentials provided to sign message (ID={msg_frame.message_id}). Discarding.")

        self.__use_select_connection = False

        # Sign the message
        self.sign_message(msg_frame=msg_frame, privkey_callback=privkey_callback)

        # Encrypt the message
        self.encrypt_message(msg_frame=msg_frame, enc_key=enc_key)

        # Send the message
        self.connect()
        self.open_channel()
        self.setup_exchange()
        self.setup_queue()

        if not msg_frame.message_id: msg_frame.message_id = str(uuid.uuid4())
        self.send_message(body=msg_frame.body, properties=msg_frame.to_message())
        self.close_channel()
        self.close_connection()


    #
    # send_keepalive
    #
    def send_keepalive(self):
        '''
        Send a keepalive message

        Parameters:
            None

        Return Value:
            None
        '''
        self.__use_select_connection = False

        # Send the message
        self.connect()
        self.open_channel()
        self.setup_exchange()
        self.setup_queue()

        _properties = pika.BasicProperties(
            content_type='application/json',
            type=rabbit_message.MCP_KEEPALIVE,
            message_id=str(uuid.uuid4())
        )

        if self.__channel:
            self.__channel.basic_publish(exchange=self._exchange, routing_key=self._routing_key,
                body=rabbit_message.MCP_KEEPALIVE, properties=_properties)

        self.close_channel()
        self.close_connection()


    #
    # receive
    #
    def receive(self, timeout=0, pubkey_callback=None, enc_key=None):
        '''
        Receive a single message

        Parameters:
            timeout: Number of seconds to wait for a message before giving up
            pubkey_callback: Function to look up the public key
            enc_key: Encryption key to decrypt the message

        Return Value:
            object: An instance of the message frame class
        '''
        if not pubkey_callback: return None

        self.__msg_frame = None

        # Set up signal handler for an alarm to create the timeout
        def timeout_handler(signum, frame):
            raise RMQ_Timeout("Timeout")

        signal.signal(signal.SIGALRM, timeout_handler)


        # Callback to process a message when it arrives
        def message_from_remote(channel, method, properties, body, rmq=self, pubkey_callback=pubkey_callback, enc_key=enc_key):
            ''' Message received from remote rabbit server  '''
             # Disable the alarm as we have received a message
            signal.alarm(0)

            # Process the message
            try:
                # Get our message frame from the Rabbit MQ message body
                rmq.__msg_frame = rmq.extract_message_frame(properties=properties, body=body)
            
                # Decrypt 
                rmq.decrypt_message(msg_frame=rmq.__msg_frame, enc_key=enc_key)

                # Verify the message signature
                rmq.verify_message(msg_frame=rmq.__msg_frame, pubkey_callback=pubkey_callback)
            except RMQ_Error as err:
                rmq.ack_message(method.delivery_tag)
                rmq.stop()
                raise RMQ_Error(err)
            except RMQ_Warning as err:
                rmq.ack_message(method.delivery_tag)
                rmq.stop()
                raise RMQ_Warning(err)

            # Close down the connection
            # rmq.ack_message(method.delivery_tag)
            rmq.stop()


        # Set up the callback, and set an alarm
        self.on_message_callback = message_from_remote
        signal.alarm(timeout)

        # Wait for the reply message
        try:
            self.listen(use_select=True)
        except RMQ_Timeout:
            # Timed out waiting for a message
            self.stop()

        return self.__msg_frame


    ###########################################################################
    #
    # Connection Handling
    #
    ###########################################################################
    #
    # connect
    #
    def connect(self):
        '''
        Create a connection to the server

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError
                When username is not supplied or not a string
                When password is not supplied or not a string
                When RMQ server is not supplied or not a string
                When vhost is not supplied or not a string
                When ca_cert file cannot be found
                When cert_pub file cannot be found
                When cert_key file cannot be found
        '''
        assert not isinstance(self.__username, str) and self.__username, \
            "username not supplied"
        assert not isinstance(self.__password, str) and self.__password, \
            "password not supplied"
        assert not isinstance(self.__host, str) and self.__host, \
            "Rabbit MQ host not supplied"
        assert not isinstance(self.vhost, str) and self.vhost, \
            "vhost not supplied"

        # Set up credentials
        _credentials = pika.PlainCredentials(self.__username, self.__password)

        if self.__ca_cert and self.__cert_pub and self.__cert_key:
            # Try to create a session over TLS
            assert os.path.isfile(self.__ca_cert), \
                f"cannot find CA Cert file: {self.__ca_cert}"
            assert os.path.isfile(self.__cert_pub), \
                f"cannot find Cert file: {self.__cert_pub}"
            assert os.path.isfile(self.__cert_key), \
                f"cannot find Cert Key file: {self.__cert_key}"

            # Create the context for SSL
            _context = ssl.create_default_context(cafile=self.__ca_cert)
            _context.load_cert_chain(self.__cert_pub, self.__cert_key)

            _context.check_hostname = False
            _context.verify_mode = ssl.CERT_REQUIRED

            _ssl_options = pika.SSLOptions(_context)

            # Set the connection parameters
            _conn_params = pika.ConnectionParameters(
                host=self.__host,
                port=self.__port,
                credentials=_credentials,
                virtual_host=self.vhost,
                ssl_options=_ssl_options,
                client_properties={
                    'connection_name': self.__connection_name,
                }
            )
        else:
            # Set the connection parameters
            _conn_params = pika.ConnectionParameters(
                host=self.__host,
                credentials=_credentials,
                virtual_host=self.vhost,
                client_properties={
                    'connection_name': self.__connection_name,
                }
            )
        
        # Create a connection
        if self.__use_select_connection:
            self.__connection = pika.SelectConnection(
                parameters=_conn_params,
                on_open_callback=self.on_connection_open,
                on_open_error_callback=self.on_connection_open_error,
                on_close_callback=self.on_connection_closed
            )

        else:
            self.__connection = pika.BlockingConnection(_conn_params)
    
        # Check the connection is OK
        if not self.__connection:
            raise exception.RMQConnectionError(
                "Unable to establish RabbitMQ Connection"
            )


    #
    # close_connection
    #
    def close_connection(self):
        '''
        Close a connection to the server

        Args:
            None

        Returns:
            None

        Raises:
            RMQConnectionError
               when the connection is not the correct type
        '''
        self.__consuming = False

        if self.__use_select_connection:
            if not isinstance(self.__connection, pika.SelectConnection):
                raise exception.RMQConnectionError(
                    "Connection is not select connection"
                )

            if self.__connection and not self.__connection.is_closing and \
                        not self.__connection.is_closed:
                self.__connection.close()
        else:
            if not isinstance(self.__connection, pika.BlockingConnection):
                raise exception.RMQConnectionError(
                    "Connection is not blocking connection"
                )

            if not self.__connection.is_closed: self.__connection.close()



    #
    # on_connection_open
    #
    def on_connection_open(
            self,
            connection: pika.BlockingConnection | pika.SelectConnection
    ):
        '''
        Callback for when connection has been established

        Args:
            connection (BlockingConnection | SelectionConnection): A handle to
                the connection object

        Returns:
            None

        Raises:
            None
        '''
        # Ignore connection - Already stored as self.__connection
        del connection

        self.open_channel()


    #
    # on_connection_open_error
    #
    def on_connection_open_error(
            self,
            connection: pika.BlockingConnection | pika.SelectConnection,
            err: str | Exception):
        '''
        Callback for when connection fails

        Args:
            connection (BlockingConnection | SelectionConnection): A handle to
                the connection object
            err (str | Exception): Reason why the connection failed

        Returns:
            None

        Raises:
            RMQConnectionError
               when the connection attempt has failed
        '''
        # Ignore connection - Already stored as self.__connection
        del connection

        raise exception.RMQConnectionError(
            f"Unable to establish RabbitMQ Connection: {str(err)}"
        )


    #
    # on_connection_closed
    #
    def on_connection_closed(
            self,
            connection: pika.BlockingConnection | pika.SelectConnection,
            err: str | Exception
    ):
        '''
        Callback for when connection closes

        Args:
            connection (BlockingConnection | SelectionConnection): A handle to
                the connection object
            err (Exception): Reason why the connection was closed

        Returns:
            None

        Raises:
            RMQConnectionError
               when the connection is not the correct type
        '''
        # Ignore connection - Already stored as self.__connection
        # Ignore err - Unused
        del connection
        del err

        self.__channel = None
        if self.__closing:
            # Should only be here for select connections
            if not isinstance(self.__connection, pika.SelectConnection):
                raise exception.RMQConnectionError(
                    "Connection is not select connection"
                )

            self.__connection.ioloop.stop()


    ###########################################################################
    #
    # Channel Handling
    #
    ###########################################################################
    #
    # open_channel
    #
    def open_channel(self):
        '''
        Open a channel to the server

        Args:
            None

        Returns:
            None

        Raises:
            RMQConnectionError
               when the connection is not the correct type
        '''
        if self.__use_select_connection:
            if not isinstance(self.__connection, pika.SelectConnection):
                raise exception.RMQConnectionError(
                    "Connection is not select connection"
                )

            self.__connection.channel(on_open_callback=self.on_channel_open)
        else:
            if not isinstance(self.__connection, pika.BlockingConnection):
                raise exception.RMQConnectionError(
                    "Connection is not blocking connection"
                )

            self.__channel = self.__connection.channel()



    #
    # close_channel
    #
    def close_channel(self):
        '''
        Close a channel

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        if self.__channel: self.__channel.close()
        self.__channel = None


    #
    # on_channel_open
    #
    def on_channel_open(
            self,
            channel: pika.channel.Channel
    ):
        '''
        Callback for when the channel is opened

        Args:
            channel (channel): Handle to the channel that was opened

        Returns:
            None

        Raises:
            None
        '''
        self.__channel = channel
        self.__channel.add_on_close_callback(self.on_channel_closed)
        self.setup_exchange()


    #
    # on_channel_closed
    #
    def on_channel_closed(
            self,
            channel: pika.channel.Channel,
            err: Exception
        ):
        '''
        Callback for when the channel closes

        Args:
            channel (Channel) : Handle to the channel that was closed
            err (Exception): Reason for the channel closing

        Returns:
            None

        Raises:
            None
        '''
        # Ignore channel - Already stored as self.__channel
        # Ignore err - Unused
        del channel
        del err

        self.close_connection()


    ###########################################################################
    #
    # Exchange Handling
    #
    ###########################################################################
    #
    # setup_exchange
    #
    def setup_exchange(self):
        '''
        Set up the exchange for use

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        def setup_exchange_callback(frame):
            self.on_exchange_declareok(frame)

        if not self.__exchange:
            # We will bypass the exchange and send to the queue
            self.__routing_key = self.queue
            if self.__use_select_connection: self.setup_queue()
        else:
            if self.__use_select_connection:
                if isinstance(self.__channel, pika.channel.Channel): 
                    self.__channel.exchange_declare(
                        exchange=self.__exchange,
                        exchange_type=ExchangeType.topic,
                        callback=setup_exchange_callback
                    )
            else:
                if self.__channel: self.__channel.exchange_declare(
                    exchange=self.__exchange,
                    exchange_type=ExchangeType.topic)


    #
    # on_exchange_declareok
    #
    def on_exchange_declareok(
            self,
            frame: pika.frame.Frame
    ):
        '''
        Set up the exchange for use

        Args:
            frame: (Frame) Exchange.DeclareOk response frame

        Returns:
            None

        Raises:
            None
        '''
        # Ignore frame - Unused
        del frame

        # Nothing to do - Can be overridden if need be...
        self.setup_queue()


    ###########################################################################
    #
    # Queue Handling
    #
    ###########################################################################
#
# FIX BELOW
#

    #
    # setup_queue
    #
    def setup_queue(self):
        '''
        Declare a queue

        Parameters:
            None

        Return Value:
            None
        '''
        def setup_queue_callback(frame):
            self.on_queue_declareok(frame)

        if self.queue_ttl > 0:
            _declare_args = {
                "x-expires": self.queue_ttl * 1000
            }
        else: 
            _declare_args = {
                "x-queue-type": "quorum"
            }

        _queue_res = None

        if self._use_select_connection:
            if self.queue_ttl > 0:
                if self.__channel:
                    _queue_res = self.__channel.queue_declare(queue=self.queue, durable=False, auto_delete=True,
                            arguments=_declare_args, callback=setup_queue_callback)
            else:
                if self.__channel: 
                    _queue_res = self.__channel.queue_declare(queue=self.queue, durable=True, arguments=_declare_args, 
                            callback=setup_queue_callback)
            
            if _queue_res and _queue_res.method:
                self.queue_message_count = _queue_res.method.message_count

        else:
            if self.queue_ttl > 0:
                if self.__channel:
                    _queue_res = self.__channel.queue_declare(queue=self.queue, durable=False, auto_delete=True,
                            arguments=_declare_args)
            else:
                if self.__channel:
                    _queue_res = self.__channel.queue_declare(queue=self.queue, durable=True, arguments=_declare_args)

            if _queue_res and _queue_res.method:
                self.queue_message_count = _queue_res.method.message_count

            if self._exchange:
                if self.__channel: self.__channel.queue_bind(self.queue, self._exchange, routing_key=self._routing_key)

            self.set_qos()


    #
    # on_queue_declareok
    #
    def on_queue_declareok(self, frame):
        '''
        Queue declared OK callback

        Parameters:
            frame: (Unused) queue.DeclareOk response frame
            userdata: Extra user data (queue name)

        Return Value:
            None
        '''
        def bind_callback(frame):
            self.on_bindok(frame)

        if self._exchange:
            if self.__channel: self.__channel.queue_bind(self.queue, self._exchange, routing_key=self._routing_key,
                    callback=bind_callback)
        else:
            self.set_qos()


    #
    # on_bindok
    #
    def on_bindok(self, frame):
        '''
        Callback for when Bind is successful

        Parameters:
            frame: (Unused) Queue.BindOk response frame

        Return Value:
            None
        '''
        self.set_qos()


    #
    # set_qos
    #
    def set_qos(self):
        '''
        Set QOS for a queue

        Parameters:
            None

        Return Value:
            None
        '''
        if self._use_select_connection:
            if self.__channel: self.__channel.basic_qos(prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok)
        else:
            if self.__channel: self.__channel.basic_qos(prefetch_count=self._prefetch_count)


    #
    # on_bindok
    #
    def on_basic_qos_ok(self, frame):
        '''
        Callback for when setting of QOS is successful

        Parameters:
            frame: (Unused) Queue.BindOk response frame

        Return Value:
            None
        '''
        self.start_consuming()


    ###########################################################################
    #
    # Receive messages on the queue
    #
    ###########################################################################
    #
    # start_consuming
    #
    def start_consuming(self):
        '''
        Looping function to consume messages...

        Parameters:
            None

        Return Value:
            None
        '''
        if not self.__channel: return

        if self._use_select_connection:
            self.__channel.add_on_cancel_callback(self.on_consumer_cancelled)

        self._consumer_tag = self.__channel.basic_consume(self.queue, self.on_message_callback)
        self._consuming = True

        if not self._use_select_connection: self.__channel.start_consuming()


    #
    # stop_consuming
    #
    def stop_consuming(self):
        '''
        Stop consuming messages (end start_consuming loop)

        Parameters:
            None

        Return Value:
            None
        '''
        if self.__channel:
            def cancel_callback(frame):
                self.on_cancelok(frame)

        self.__channel.basic_cancel(self._consumer_tag, cancel_callback)


    #
    # on_consumer_cancelled
    #
    def on_consumer_cancelled(self, method_frame):
        '''
        When RabbitMQ sends a Basic.Cancel for a consumer

        Parameters:
            method_frame: The Basic.Cancel frame

        Return Value:
            None
        '''
        if self.__channel:
            self.__channel.close()


    def on_cancelok(self, frame):
        '''
        When RabbitMQ acknowledges channel cancellation

        Parameters:
            frame: The Basic.CancelOk frame

        Return Value:
            None
        '''
        self._consuming = False
        self.close_channel()


    #
    # ack_message
    #
    def ack_message(self, delivery_tag=0):
        '''
        Acknowledge a message has been processed

        Parameters:
            delivery_tag: delivery_tag of the message to acknowledge
        
        Return Value:
            None
        '''
        if not self.__channel: return
        if delivery_tag < 1: return

        if self.__channel.is_open:
            self.__channel.basic_ack(delivery_tag=delivery_tag)
    

    #
    # nack_message
    #
    def nack_message(self, delivery_tag=0):
        '''
        Reject/Requeu a message due to a transient processing failure

        Parameters:
            delivery_tag: delivery_tag of the message to reject
        
        Return Value:
            None
        '''
        if not self.__channel: return
        if delivery_tag < 1: return

        if self.__channel.is_open:
            self.__channel.basic_nack(delivery_tag=delivery_tag, multiple=False, requeue=True)
    

    ###########################################################################
    #
    # Send messages to the queue
    #
    ###########################################################################
    #
    # send_message
    #
    def send_message(self, body="", properties=None):
        '''
        Send a message

        Parameters:
            body: The message body
            properties: The properties for the message

        Return Value:
            None
        '''
        # Make sure the message size isn't too big!
        if sys.getsizeof(body) > MAX_MSG_SIZE:
            raise RMQ_Error("Message is too large")

        # Send it
        if self.__channel: self.__channel.basic_publish(exchange=self._exchange, routing_key=self._routing_key,
            body=body, properties=properties)


    ###########################################################################
    #
    # Message Processing - Message Format
    #
    ###########################################################################
    #
    # extract_message_frame
    #
    def extract_message_frame(self, properties=None, body=None):
        '''
        Extract the message frame from the body

        Parameters:
            properties: The message properties
            body: The message body

        Return Value:
            object: An instance of the message frame class
        '''
        # Import the message frame into our class
        msg_frame = rabbit_frame.Rabbit_Frame()
        if not msg_frame.from_message(properties=properties, body=body):
            raise RMQ_Warning(f"Message frame invalid (ID={properties.message_id}). Discarding.")
        
        return msg_frame


    ###########################################################################
    #
    # Message Processing - Encryption/Signing
    #
    ###########################################################################
    #
    # encrypt_message
    #
    def encrypt_message(self, msg_frame=None, enc_key=None):
        '''
        Encrypt a message

        Parameters:
            msg_frame: An instance of the message frame class
            queue: Queue the message will be sent on
            enc_key: The encryption key

        Return Value:
            None (Message in frame is encrypted in place)
        '''
        # Encrypt the message
        if not msg_frame.encrypt(key=enc_key):
            raise RMQ_Warning(f"Unable to encrypt message.  Unable to process the message (ID={msg_frame.message_id}). Discarding.")


    #
    # decrypt_message
    #
    def decrypt_message(self, msg_frame=None, enc_key=None):
        '''
        Decrypt a message - If not encrypted, will leave the message alone

        Parameters:
            msg_frame: An instance of the message frame class
            queue: Queue the message arrive on
            enc_key: The encryption key for decryption

        Return Value:
            None (Message in frame is unencrypted in place)
        '''
        if not enc_key and msg_frame.encrypted:
            raise RMQ_Warning(f"No key provided, message is encrypted. Unable to process the message (ID={msg_frame.message_id}). Discarding.")

        if not msg_frame.decrypt(key=enc_key):
            raise RMQ_Warning(f"Unable to decrypt message (ID={msg_frame.message_id}). Discarding.")


    #
    # sign_message
    #
    def sign_message(self, msg_frame=None, privkey_callback=None):
        '''
        Create the message signature

        Parameters:
            msg_frame: An instance of the message frame class
            privkey_callback: Callback to get the private key from the datastore

        Return Value:
            None
        '''
        if not msg_frame: raise RMQ_Warning(f"Sign Message: No message provided.")
        
        if not self.me:
            raise RMQ_Warning(f"Sign Message: Unable to determine IAS Appliance ID (ID={msg_frame.message_id}). Discarding.")

        if not privkey_callback:
            raise RMQ_Warning(f"Unable to determine signing credentials (ID={msg_frame.message_id}). Discarding.")

        msg_frame.sender = self.me
        _private_key = privkey_callback(appliance_id=msg_frame.sender, is_private_key=True)
        if not _private_key:
            raise RMQ_Warning(f"Unable to retreive signing credentials (ID={msg_frame.message_id}). Discarding.")

        # Sign the message
        if not msg_frame.sign(private_key=_private_key):
            raise RMQ_Warning(f"Unable to sign message (ID={msg_frame.message_id}). Discarding.")


    #
    # verify_message
    #
    def verify_message(self, msg_frame=None, pubkey_callback=None):
        '''
        Verify the message signature

        Parameters:
            msg_frame: An instance of the message frame class
            public_key: The public key of the sender to use to verify the signature

        Return Value:
            None
        '''
        if not pubkey_callback:
            raise RMQ_Warning(f"Unable to verify message sender (ID={msg_frame.message_id}). Discarding.")

        _public_key = pubkey_callback(appliance_id=msg_frame.sender, is_private_key=False)
        if not _public_key: 
            raise RMQ_Warning(f"Unable to verify message sender (ID={msg_frame.message_id}). Discarding.")

        # Verify the signature
        if not msg_frame.verify(public_key=_public_key):
            raise RMQ_Warning(f"Unable to verify message (ID={msg_frame.message_id}). Discarding.")


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
