# AppCore
## Release Notes


__Version 1.0.8__
Released: 2025-MM-DD
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
