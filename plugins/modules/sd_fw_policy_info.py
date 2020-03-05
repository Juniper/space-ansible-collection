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
module: sd_policy_info
short_description: Obtain information about one or many Security Director FirewallPolicies, with filter options
description:
  - This module obtains information about one or many Security Director FirewallPolicies, with filter options
version_added: "2.9"
options:
  id:
    description:
      - Obtain only information of the FirewallPolicy with provided ID
    required: false
    type: int
  name:
    description:
      - Obtain only information of the FirewallPolicy that matches the provided name
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
from ansible_collections.juniper.space.plugins.module_utils.sd_fw_policy_lib import SDFWPolicyMgr
import copy
import json


def main():
    argspec = dict(
        id=dict(required=False, type="int"),
        name=dict(required=False, type="str"),
    )

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    mgr = SDFWPolicyMgr(
        module=module
    )

    if module.params["id"]:
        policies = mgr.get_by_id(module.params["id"])
        module.exit_json(policies=policies, changed=False)
    else:
        if module.params["name"]:
            # call get_one for greater detail and single element list
            policies = mgr.get_one(
                name=module.params["name"],
                ip_address=module.params["ip_address"]
            )
        else:
            # call general get which will return full list only if no filters are provided
            policies = mgr.get()

    module.exit_json(policies=policies, changed=False)

if __name__ == "__main__":
    main()