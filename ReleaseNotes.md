# AppCore
## Release Notes


__Version 2.0.1__
Released: 2025-01-12
* New - Pickle - Added to_pickle, from_pickle conversion functions


__Version 2.0.0__
Released: 2026-01-08
* Change - Removed most submodules to separate modules 


__Version 1.0.23__
Released: 2025-10-15
* Change - RMQ - Transient queues declared as Durable

The following modules remain in AppCore:
- Conversion
  - A collection of conversion functions
    - set_value - Ensure a value is set to the specific DataType
    - get_value_type - Get the data type of a value
    - to_json, from_json - Convert data to and from JSON
    - from_base64, from_base64 - Convert data to and from base 64
- Helpers
  - A collection of general functions
    - timestamp - Generate a timestamp


__Version 1.0.22__
Released: 2025-10-08
* Change - Task - Cleanup modified to try terminating, then killing a process
* Fix - Telemetry - Don't store webserver info in Telemtry instance


__Version 1.0.21__
Released: 2025-10-01
* Fix - RMQInterface - Change 'receive' function to use basic_consume


__Version 1.0.20__
Released: 2025-09-25
* Fix - RMQInterface - Correct 'receive' function connect/disconnect
* Fix - TaskQueue - Correct calculations for timeouts and keepalives


__Version 1.0.19__
Released: 2025-09-25
* Fix - RMQInterface - Moved all double underscore properties to single underscore properties


__Version 1.0.18__
Released: 2025-09-24
* Fix - Added 'port' connection for AMQP


__Version 1.0.17__
Released: 2025-09-24
* New - Added 'receive' method to RMQ to receive a single message


__Version 1.0.16__
Released: 2025-09-23
* New - Added exception ZMQRequestTimeOut
* Change - Add internal keepalive processing for queues
* Change - Add internal keepalive via telemetry for watchdog 'dicts'


__Version 1.0.15__
Released: 2025-09-22
* Change - Modified for compatability with 3.8


__Version 1.0.14__
Released: 2025-09-19
* Delete - Remove 'send' function
* New - Add 'request' and 'query' functions
  * A 'query' is a query for which a response is expected immediately
  * A 'request' is a query for which the response may take time.  There is the option to time out the request. 


__Version 1.0.13__
Released: 2025-09-16
* New - Add put_frame method to task_queue to allow a raw frame to be sent
* Change - 'send' function modified to be query function (expecting immediate response)


__Version 1.0.12__
Released: 2025-09-15
* Fix - Datastore decryption failing due to incorrect type


__Version 1.0.11__
Released: 2025-09-15
* New - Added type JSON types


__Version 1.0.10__
Released: 2025-09-14
* Change - 'timestamp' moved to util.functions


__Version 1.0.9__
Released: 2025-09-13
* New - ZMQ Add 'send' function (expects immediate response)
* Fix - ZMQ 'request' uses out of band responses to handle slow queries
* New - ZMQ Add 'response' function (to provide response to 'request')
* Fix - ZMQ 'server' separated in 'server' (initialisation) and 'listen' (the listen loop)
* Fix - ZMQ Client Timeout
* Change - ZMQ - Using DEALER/ROUTER rather than REQ/REP
* Fix - Check connection state in RMQ before beginning 'listen'
* Change - RMQ - Move 'use_select' to initiation instead of when starting listener


__Version 1.0.8__
Released: 2025-09-10
* New - Add list function to datastores
* Fix - get_value_type checks boolean before int (bool is subclass of int)
* Fix - Base64 Conversion now expects string to convert from base 64
* New - Add Rabbit MQ 'send'


__Version 1.0.7__
Released: 2025-08-26
* New - Add Memfile utility
* Fix - from_json option to import without container
* Fix - Dependencies in pyproject.toml
* New - Add conversion to/from base 64
* Fix - Assertions in RMQ interface
* Add - thread_only option to Watchdog - Allow more complex datastructures (eg classes) in thread arguments
* Fix - TaskQueue timeout now raises exceptions correctly
* Fix - RMQ connector use threadsafe call for ACK/NACK


__Version 1.0.6__
Released: 2025-08-20
* RMQ Interface added for comms


__Version 1.0.5__
* Expose Manager Watchdog so it can be used by top level process
* Watchdog shutdown event add to synch shutdown process
* ZMQ Interface added for comms

`
__Version 1.0.4__
* Watchdog shutdown stops all registered tasks


__Version 1.0.0__
* Initial Release
