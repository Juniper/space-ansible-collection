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
from ansible_collections.juniper.space.plugins.module_utils.space_device_lib import SpaceDeviceMgr

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
        attribute_column_0=dict(required=False, type="str"),
        ip_address=dict(required=False, type="str")
    )

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    space_device_manager = SpaceDeviceMgr(
        module,
    )

    if module.params["id"]:
      devices = space_device_manager.get_device_by_id(module.params["id"])
      module.exit_json(devices=devices, changed=False)
    else:
      devices = space_device_manager.get_devices(
        name=module.params["name"],
        osversion=module.params["osversion"],
        devicefamily=module.params["devicefamily"],
        serialnumber=module.params["serialnumber"],
        platform=module.params["platform"],
        managedstatus=module.params["managedstatus"],
        connectionstatus=module.params["connectionstatus"],
        attribute_column_0=module.params["attribute_column_0"],
        ip_address=module.params["ip_address"]
        )
      module.exit_json(devices=devices, changed=False)

if __name__ == "__main__":
    main()