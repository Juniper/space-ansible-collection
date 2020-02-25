#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Michael Tucker (@mtucker502)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.juniper.space.plugins.module_utils.space import ObjectManager
from ansible_collections.juniper.space.plugins.module_utils.space import ObjectConfig

class SDServiceConfig(ObjectConfig):
    uris = dict(get="/api/juniper/sd/service-management/v5/services",
            get_by_id="/api/juniper/sd/policy-management/nat/policies/{policy_id}/rules"
    )
    headers = dict(get={"Accept": "application/json"},
                get_by_id={"Accept": "application/json"}
    )
    list_keys = ['services', 'service']
    filter_operator = 'contains'
    formatter = dict(get=True,
                    get_by_id=True
    )

class SDServiceMgr(ObjectManager):
    def __init__(self, **kwargs):
        super(eval(self.__class__.__name__), self).__init__(config=SDServiceConfig, **kwargs)