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
module: sd_address
short_description: This module allows for addition, deletion, or modification of addresses in Security Director
description:
  - This module allows for addition, deletion, or modification of addresses in Security Director
version_added: "2.9"
options:
  id:
    description:
      - ID of address object
    required: false
    type: int
  name:
    description:
      - IP address of address object
    required: false
    type: str
  ip_address:
    description:
      - IP address of address object
    required: false
    type: str
  type:
    description:
      - Type of address object
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
from ansible_collections.juniper.space.plugins.module_utils.space import SpaceRequest, SDAddressMgr

import copy
import json

#### ADD CHANGE functionality

def main():

    argspec = dict(
        state=dict(required=True, choices=["present", "absent"], type="str"),
        id=dict(required=False, type="int"),
        name=dict(required=False, type="str"),
        ip_address=dict(required=False, type="str"),
        type=dict(required=False, choices=["IPADDRESS", "GROUP"], type="str", default="IPADDRESS")
    )

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    space_request = SpaceRequest(
        module,
    )
    sd_address_manager = SDAddressMgr(
        module,
    )

    # Gather address details to determine if address exists
    if module.params["id"]:
        address = sd_address_manager.get_address_by_id(module.params["id"])
    elif module.params["name"]:
        address = sd_address_manager.get_address(name=module.params["name"])
    else:
        module.fail_json(msg='You must provide either an id or a name')
    
    if to_text(module.params["state"]) == "present":
        if address:
            #FIXME: Add logic for changing an existing address
            module.exit_json(msg='address already present', address=address[0], changed=False)
        #check params
        else:
            if not module.params["name"]:
                module.fail_json(msg='You must provide a name')
            elif not module.params["ip_address"]:
                module.fail_json(msg='You must provide an IP address')
        
        #FIXME: Add address-group type functionality

        # Create the address
        space_request.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        body = {
            "address": {
                "definition_type": "CUSTOM",
                "associated_metadata": "",
                "name": "{}".format(module.params["name"]),
                "description": "",
                "address_type": "{}".format(module.params["type"]),
                "address_version": "IPV4",
                "host_name": "",
                "ip_address": "{}".format(module.params["ip_address"])
            }  
        }

        # if module.params["snmp_community"]:
        #     body['systemDiscoveryRule']['snmpV2CSetting'] = { "communityName":"{}".format(module.params["snmp_community"]) }
        #     body['systemDiscoveryRule']['useSnmp'] = "True"

        code, response = space_request.post("/api/juniper/sd/address-management/v5/address", payload=json.dumps(body))
        # module.exit_json(code=code, response=response, changed=True)
        address = sd_address_manager.get_address_by_id(id=response['address']['uuid'])
        module.exit_json(address=address, changed=True)

    elif module.params["state"] == "absent":
        if not address:
            module.exit_json(msg="address already absent", address=address, changed=False)
        else:
            space_request.headers = {"Accept": "application/vnd.net.juniper.space.address-management.address+json;version=1"}
            space_request.expect_json = False

            code, response =  space_request.delete(
                "/api/juniper/sd/address-management/addresses/{0}".format(address[0]["id"]),
                status_codes="204, 500"
            )

            if code == 204:
                module.exit_json(changed=True)
            elif code == 500:
                module.fail_json(msg="Could not delete the address. Most likely it is in use.", response=response)
            
if __name__ == "__main__":
    main()