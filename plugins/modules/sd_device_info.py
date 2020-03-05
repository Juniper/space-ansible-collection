#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Michael Tucker (@mtucker502)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}
DOCUMENTATION = """
---
module: sd_device_info
short_description: Obtain information about one or many SD devices, with filter options
description:
  - This module obtains information about one or many SD devices, with filter options
version_added: "2.9"
options:
  id:
    description:
      - Obtain only information of the Device with provided SD ID
    required: false
    type: int
  name:
    description:
      - Obtain only information of the Device that matches the provided name
    required: false
    type: str
  ip:
    description:
      - Obtain only information of the Device that matches the provided IP address
    required: false
    type: str
  platform_id:
    description:
      - Obtain only information of the Device with provided Space Platform ID
    required: false
    type: int
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
from ansible_collections.juniper.space.plugins.module_utils.sd_device_lib import SDDeviceMgr

import copy
import json


def main():

    argspec = dict(
        id=dict(required=False, type="int"),
        name=dict(required=False, type="str"),
        ip=dict(required=False, type="str"),
        platform_id=dict(required=False, type="int")
    )

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    sd_device_manager = SDDeviceMgr(
        module,
    )

    devices = sd_device_manager.get_devices(
      id=module.params["id"],
      name=module.params["name"],
      ip=module.params["ip"]
      )
    
    module.exit_json(devices=devices, changed=False)

if __name__ == "__main__":
    main()