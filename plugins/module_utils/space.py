#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2019, Michael Tucker (@mtucker502)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.urls import CertificateError
from ansible.module_utils.six.moves.urllib.parse import urlencode, quote_plus, quote
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.connection import Connection
from ansible.module_utils._text import to_text
from time import sleep

import json

class SpaceRequest(object):
    def __init__(self, module, headers=None):

        self.module = module
        self.connection = Connection(self.module._socket_path)
        self.headers = headers

    def _httpapi_error_handle(self, method, uri, payload=None, **kwargs):
        # FIXME - make use of handle_httperror(self, exception) where applicable
        #   https://docs.ansible.com/ansible/latest/network/dev_guide/developing_plugins_network.html#developing-plugins-httpapi
        try:
            code, response = self.connection.send_request(
                method, uri, payload=payload, headers=self.headers
            )
        except ConnectionError as e:
            self.module.fail_json(msg="connection error occurred: {0}".format(e))
        except CertificateError as e:
            self.module.fail_json(msg="certificate error occurred: {0}".format(e))
        except ValueError as e:
            self.module.fail_json(msg="certificate not found: {0}".format(e))
        
        if 'status_codes' in kwargs:
            status_codes = kwargs['status_codes'].replace(' ', '').split(',')
            if to_text(code) in status_codes:
                return code, response
            else:
                self.module.fail_json(
                    msg="space httpapi returned response code {0} with message {1}".format(
                        code, response
                    )
                )
        elif code == 409:
            pass
        elif not (code >= 200 and code < 300):
            self.module.fail_json(
                msg="space httpapi returned error {0} with message {1}".format(
                    code, response
                )
            )

        return code, response

    def get(self, url, **kwargs):
        return self._httpapi_error_handle("GET", url, **kwargs)

    def put(self, url, **kwargs):
        return self._httpapi_error_handle("PUT", url, **kwargs)

    def post(self, url, **kwargs):
        return self._httpapi_error_handle("POST", url, **kwargs)

    def patch(self, url, **kwargs):
        return self._httpapi_error_handle("PATCH", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._httpapi_error_handle("DELETE", url, **kwargs)

    def get_data(self):
        """
        Get the valid fields that should be passed to the REST API as urlencoded
        data so long as the argument specification to the module follows the
        convention:
            - the key to the argspec item does not start with space_
            - the key does not exist in the not_data_keys list
        """
        try:
            space_data = {}
            for param in self.module.params:
                if (self.module.params[param]) != None and (
                    param not in self.not_rest_data_keys
                ):
                    space_data[param] = self.module.params[param]
            return space_data

        except TypeError as e:
            self.module.fail_json(msg="invalid data type provided: {0}".format(e))

    def get_urlencoded_data(self):
        return urlencode(self.get_data())

    def get_by_path(self, rest_path, **kwargs):
        """
        GET attributes by rest path
        """
        return self.get("/{0}".format(rest_path), **kwargs)

    def delete_by_path(self, rest_path):
        """
        DELETE attributes by rest path
        """

        return self.delete("/{0}".format(rest_path))

    def post_by_path(self, rest_path, data=None, **kwargs):
        """
        POST with data to path
        """
        if data == None:
            data = json.dumps(self.get_data())
        elif data == False:
            # Because for some reason some REST API endpoint use the
            # query string to modify state
            return self.post("/{0}".format(rest_path), **kwargs)
        return self.post("/{0}".format(rest_path), payload=data, **kwargs)
    
    def check_job(self, task_id=None, retries=5, delay=10):
        """
        Shared method for checking Space job status
        """
        self.headers = {"Accept": "application/vnd.net.juniper.space.job-management.job+json;version=3"}
        self.module.log("Trying {} time(s)".format(retries))
        while retries > 0:
            self.module.log("Sleeping for {} seconds".format(delay))
            sleep(delay)
            code, response = self.get_by_path("/api/space/job-management/jobs/{}".format(task_id))

            if response["job"]["job-state"] == "DONE":
                return "DONE"
            elif response["job"]["job-state"] == "FAILURE":
                return "FAILURE"
            else:
                self.module.log("Job is still running")
                retries = retries - 1
        
        return response["job"]["job-state"]


class SDAddressMgr(object):
    def __init__(self, module):
        self.space_request = SpaceRequest(
        module,
    )

    def get_address_by_id(self, id):
        '''
        Querries SD API and returns single element list with one address or None
        '''
        self.space_request.headers = {"Accept": "application/json"}
        code, response =  self.space_request.get_by_path(
            "/api/juniper/sd/address-management/v5/address/{0}".format(id),
            status_codes="200,404"
        )

        if code == 200:
            return self._return_list(response)
        elif 404:
            return None

    def get_addresses(self, name=None, ip_address=None):
        '''
        Querries Space API and returns list of any addresses matching filter(s) or None
        '''
        query_strs = []
        self.space_request.headers = {"Accept": "application/json"}
        if name:
            query_strs.append(quote("name contains '{0}'".format(to_text(name))))

        if ip_address:
            query_strs.append(quote("ip_address contains '{0}'".format(ip_address)))

        if query_strs:
            code, response = self.space_request.get_by_path(
                "/api/juniper/sd/address-management/v5/address?filter=({0})".format("%20and%20".join(query_strs))
            )
            return self._return_list(response['addresses'])
        else:
            code, response = self.space_request.get_by_path("/api/juniper/sd/address-management/v5/address")
            return self._return_list(response['addresses'])

    def get_address(self, **kwargs):
        '''
        This address first querries by filter and then uses first address in the list to querry by ID.
        The /api/space/address-management/v5/address/<id> endpoint provides greater detail thann simply querrying by filter
        '''
        address_list = self.get_addresses(**kwargs)
        if address_list:
            return self.get_address_by_id(address_list[0]['uuid'])
        else:
            return address_list
    
    def _return_list(self, addresses):
        try:
            if not isinstance(addresses['address'], list):
                addresses = [addresses['address']]
                return addresses
        except KeyError:
            return None #no addresses exist
        
        if len(addresses['address']) == 0:
            return None
        else:
            return addresses['address']

class ObjectConfig(object):
    uris = None
    headers = None
    filters = None
    list_keys = None
    filter_operator = None
    formatter = None

class ObjectManager(object):
    def __init__(self, module=None, config=None, **kwargs):
        '''Base class for which all future modules will use

        Args:
            module (obj): Ansible module used to create the SpaceRequest instance
            uri (dict): Dictionary of URIs used by each class method.
                Should include keys matching method name (ie. get_by_id, get)
            headers (dict): Dictionary of headers used by each class method.
                Should include keys matching method name (ie. get_by_id, get)
            filters (list): List of accepted filter names for these endpoints.
                Filter names should match actual filter names expected by the endpoints
                in both case and spelling.
            list_key (list): List of two strings containing the keynames we expect to see
                in the response body. Device example: "devices" & "device"
            formatter (dict): If a key exists matching the method name then _formatter() is called
        '''
        self.space_request = SpaceRequest(module)
        self.config = config
        self.update_from_config()
        
    def update_from_config(self):
        self.uris = self.config.uris or {}
        self.headers = self.config.headers or {}
        self.filters = self.config.filters or []
        self.filter_operator = self.config.filter_operator or "contains"
        self.list_keys = self.config.list_keys or None
        self.formatter = self.config.formatter or {}
         
    def get_by_id(self, id, **kwargs):
        '''
        Returns single element list with one entry or None
        '''
        self.space_request.headers = self.headers['get_by_id']
        path = self._formatter(name='get', path=self.uris['get'], **kwargs)
        code, response =  self.space_request.get_by_path(
            "{0}/{1}".format(path, id),
            status_codes="200,404"
        )

        if code == 200:
            return self._return_list(response)
        elif 404:
            return None

    def get_all(self, **kwargs):
        '''
        Returns list of any objects matching the supplied filter(s) or None.
        '''
        path = self._formatter(name='get', path=self.uris['get'], **kwargs)

        query_strs = self._prepare_filters(**kwargs)

        self.space_request.headers = self.headers['get']

        if query_strs:
            code, response = self.space_request.get_by_path(
                "{0}?filter=({1})".format(path, "%20and%20".join(query_strs))
            )
            return self._return_list(response[self.list_keys[0]])
        else:
            code, response = self.space_request.get_by_path(path)
            return self._return_list(response)

    def get(self, **kwargs):
        '''
        This address first querries by filter and then uses first address in the list to querry by ID.
        Usually the API endpoint used by get_all() does not return a verbose body like the get_by_id() endpoint.
        '''
        address_list = self.get_all(**kwargs)
        if address_list:
            return self.get_by_id(address_list[0]['id'])
        else:
            return address_list
    
    def delete(self, id):
        pass
    
    def _prepare_filters(self, **kwargs):
        if not self.filters:
            return None
            
        query_strs = []

        for filter, value in kwargs.items():
            if filter in self.filters:
                query_strs.append(quote("{0} {1} '{2}'".format(filter, self.filter_operator, value)))
        
        if len(query_strs) > 0:
            return query_strs
        else:
            return None
        
    def _return_list(self, items):
        '''
        self.list_keys[0]: This should be the plural form expected in the response body
        self.list_keys[1]: This should be the singular form expected in the response body

        Example:

         "policies" : {
            "policy" : [ {
            "created-by-user-name" : "String",
            "last-modified-time" : "Date",
            "version" : "Integ
            ....
        
        In this example self.list_keys[0] would be "policies" and self.list_keys[1] would be "policy"
        '''

        # just return the list if no keys provided        
        if not self.list_keys:
            return items

        try:
            items = items[self.list_keys[0]][self.list_keys[1]]
            return items
        except KeyError:
            for key in self.list_keys:
                if key in items.keys():
                    return [items[key]]

            return None #no items exist
        
        if not isinstance(items, list):
            items = [items]
        
        if len(items) == 0:
            return None

        return items

    def _formatter(self, name=None, path=None, **kwargs):
        if self.formatter.get(name, None):
            return path.format(**kwargs)
        else:
            return path