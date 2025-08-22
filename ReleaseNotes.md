# AppCore
## Release Notes


__Version 1.0.7__
Released: 2025-MM-DD
* Fix - from_json option to import without container
* Fix - Dependencies in pyproject.toml
* New - Add conversion to/from base 64
* Fix - Assertions in RMQ interface
* Add - thread_only option to Watchdog - Allow more complex datastructures (eg classes) in thread arguments


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
