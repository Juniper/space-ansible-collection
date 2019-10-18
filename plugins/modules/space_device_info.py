#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2019, Michael Tucker (@mtucker502)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "0.1",
    "status": ["preview"],
    "supported_by": "community",
}
DOCUMENTATION = """
---
module: space_device_info
short_description: Obtain information about one or many space Rules, with filter options
description:
  - This module obtains information about one or many space Rules, with filter options
version_added: "2.9"
options:
  id:
    description:
      - Obtain only information of the Device with provided ID
    required: false
    type: int
  name:
    description:
      - Obtain only information of the Device that matches the provided name
    required: false
    type: str
  osversion:
    description:
      - Obtain only information of the Device that matches the provided OSversion
    required: false
    type: str
  devicefamily:
    description:
      - Obtain only information of the Device that matches the provided deviceFamily
    required: false
    type: str
  serialnumber:
    description:
      - Obtain only information of the Device that matches the provided SerialNumber
    required: false
    type: str
  platform:
    description:
      - Obtain only information of the Device that matches the provided platform
    required: false
    type: str
  managedstatus:
    description:
      - Obtain only information of the Device that matches the provided managedStatus
    required: false
    type: str
  connectionstatus:
    description:
      - Obtain only information of the Device that matches the provided connectionStatus
    required: false
    type: str
  attribute_column_0:
    description:
      - Obtain only information of the Device that matches the provided attribute-column-0
    required: false
    type: str

notes:
  - You may provide many filters and they will all be applied, except for C(id)
    as that will return only the Rule identified by the unique ID provided.
author: "Juniper Networks Automation Team (https://github.com/juniper)
"""


# FIXME - provide correct example here
RETURN = """
"""

EXAMPLES = """
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text

from ansible.module_utils.urls import Request
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible_collections.juniper.space.plugins.module_utils.space import SpaceRequest

import copy
import json


def main():

    argspec = dict(
        id=dict(required=False, type="int"),
        name=dict(required=False, type="str"),
        osversion=dict(required=False, type="str"),
        devicefamily=dict(required=False, type="str"),
        serialnumber=dict(required=False, type="str"),
        platform=dict(required=False, type="str"),
        managedstatus=dict(required=False, type="str"),
        connectionstatus=dict(required=False, type="str"),
        attribute_column_0=dict(required=False, type="str")
    )

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    space_request = SpaceRequest(
        module,
    )

    if module.params["id"]:
        space_request.headers = {"Accept": "application/vnd.net.juniper.space.device-management.device+json;version=1"}
        devices =  space_request.get_by_path(
            "/api/space/device-management/devices/{0}".format(module.params['id'])
        )
    else:
        query_strs = []
        space_request.headers = {"Accept": "application/vnd.net.juniper.space.device-management.devices+json;version=2"}
        if module.params["name"]:
            query_strs.append(quote("name eq '{0}'".format(to_text(module.params["name"]))))

        if module.params["osversion"]:
            query_strs.append(quote("OSversion eq '{0}'".format(module.params["osversion"])))

        if module.params["devicefamily"]:
            query_strs.append(quote("deviceFamily eq '{0}'".format(module.params["devicefamily"])))

        if module.params["serialnumber"]:
            query_strs.append(quote("SerialNumber eq '{0}'".format(module.params["serialnumber"])))

        if module.params["platform"]:
            query_strs.append(quote("platform eq '{0}'".format(module.params["platform"])))

        if module.params["managedstatus"]:
            query_strs.append(quote("managedStatus eq '{0}'".format(module.params["managedstatus"])))

        if module.params["connectionstatus"]:
            query_strs.append(quote("connectionStatus eq '{0}'".format(module.params["connectionstatus"])))

        if module.params["attribute_column_0"]:
            query_strs.append(quote("attribute-column-0 eq '{0}'".format(module.params["attribute_column_0"])))

        if query_strs:
            devices = space_request.get_by_path(
                "/api/space/device-management/devices?filter=({0})".format("%20and%20".join(query_strs))
            )['devices']
        else:
            devices = space_request.get_by_path("/api/space/device-management/devices")['devices']
    
    # Ensure we always return the device key as a list
    if not isinstance(devices['device'], list):
      devices['device'] = [devices['device']]
    
    module.exit_json(devices=devices, changed=False)

if __name__ == "__main__":
    main()