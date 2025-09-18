# AppCore
## Release Notes

__Version 1.0.13__
Released: 2025-09-16
* New - Add put_frame method to task_queue to allow a raw frame to be sent
* Change - 'send' function modified to be query function (expecting immediate respone)


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
