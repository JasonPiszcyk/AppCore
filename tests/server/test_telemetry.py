#!/usr/bin/env python3
'''
PyTest - Test of telemetry

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

import appcore.datastore.exception as ds_exception

#
# Globals
#
BASE_URI = "http://127.0.0.1:8180/"

UPDATE_STRING_VALUE = "Update String Value"

###########################################################################
#
# Functions to run update items
#
###########################################################################
def update_string():
    return UPDATE_STRING_VALUE


###########################################################################
#
# The tests...
#
###########################################################################
#
# Test Telemetry
#
class Test_Telemetry():
    ###########################################################################
    #
    # Web Server Tests
    #
    ###########################################################################
    #
    # Invalid methods
    #
    def test_invalid_methods_root_path(self, telemetry_server, web_request):
        # / - GET is allowed
        web_request.standard_invalid_method_test(
            uri=f"{BASE_URI}",
            valid_methods=["get"]
        )


    def test_invalid_methods_any_path(self, telemetry_server, web_request):
        # Nothing is allowed
        web_request.standard_invalid_method_test(
            uri=f"{BASE_URI}any",
            valid_methods=[]
    )


    #
    # Valid Requests
    #
    def test_valid(self, telemetry_server, web_request):
        _var_name = "webvalue"
        _var_string = "web string"

        # Create a value
        telemetry_server.set_static(name=_var_name, value=_var_string)
        assert telemetry_server.get(name=_var_name) == _var_string

        # Get the value via the web interface
        _req = web_request.get(uri=f"{BASE_URI}")

        # Validate the response
        assert _req
        assert _var_name in _req
        assert _req[_var_name] == _var_string


    ###########################################################################
    #
    # Item Tests
    #
    ###########################################################################
    def test_static_entries(self, telemetry_server):
        _varstr = "A static variable in"

        for _name in ("staticVar", "nested.staticVar", "deeply.nested.staticVar"):
            telemetry_server.set_static(
                name=_name,
                value=f"{_varstr} {_name}"
            )

            _value = telemetry_server.get(name=_name)

            assert _value == f"{_varstr} {_name}"


    #
    # Deletion of status entries
    #
    def test_delete_entries_subtree_false(self, telemetry_server):
        _varstr = "A static variable in"

        for _name in ("deleteVar", "nested.deleteVar", "deeply.nested.deleteVar"):
            telemetry_server.set_static(name=_name, value=f"{_varstr} {_name}")
            _value = telemetry_server.get(name=_name)
            assert _value == f"{_varstr} {_name}"
            telemetry_server.delete(name=_name, subtree=False)
            _value = telemetry_server.get(name=_name)
            assert not _value 


    # def test_delete_entries_subtree_true(self):
    #     _varstr = "A static variable in"

    #     for _name in ("deleteVar", "nested.deleteVar", "deeply.nested.deleteVar"):
    #         assert Status.set_static(name=_name, value=f"{_varstr} {_name}")
    #         _value = Status.get(name=_name)
    #         assert _value == f"{_varstr} {_name}"
    #         assert Status.delete(name=_name, subtree=True)
    #         _value = Status.get(name=_name)
    #         assert not _value 


    #
    # Invalid entries
    #
    def test_invalid_set_nested(self, telemetry_server):
        _varstr = "A static variable in"

        telemetry_server.set_static(name="nested.value", value=_varstr)
        assert telemetry_server.get(name="nested.value") == _varstr

        with pytest.raises(ds_exception.DataStoreDotNameError):
            telemetry_server.set_static(name="nested", value=_varstr)

        assert not telemetry_server.get(name="nested")
        time.sleep(0.1)


    #
    # Dynamic entries
    #
    def test_dynamic_entry(self, telemetry_server):
        _wait_time = 2
        _var_name = "dynamicvalue"
        _var_string_change = "Something different"

        telemetry_server.set_interval(
            name=_var_name,
            func=update_string,
            interval=_wait_time
        )

        # Val should be set after wait_time
        time.sleep(_wait_time + 0.5)
        assert telemetry_server.get(name=_var_name) == UPDATE_STRING_VALUE

        # Change it
        telemetry_server.set_static(name=_var_name, value=_var_string_change)
        assert telemetry_server.get(name=_var_name) == _var_string_change

        # Wait for it to update and it should be back to original
        time.sleep(_wait_time + 1)
        assert telemetry_server.get(name=_var_name) == UPDATE_STRING_VALUE


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
