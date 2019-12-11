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

def find_dict_in_list(some_list, key, value):
    text_type = False
    try:
        to_text(value)
        text_type = True
    except TypeError:
        pass
    for some_dict in some_list:
        if key in some_dict:
            if text_type:
                if to_text(some_dict[key]).strip() == to_text(value).strip():
                    return some_dict, some_list.index(some_dict)
            else:
                if some_dict[key] == value:
                    return some_dict, some_list.index(some_dict)
    return None

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
        self.space_request.headers = {"Accept": "application/vnd.juniper.sd.address-management.address+json;version=1;q=0.01"}
        code, response =  self.space_request.get_by_path(
            "/api/juniper/sd/address-management/addresses/{0}".format(id),
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
        self.space_request.headers = {"Accept": "application/vnd.juniper.sd.address-management.address-refs+json;version=1;q=0.01"}
        if name:
            query_strs.append(quote("name eq '{0}'".format(to_text(name))))

        if ip_address: #FIXME: searching by IP currently broken
            query_strs.append(quote("'ip-address' eq '{0}'".format(ip_address)))

        if query_strs:
            code, response = self.space_request.get_by_path(
                "/api/juniper/sd/address-management/addresses?filter=({0})".format("%20and%20".join(query_strs))
            )
            return self._return_list(response['addresses'])
        else:
            code, response = self.space_request.get_by_path("/api/juniper/sd/address-management/addresses")
            return self._return_list(response['addresses'])

    def get_address(self, **kwargs):
        '''
        This address first querries by filter and then uses first address in the list to querry by ID.
        The /api/space/address-management/addresses/<id> endpoint provides greater detail thann simply querrying by filter
        '''
        address_list = self.get_addresses(**kwargs)
        if address_list:
            return self.get_address_by_id(address_list[0]['id'])
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