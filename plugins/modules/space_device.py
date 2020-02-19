#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2019, Michael Tucker (@mtucker502)
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
  use_ping:
    description:
      - Use ping to monitor the device reachability
    required: false
    type: bool
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
from ansible_collections.juniper.space.plugins.module_utils.space_device_lib import SpaceDeviceMgr

import copy
import json

def main():

    argspec = dict(
        state=dict(required=True, choices=["present", "absent"], type="str"),
        id=dict(required=False, type="int"),
        ip_address=dict(required=False, type="str"),
        username=dict(required=False, type="str", no_log=True),
        password=dict(required=False, type="str", no_log=True),
        use_ping=dict(required=False, type="bool", default=True),
        use_snmp=dict(required=False, type="bool", default=False),
        snmp_community=dict(required=False, type="str"),
        queue=dict(required=False, type="str")
    )

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    space_request = SpaceRequest(
        module,
    )
    space_device_manager = SpaceDeviceMgr(
        module,
    )

    # Gather device details to determine if device exists
    if module.params["id"]:
        device = space_device_manager.get_device_by_id(module.params["id"])
    elif module.params["ip_address"]:
        #FIXME: Use get_device instead so we get full device details when we implment changing existing device
        device = space_device_manager.get_device(ip_address=module.params["ip_address"])
    else:
        module.fail_json(msg='You must provide either an id or ip_address')
    
    if to_text(module.params["state"]) == "present":
        if device:
            #FIXME: Add logic for changing an existing device
            module.exit_json(msg='Device already present', device=device[0], changed=False)
        #check params
        else:
            if not module.params["ip_address"]:
                module.fail_json(msg='You must provide either an ip_address')
            elif not module.params["username"]:
                module.fail_json(msg='You must provide a username')
            elif not module.params["password"]:
                module.fail_json(msg='You must provide either a password')
        
        # Create the device
        space_request.headers = {
            "Accept": "application/vnd.net.juniper.space.device-management.discover-devices+json;version=1",
            "Content-Type": "application/vnd.net.juniper.space.device-management.discover-devices+json;version=1;charset=UTF-8"
        }
        body = {
            "systemDiscoveryRule":{
                "ipAddressDiscoveryTarget": { "exclude":"false","ipAddress":"{}".format(module.params["ip_address"]) },
                "usePing":"{}".format(module.params["use_ping"]),
                "manageDiscoveredSystemsFlag":"true",
                "sshCredential": {
                    "userName":"{}".format(module.params["username"]),
                    "password":"{}".format(module.params["password"])
                },
                "tagNewlyManagedDiscoveredSystemsFlag":"false"
            }
        }

        if module.params["snmp_community"]:
            body['systemDiscoveryRule']['snmpV2CSetting'] = { "communityName":"{}".format(module.params["snmp_community"]) }
            body['systemDiscoveryRule']['useSnmp'] = "True"

        code, response = space_request.post("/api/space/device-management/discover-devices", payload=json.dumps(body))
        
        task_id = response['task']['id']
        job_status = space_request.check_job(task_id=task_id)

        if job_status == "DONE":
            device = space_device_manager.get_devices(ip_address=module.params["ip_address"])
            module.exit_json(device=device, task_id=task_id, job_status=job_status, changed=True)
        else:
            module.fail_json(task_id=task_id, job_status=job_status, changed=False)


    elif module.params["state"] == "absent":
        if not device:
            module.exit_json(msg="Device already absent", device=device, changed=False)
        else:
            space_request.headers = {"Accept": "application/vnd.net.juniper.space.device-management.device+json;version=1"}
            space_request.expect_json = False

            code, response =  space_request.delete(
                "/api/space/device-management/devices/{0}".format(device[0]["device-id"]),
                status_codes="202"
            )
            if code == 202:
                module.exit_json(task_id=response['task']['id'], changed=True)

if __name__ == "__main__":
    main()