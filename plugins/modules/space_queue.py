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
module: space_queue
short_description: Manage state of Space's HornetQ Queues
description:
  - Manage state of Space's HornetQ
version_added: "2.9"
options:
  name:
    description:
      - Manage Space queue by name
    required: True
    type: str

  state:
    description:
      - Manage state of a QRadar Rule
    required: True
    choices: [ "present", "absent" ]
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


def main():

    argspec = dict(
      name=dict(required=True, type="str"),
      state=dict(required=True, choices=["present", "absent"], type="str")
    )

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    space_request = SpaceRequest(
        module,
    )

    space_request.headers = {"Content-Type": "application/hornetq.jms.queue+xml"}
    space_request.expect_json = False
    queue_name = to_text(module.params["name"])

    if to_text(module.params["state"]) == "present":
      body = '<queue name="{0}"><durable>false</durable></queue>'.format(queue_name)   
      code, response = space_request.post("/api/hornet-q/queues", payload=body, status_codes='201, 412')
      
      if code == 201:
        module.exit_json(return_code=code, return_body=response, changed=True)
      elif code == 412:
        module.exit_json(return_code=code, return_body=response, changed=False)
    elif to_text(module.params["state"]) == "absent":
      code, response = space_request.delete(
        '/api/hornet-q/queues/jms.queue.{0}'.format(queue_name),
        status_codes='204, 405'
        )
      if code == 204:
        module.exit_json(return_code=code, return_body=response, changed=True)
      elif code == 405:
        module.exit_json(return_code=code, return_body=response, changed=False)
      


if __name__ == "__main__":
    main()