#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2019, Michael Tucker (@mtucker502)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import to_text
from ansible_collections.juniper.space.plugins.module_utils.space import SpaceRequest
from ansible.module_utils.six.moves.urllib.parse import quote

class SpaceDeviceMgr(object):
    def __init__(self, module):
        self.space_request = SpaceRequest(
        module,
    )

    def get_device_by_id(self, id):
        '''
        Querries Space API and returns single element list with one device or None
        '''
        self.space_request.headers = {"Accept": "application/vnd.net.juniper.space.device-management.device+json;version=1"}
        code, response =  self.space_request.get_by_path(
            "/api/space/device-management/devices/{0}".format(id),
            status_codes="200,404"
        )

        if code == 200:
            return self._return_list(response)
        elif 404:
            return None

    def get_devices(self, name=None, osversion=None, devicefamily=None, serialnumber=None, platform=None, managedstatus=None,
        connectionstatus=None, attribute_column_0=None, ip_address=None):
        '''
        Querries Space API and returns list of any devices matching filter(s) or None
        '''
        query_strs = []
        self.space_request.headers = {"Accept": "application/vnd.net.juniper.space.device-management.devices+json;version=2"}
        if name:
            query_strs.append(quote("name eq '{0}'".format(to_text(name))))

        if osversion:
            query_strs.append(quote("OSversion eq '{0}'".format(osversion)))

        if devicefamily:
            query_strs.append(quote("deviceFamily eq '{0}'".format(devicefamily)))

        if serialnumber:
            query_strs.append(quote("SerialNumber eq '{0}'".format(serialnumber)))

        if platform:
            query_strs.append(quote("platform eq '{0}'".format(platform)))

        if managedstatus:
            query_strs.append(quote("managedStatus eq '{0}'".format(managedstatus)))

        if connectionstatus:
            query_strs.append(quote("connectionStatus eq '{0}'".format(connectionstatus)))

        if attribute_column_0:
            query_strs.append(quote("attribute-column-0 eq '{0}'".format(attribute_column_0)))
        
        if ip_address:
            query_strs.append(quote("ipAddr eq '{0}'".format(ip_address)))

        if query_strs:
            code, response = self.space_request.get_by_path(
                "/api/space/device-management/devices?filter=({0})".format("%20and%20".join(query_strs))
            )
            return self._return_list(response['devices'])
        else:
            code, response = self.space_request.get_by_path("/api/space/device-management/devices")
            return self._return_list(response['devices'])

    def get_device(self, **kwargs):
        '''
        This device first querries by filter and then uses first device in the list to querry by ID.
        The /api/space/device-management/devices/<id> endpoint provides greater detail thann simply querrying by filter
        '''
        device_list = self.get_devices(**kwargs)
        if len(device_list) > 0:
            return self.get_device_by_id(device_list[0]['device-id'])
        else:
            return None #no devices exist
    
    def _return_list(self, devices):
        try:
            if not isinstance(devices['device'], list):
                devices = [devices['device']]
        except KeyError:
            return None #no devices exist
        
        return devices