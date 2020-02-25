#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Michael Tucker (@mtucker502)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.juniper.space.plugins.module_utils.space import ObjectManager
from ansible_collections.juniper.space.plugins.module_utils.space import ObjectConfig

class SDNatRuleConfig(ObjectConfig):
    uris = dict(get="/api/juniper/sd/policy-management/nat/policies/{policy_id}/rules",
            get_by_id="/api/juniper/sd/policy-management/nat/policies/{policy_id}/rules"
    )
    headers = dict(get={"Accept": "application/vnd.juniper.sd.policy-management.nat.rules+json;version=2;q=0.02"},
                get_by_id={"Accept": "application/vnd.juniper.sd.policy-management.nat.rule+json;version=2;q=0.02"}
    )
    list_keys = ['dc-nat-rules', 'rule']
    filter_operator = 'contains'
    formatter = dict(get=True,
                    get_by_id=True
    )

class SDNatRuleMgr(ObjectManager):
    def __init__(self, **kwargs):
        super(SDNatRuleMgr, self).__init__(config=SDNatRuleConfig, **kwargs)