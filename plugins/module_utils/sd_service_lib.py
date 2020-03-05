#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, Michael Tucker (@mtucker502)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.juniper.space.plugins.module_utils.space import ObjectManager
from ansible_collections.juniper.space.plugins.module_utils.space import ObjectConfig

class SDServiceConfig(ObjectConfig):
    uris = dict(get="/api/juniper/sd/service-management/v5/services",
            get_by_id="/api/juniper/sd/service-management/v5/services",
            create="/api/juniper/sd/service-management/v5/services",
            delete="/api/juniper/sd/service-management/v5/services",
            update="/api/juniper/sd/service-management/v5/services"
    )
    headers = dict(get={"Accept": "application/json"},
                get_by_id={"Accept": "application/json"},
                create={"Accept": "application/json", "Content-Type": "application/json"},
                delete=None,
                update={"Accept": "application/json", "Content-Type": "application/json"}
    )
    list_keys = ['services', 'service']
    filter_operator = 'contains'
    filters = ['name']

class SDServiceMgr(ObjectManager):
    def __init__(self, **kwargs):
        super(eval(self.__class__.__name__), self).__init__(config=SDServiceConfig, **kwargs)


    def _body_builder(self, body_parts, **kwargs):
        body = dict(
            service = {
                "name" : body_parts["name"],
                "description" : body_parts["description"],
                "is-group" : body_parts["is-group"]
            }
        )

        protocol_numbers = dict(
            PROTOCOL_TCP=6,
            PROTOCOL_UDP=17,
            PROTOCOL_ICMP=1,
            PROTOCOL_ICMPV6=58
        )

        # Add service-refs if necessary
        if body_parts["is-group"]:
            service_refs = []
            for member in body_parts["members"]:
                response = self.get_one(name=member)
                if response is not None:
                    # service_refs.append(dict(name=response[0]['name'], uuid=response[0]['uuid']))

                    # Pop keys to make retrieved protocol body match expected member format which is less verbose
                    response[0].pop('edit-version', None)
                    response[0].pop('id_perms', None)
                    response[0].pop('protocols', None)
                    response[0].pop('update_number', None)
                    response[0].pop('uri', None)

                    # # Add required keys
                    # response[0]['id'] = int(response[0]['uuid'])
                    # response[0]['href'] = response[0]['uri'][0:-1]
                    service_refs.append(response[0])
                else:
                    self.space_request.module.fail_json(msg="Could not find member with name: {}".format(member))
            body['service']['service_refs'] = service_refs

        elif not body_parts["is-group"]:
            body['service']['definition_type'] = body_parts["definition_type"]

            if body['service'].get('application-services'):
                body['service']['application-services'] = body_parts["application-services"]

            #init protocol list
            body['service']['protocols'] = dict(
                protocol=[]
            )

            for protocol in body_parts['protocols']:
                protocol_type = 'PROTOCOL_{}'.format(protocol.pop('protocol').upper())
                protocol['protocol-type'] = protocol_type
                if protocol_type == 'PROTOCOL_OTHER':
                    if not protocol['protocol-number']:
                        module.fail_json(msg="You must specify a protocol_number when protocol=other!")
                else:
                    protocol['protocol-number'] = protocol_numbers[protocol_type]

                if not protocol.get('inactivity-timeout'):
                    protocol.pop('inactivity-timeout', None)
                    protocol.pop('inactivity-time-type', None)
                
                if not protocol.get('src-port'):
                    protocol.pop('src-port', None) 
                
                if not protocol.get('dst-port'):
                    protocol.pop('dst-port', None) 

                body['service']['protocols']['protocol'].append(protocol)
            
        return body
