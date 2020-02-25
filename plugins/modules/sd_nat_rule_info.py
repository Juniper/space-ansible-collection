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
module: sd_address_info
short_description: Obtain information about one or many Security Director NAT Rules, with filter options
description:
  - This module obtains information about one or many Security Director NAT Rules, with filter options.
  - policy_id is always required
version_added: "2.9"
options:
  id:
    description:
      - Obtain only information of the NAT Rules with provided ID
    required: false
    type: int
  name:
    description:
      - Obtain only information of the NAT Rules that matches the provided name
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
from ansible_collections.juniper.space.plugins.module_utils.sd_nat_rule_lib import SDNatRuleMgr
import copy
import json

#FIXME: Validate this works if rule groups are configured in the GUI

def main():
    argspec = dict(
        id=dict(required=False, type="int"),
        policy_id=dict(required=True, type="int"),
        name=dict(required=False, type="str"),
        ip_address=dict(required=False, type="str")
    )

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    mgr = SDNatRuleMgr(
        module=module
    )

    if module.params["id"]:
        rules = mgr.get_by_id(module.params["id"], policy_id = module.params["policy_id"])
    else:
        rules = mgr.get_all(policy_id = module.params["policy_id"])
    
    module.exit_json(rules=rules, changed=False)

if __name__ == "__main__":
    main()