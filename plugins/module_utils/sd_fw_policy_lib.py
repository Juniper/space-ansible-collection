#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Michael Tucker (@mtucker502)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.juniper.space.plugins.module_utils.space import ObjectManager
from ansible_collections.juniper.space.plugins.module_utils.space import ObjectConfig

class SDFWPolicyConfig(ObjectConfig):
    uris = dict(
        get="/api/juniper/sd/policy-management/firewall/policies",
        get_by_id="/api/juniper/sd/policy-management/firewall/policies",
        create="/api/juniper/sd/policy-management/firewall/policies", #FIXME: trailing / required?
        delete="/api/juniper/sd/policy-management/firewall/policies",
        update="/api/juniper/sd/policy-management/firewall/policies"
    )
    headers = dict(
        get={"Accept": "application/vnd.juniper.sd.policy-management.firewall.policies+json;version=2;q=0.02"},
        get_by_id={"Accept": "application/vnd.juniper.sd.policy-management.firewall.policy+json;version=2"},
        create={
            "Accept": "application/vnd.juniper.sd.policy-management.firewall.policy+json;version=2",
            "Content-Type": "application/vnd.juniper.sd.policy-management.firewall.policy+json;version=2;charset=UTF-8"},
        delete=None,
        update={"Accept": "application/json", "Content-Type": "application/json"}
    )
    list_keys = ['policies', 'policy']
    filter_operator = 'contains'
    filters = ['name']

class SDFWPolicyMgr(ObjectManager):
    def __init__(self, **kwargs):
        super(eval(self.__class__.__name__), self).__init__(config=SDFWPolicyConfig, **kwargs)


    def _body_builder(self, body_parts, **kwargs):
        body = dict(
        )
            
        return body



# CREATE body:
# {
#     "policy": {
#         "name": "test",
#         "description": "",
#         "policy-type": "DEVICE",
#         "showDevicesWithoutPolicy": false,
#         "jqg_slipstream_listbuilder_grid1_address_360467": false,
#         "policy-position": "DEVICE",
#         "manage-zone-policy": true,
#         "manage-global-policy": true,
#         "policy-profile": {
#             "id": ""
#         },
#         "ips-mode": "NONE"
#     }
# }


# CREATE response
# {
#     "policy": {
#         "last-modified-time": 1583353418037,
#         "edit-version": 0,
#         "policy-type": "DEVICE",
#         "policy-state": "FINAL",
#         "policy-order": 0.0,
#         "created-time": 1583353418037,
#         "name": "test",
#         "domain-id": 2,
#         "description": "",
#         "id": 491521,
#         "created-by-user-name": "jcluser",
#         "policy-position": "DEVICE",
#         "version": 0,
#         "uri": "/api/juniper/sd/policy-management/firewall/policies/491521",
#         "policy-profile": {},
#         "publish-state": "NOT_PUBLISHED",
#         "locked-for-edit": false
#     }
# }


