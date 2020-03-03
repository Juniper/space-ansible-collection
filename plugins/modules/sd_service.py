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
module: sd_service_info
short_description: Obtain information about one or many Security Director Service Objects, with filter options
description:
  - This module obtains information about one or many Security Director Service Objects, with filter options
version_added: "2.9"
options:
  id:
    description:
      - Obtain only information of the Service Object with provided ID
    required: false
    type: int
  name:
    description:
      - Obtain only information of the Service Object that matches the provided name
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
from ansible_collections.juniper.space.plugins.module_utils.sd_service_lib import SDServiceMgr
from copy import deepcopy
import json


def main():
    argspec = dict(
        state=dict(
            required=True,
            choices=['present', 'absent'],
            type='str'
        ),
        id=dict(
            required=False,
            type='int'
        ),
        name=dict(
            required=False,
            type='str'
        ),
        description=dict(
            required=False,
            type='str',
            default=''
        ),
        application_services=dict(
            type='str',
            required=False,
        ),
        # is_group=dict(
        #     type='bool',
        #     default=False
        # ),
        definition_type=dict(
            type='str',
            default='CUSTOM'
        ),
        members=dict(
            required=False,
            type='list',
            elements='str'
        ),
        protocols=dict(
            type='list',
            required=False,
            elements='dict',
            options=dict(
                name=dict(
                    type='str',
                    required=True
                ),
                description=dict(
                    type='str',
                    required=False,
                    default=''
                ),
                protocol=dict(
                    type='str',
                    required=True,
                    choices= [
                        'tcp', 
                        'udp',
                        'other'
                    ]
                ),
                dst_port=dict(
                    type='str',
                    required=False
                ),
                src_port=dict(
                    type='str',
                    required=False
                ),
                disable_timeout=dict(
                    type='bool',        #FIXME: test this.Does disable_timeout=True require parameter ename_timeout=False to exist?
                    default=False,
                ),
                inactivity_timeout=dict(
                    type='str',
                    required=False,
                ),
                inactivity_time_type=dict(
                    type='str',
                    default='Seconds'  #FIXME: ADD choices [seconds, minutes]
                ),
                protocol_number=dict(
                    type='int',
                    required=False
                )
            )
        )
    )

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    module.params['is_group'] = False
    service_list = dict(
        application_services='application-services',
        is_group='is-group'
    )
    protocol_list = dict(
        dst_port='dst-port',
        src_port='src-port',
        disable_timeout='disable-timeout',
        inactivity_timeout='inactivity-timeout',
        inactivity_time_type='inactivity-time-type',
        protocol_number='protocol-number',
    )

    mgr = SDServiceMgr(
        module=module
    )

    # marshal (rename) the data
    module.params = mgr._marshal(data=module.params, conversion_list=service_list)
    if module.params.get('protocols'):
        for protocol in module.params.get('protocols'):
            protocol = mgr._marshal(data=protocol, conversion_list=protocol_list)

    if module.params["id"]:
        service = mgr.get_by_id(module.params["id"])
    elif module.params["name"]:
        service = mgr.get_one(name=module.params["name"])
    else:
        module.fail_json(msg='You must provide either an id or a name')


    if module.params["state"] == "present":
        #check params
        if not module.params["name"]:
            module.fail_json(msg='You must provide a name')

        #only require protocols suboptions if this isn't a group
        if not module.params["is-group"] and not module.params["protocols"]:
            module.fail_json(msg='You must provide one or more protocols')
        
        if module.params["is-group"] and module.params["members"] is None:
            module.fail_json(msg='You must provide at least one member if the service type is GROUP')
        
        # Create the service body
        body = mgr._body_builder(module.params)
        
        # Logic for changing an existing service
        if service:
            # make a copy
            patch_body = dict(service=deepcopy(service[0]))

            if module.params['is-group']:
                members = mgr._update_list(
                    patch_body['service']['service_refs'],
                    body['service']['service_refs'],
                    'name'
                )

                patch_body['service']['service_refs'] = members
                body['service'].pop('service_refs', None)

            elif not module.params['is-group']:
                protocols = mgr._update_list(
                    patch_body['service']['protocols']['protocol'],
                    body['service']['protocols']['protocol'],
                    'name'
                )

                patch_body['service']['protocols']['protocol'] = protocols
                body['service'].pop('protocols', None)
            
            patch_body['service'].update(body['service'])

            #compare for differences
            if service[0] == patch_body['service']:
                module.exit_json(msg='Service already up to date', service=service[0], changed=False)
            else:
                service = mgr.update(service[0]['uuid'], patch_body)
                module.exit_json(msg='Service updated', service=service, changed=True)

        elif not service:
            #create
            service = mgr.create(body)
            module.exit_json(service=service, changed=True)

    elif module.params["state"] == "absent":
        if not service:
            module.exit_json(msg="Service already absent", changed=False)
        else:
            status, err = mgr.delete(service[0]['uuid'])
            if status:
                module.exit_json(changed=True)
            else:
                module.exit_json(msg="Could not delete the service. Most likely it is in use by another group or policy.", response=err)

if __name__ == "__main__":
    main()