#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Michael Tucker (@mtucker502)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.juniper.space.plugins.module_utils.space import ObjectManager
from ansible_collections.juniper.space.plugins.module_utils.space import ObjectConfig

class SDNatPolicyConfig(ObjectConfig):
    uris = dict(get="api/juniper/sd/policy-management/nat/policies",
            get_by_id="api/juniper/sd/policy-management/nat/policies"
    )
    headers = dict(get={"Accept": "application/vnd.juniper.sd.policy-management.nat.policies+json;version=1;q=0.01"},
                get_by_id={"Accept": "application/vnd.juniper.sd.policy-management.nat.policy+json;version=1;q=0.01"}
    )
    filters = ['name']
    list_keys = ['policies', 'policy']
    filter_operator = 'contains'

class SDNatPolicyMgr(ObjectManager):
    def __init__(self, **kwargs):
        super(SDNatPolicyMgr, self).__init__(config=SDNatPolicyConfig, **kwargs)