#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Michael Tucker (@mtucker502)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import to_text
from ansible_collections.juniper.space.plugins.module_utils.space import SpaceRequest
from ansible.module_utils.six.moves.urllib.parse import quote

class SDDeviceMgr(object):
    '''
    This SD API endpoint only supports filters and does not support device specific URIs.
    Hence we will only implement get_devices() with filters.
    '''
    def __init__(self, module):
        self.space_request = SpaceRequest(
        module,
    )

    def get_devices(self, id=None, name=None, ip=None, platform_id=None):
        '''
        Querries SD API and returns list of any devices matching filter(s) or None
        '''
       
        self.space_request.headers = {"Accept": "application/vnd.juniper.sd.device-management.devices-extended+json;version=2;q=0.02"}
        query_strs = []

        if id:
            query_strs.append(quote("id eq '{0}'".format(to_text(id))))

        if platform_id:
            query_strs.append(quote("device-id eq '{0}'".format(to_text(platform_id))))

        if name:
            query_strs.append(quote("name eq '{0}'".format(to_text(name))))
        
        if ip:
            query_strs.append(quote("device-ip eq '{0}'".format(ip)))

        if query_strs:
            code, response = self.space_request.get_by_path(
                "/api/juniper/sd/device-management/devices?filter=({0})".format("%20and%20".join(query_strs))
            )
            return self._return_list_or_none(response['devices']['device'])
        else:
            code, response = self.space_request.get_by_path("/api/juniper/sd/device-management/devices")
            return self._return_list_or_none(response['devices']['device'])

    def _return_list_or_none(self, alist):
        if not isinstance(alist, list):
            alist = [alist]

        if  len(alist) == 0:
            return None

        return alist