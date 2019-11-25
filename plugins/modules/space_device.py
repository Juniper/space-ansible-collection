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
module: space_device
short_description: This module allows for addition, deletion, or modification of devices in Junos Space
description:
  - This module allows for addition, deletion, or modification of devices in Junos Space
version_added: "2.9"
options:
  id:
    description:
      - ID of device
    required: false
    type: int
  ip_address:
    description:
      - IP address of device
    required: false
    type: str
  username:
    description:
      - Username to authenticate to the device
    required: true
    type: str
  password:
    description:
      - Password to authenticate to the device
    required: true
    type: str
  snmp_comunity:
    description:
      - SNMP community string. If provided the device must be reachable via SNMP or discovery will fail
    required: false
    type: str
  queue:
    description:
      - Name of HornetQ for 
    required: false
    type: str

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

#### ADD IP CHANGE functionality

def main():

    argspec = dict(
        state=dict(required=True, choices=["present", "absent"], type="str"),
        id=dict(required=False, type="int"),
        ip_address=dict(required=False, type="str"),
        username=dict(required=False, type="str", no_log=True),
        password=dict(required=False, type="str", no_log=True),
        snmp_community=dict(required=False, type="str"),
        queue=dict(required=False, type="str")
    )

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    space_request = SpaceRequest(
        module,
    )
    if to_text(module.params["state"]) == "present":
      pass
    elif to_text(module.params["state"]) == "absent":
        space_request.headers = {"Accept": "application/vnd.net.juniper.space.device-management.device+json;version=1"}
        space_request.expect_json = False

        code, response =  space_request.delete(
            "/api/space/device-management/devices/{0}".format(module.params['id']),
            status_codes="202,404"
        )
        if code == 202:
          module.exit_json(return_code=code, return_body=response, changed=True)
        elif code == 404:
          module.exit_json(return_code=code, return_body=response, changed=False)    
    
    module.exit_json(devices=devices, changed=False)

if __name__ == "__main__":
    main()