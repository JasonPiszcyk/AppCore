#!/usr/bin/env python3
'''
*
* web_request.py
*
* Copyright (c) 2025 Iocane Pty Ltd
*
* @author: Jason Piszcyk
* 
* The base web request class
*
'''

# System Imports
import requests
import urllib3
import json
import pytest
import re

#
# Globals
#

urllib3.disable_warnings()


###########################################################################
#
# Exceptions
#
###########################################################################
class Request_No_Data(UserWarning):
    pass


class API_Error(RuntimeWarning):
    pass


###########################################################################
#
# The Base Class
#
###########################################################################
class Web_Request():
    '''
    Class to handle an API request
    '''
    # Response info
    BAD_REQUEST = "400 Client Error: BAD REQUEST"
    UNAUTHORISED = "401 Client Error: UNAUTHORIZED"
    FORBIDDEN = "403 Client Error: FORBIDDEN"
    NOT_FOUND = "404 Client Error: NOT FOUND"
    METHOD_NOT_ALLOWED = "405 Client Error: Method Not Allowed"
    UNSUPPORTED_METHOD = "501 Server Error: Unsupported method"

    # Methods to test
    METHOD_LIST=["get", "put", "post", "patch", "delete"]


    #
    # __init__
    #
    def __init__(self):
        '''
        Class Constructor

        Parameters:
            None

        Return Value:
            None
        '''
        # Set Values
        pass


    ###########################################################################
    #
    # Helper/Convenience Functions
    #
    ###########################################################################
    #
    # check_status
    #
    def check_status(self, request=None):
        assert request is not None

        if hasattr(request, "raise_for_status"):
            request.raise_for_status()
        else:
            raise API_Error("Response was not formatted correctly")

        if request.status_code == 204:
            raise Request_No_Data("Response did not contain any data")


    #
    # Set the headers
    #
    def set_headers(self, headers={}):
        # Set the default headers
        _new_headers = {
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json",
        }

        # Add any supplied headers
        if headers:
            _new_headers.update(headers)

        return _new_headers


    #
    # Get the function for the method
    #
    def get_method_function(self, method=""):
        if method == "get":
            return self.get
        elif method == "put":
            return self.put
        elif method == "post":
            return self.post
        elif method == "patch":
            return self.patch
        elif method == "delete":
            return self.delete
        else:
            raise AssertionError(f"Invalid method supplied ({method})")


    ###########################################################################
    #
    # API methods
    #
    ###########################################################################
    #
    # get
    #
    def get(self, uri="", headers={}, params={}):
        _req_headers = self.set_headers(headers=headers)

        _req = requests.get(
            uri,
            headers=_req_headers,
            params=params,
            verify=False
        )

        # Raise an exception if the request failed
        self.check_status(request=_req)

        # Return the info from the request
        _req_data = json.loads(_req.text)

        return _req_data


    #
    # put
    #
    def put(self, uri="", headers={}, params={}, data={}):
        _req_headers = self.set_headers(headers=headers)

        _req = requests.put(
            uri,
            headers=_req_headers,
            params=params,
            data=json.dumps(data),
            verify=False
        )

        # Raise an exception if the request failed
        self.check_status(request=_req)

        # Return the info from the request
        _req_data = json.loads(_req.text)

        return _req_data


    #
    # post
    #
    def post(self, uri="", headers={}, params={}, data={}):
        _post_headers = headers
        _post_headers.update( {"Content-Type": "application/json" } )
        _req_headers = self.set_headers(headers=_post_headers)

        _req = requests.post(
            uri,
            headers=_req_headers,
            params=params,
            data=json.dumps(data),
            verify=False
        )

        # Raise an exception if the request failed
        self.check_status(request=_req)

        # Return the info from the request
        _req_data = json.loads(_req.text)

        return _req_data


    #
    # patch
    #
    def patch(self, uri="", headers={}, params={}, data={}):
        _req_headers = self.set_headers(headers=headers)

        _req = requests.patch(
            uri,
            headers=_req_headers,
            params=params,
            data=json.dumps(data),
            verify=False
        )

        # Raise an exception if the request failed
        self.check_status(request=_req)

        # Return the info from the request
        _req_data = json.loads(_req.text)

        return _req_data


    #
    # delete
    #
    def delete(self, uri="", headers={}, params={}):
        _req_headers = self.set_headers(headers=headers)

        _req = requests.delete(
            uri,
            headers=_req_headers,
            params=params,
            verify=False
        )

        # Raise an exception if the request failed
        self.check_status(request=_req)

        # Return the info from the request
        try:
            _req_data = json.loads(_req.text)
        except:
            _req_data = {}

        return _req_data


    ###########################################################################
    #
    # Standard Checks on an API Method
    #
    ###########################################################################
    #
    # Test invalid methods
    #
    def standard_invalid_method_test(self, uri="", valid_methods=["get"]):
        assert uri

        # Create a list of invalid methods
        _invalid_methods = []
        for _test_method in self.METHOD_LIST:
            if not _test_method in valid_methods:
                _invalid_methods.append(_test_method)

        #
        # Invalid methods are reported before authorisation check, so ignore auth
        #
        for _test_method in _invalid_methods:
            _method_func = self.get_method_function(method=_test_method)

            _match_regex = r""\
                + re.escape(self.METHOD_NOT_ALLOWED) + ".*|"\
                + re.escape(self.UNSUPPORTED_METHOD) + ".*"

            with pytest.raises(requests.exceptions.HTTPError, match=_match_regex):
                _ = _method_func(uri=uri)
