#!/usr/bin/env python3
'''
PyTest - Test of scheduling

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
# System Imports
import pytest
import time
import os
from datetime import datetime, timezone, timedelta

#
# Globals
#
TEST_FILE = "/tmp/test-scheduler.flag"

###########################################################################
#
# Functions to run as the schedule
#
###########################################################################
#
# Task to create a file
#
def create_file():
    with open(TEST_FILE, "w") as fp:
        fp.write("Scheduler test\n")


#
# Task to delete a file
#
def delete_file():
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


###########################################################################
#
# The tests...
#
###########################################################################
#
# Test the scheduler
#
class Test_Scheduler():
    #
    # Interval scheduler
    #
    def test_interval_schedule(self, manager, scheduler):
        delete_file()
        assert not os.path.exists(TEST_FILE)

        # Schedule the file to be created in 1 second
        scheduler.every().second.run(
            name="Scheduler Test - Create File",
            func=create_file,
            kwargs={}
        )

        time.sleep(2)
        assert os.path.exists(TEST_FILE)

        # Shutdown the scheduler before we delete the file (or it may be
        # recreated)
        manager.shutdown()

        delete_file()
        assert not os.path.exists(TEST_FILE)

    #
    # At scheduler
    #
    # def test_at_schedule(self, manager):
    #     # Start the scheduler
    #     _scheduler = manager.StartScheduler()

    #     delete_file()
    #     assert not os.path.exists(TEST_FILE)

    #     # Schedule the file to be created in 1 minute
    #     _task = manager.Thread(
    #         name = f"Create File",
    #         target = create_file
    #     )

    #     # _time = datetime.now(timezone.utc) + timedelta(minutes=1)
    #     _time = datetime.now() + timedelta(minutes=1)
    #     _scheduler.at(datetime.strftime(_time, "%H:%M")).run(_task)

    #     time.sleep(90)
    #     assert os.path.exists(TEST_FILE)

    #     manager.shutdown()

    #     delete_file()
    #     assert not os.path.exists(TEST_FILE)


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
