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
  address_version:
    description:
      - IP version of address object
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


def main():

    argspec = dict(
        state=dict(required=True, choices=["present", "absent"], type="str"),
        id=dict(required=False, type="int"),
        name=dict(required=False, type="str"),
        ip_address=dict(required=False, type="str"),
        address_version=dict(required=False, choices=["ipv4", "ipv6"], type="str", default="ipv4"),
        type=dict(required=False, choices=["ipaddress", "group"], type="str", default="ipaddress"),
        members=dict(required=False, type="list", elements="str")
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
        #check params
        if not module.params["name"]:
            module.fail_json(msg='You must provide a name')
        elif not module.params["ip_address"] and not module.params["type"] == "group": #only require IP addres if this isn't a group
            module.fail_json(msg='You must provide an IP address')
        
        if module.params["type"] == "group" and module.params["members"] is None:
            module.fail_json(msg='You must provide at least one member if the address type is GROUP')
        
        space_request.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Create the address body
        body = dict(address = {
            "definition_type" : "CUSTOM",
            "associated_metadata" : "",
            "name" : module.params["name"],
            "description" : "",
            "address_type" : module.params["type"].upper(),
            "address_version" : module.params["address_version"].upper(),
            "host_name" : ""}
        )

        # Add member-refs if necessary
        if module.params["type"] == "group":
            address_refs = []
            for member in module.params["members"]:
                response = sd_address_manager.get_address(name=member)
                if response is not None:
                    # address_refs.append(dict(name=response[0]['name'], uuid=response[0]['uuid']))
                    response[0].pop('uri', None)
                    address_refs.append(response[0])
                else:
                    module.fail_json(msg="Could not find member with name: {}".format(member))
            body['address']['address_refs'] = address_refs
        else:
            # only set ip_address key if this isn't a group
            body['address']['ip_address'] = module.params["ip_address"]

        # Logic for changing an existing address
        if address:
            # make a copy 
            patch_address = dict(address=address[0].copy())

            #update the patch with the prepared body
            patch_address['address'].update(body['address'])

            #compare for differences
            if address[0] == patch_address['address']:
                module.exit_json(msg='Address already up to date', address=address[0], changed=False)
            else:
                code, response = space_request.put(
                    "/api/juniper/sd/address-management/v5/address/{0}".format(address[0]["uuid"]),
                    payload=json.dumps(patch_address)
                    )

                module.exit_json(msg='Address updated', address=response['address'], changed=True)
            

            if address[0]["address-type"] == "IPADDRESS" and address[0]["ip-address"] != body["address"]["ip_address"]:
                pass # update body with edit-version and set method to PUT

            elif address[0]["address-type"] == "GROUP":
                for member in body["address"]["address_refs"]:
                    if not any(d["uuid"] == member["uuid"] for d in a):
                        pass # update body with edit-version and set method to PUT
            
            module.exit_json(msg='Address already present', address=address[0], changed=False)        

        if address:
            #FIXME: Add logic for changing an existing address
            # add edit_version
            # Evaluate if any fields need to be updated
            if address[0]["address-type"] == "IPADDRESS" and address[0]["ip-address"] != body["address"]["ip_address"]:
                pass # update body with edit-version and set method to PUT

            elif address[0]["address-type"] == "GROUP":
                for member in body["address"]["address_refs"]:
                    if not any(d["uuid"] == member["uuid"] for d in a):
                        pass # update body with edit-version and set method to PUT
            
            module.exit_json(msg='Address already present', address=address[0], changed=False)        



        code, response = space_request.post("/api/juniper/sd/address-management/v5/address", payload=json.dumps(body))

        module.exit_json(address=response['address'], changed=True)

    elif module.params["state"] == "absent":
        if not address:
            module.exit_json(msg="Address already absent", address=address, changed=False)
        else:
            space_request.headers = {"Accept": "application/vnd.net.juniper.space.address-management.address+json;version=1"}
            space_request.expect_json = False

            code, response =  space_request.delete(
                "/api/juniper/sd/address-management/addresses/{0}".format(address[0]["uuid"]),
                status_codes="204, 500"
            )

            if code == 204:
                module.exit_json(changed=True)
            elif code == 500:
                module.fail_json(msg="Could not delete the address. Most likely it is in use by another group or policy.", response=response)
            
if __name__ == "__main__":
    main()