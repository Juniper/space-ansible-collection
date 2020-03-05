# Juniper Junos Space Ansible Collection

## Tech Preview

This is the [Ansible
Collection](https://www.ansible.com/resources/webinars-training/collections-future-of-how-ansible-content-is-handled)
provided by the [Juniper Network Automation
Team](https://github.com/juniper) for automating actions in [Junos Space](https://www.juniper.net/us/en/products-services/network-management/junos-space-platform/).

This Collection is meant for distribution via
[Ansible Galaxy](https://galaxy.ansible.com/) as is available for all

### Current Modules

* `space_device_info` - Obtain information about one or many space Rules, with filter options
* `space_device` - This module allows for addition, deletion, or modification of devices in Junos Space
* `space_queue` - Manage state of Space's HornetQ Queues
* `sd_address_info` - Obtain information about one or many SD address objects, with filter options
* `sd_address` - This module allows for addition, deletion, or modification of addresses in SD
* `sd_device_info` - Obtain information about one or many SD devices, with filter options
* `sd_service_info` - Obtain information about one or many SD service objects, with filter options
* `sd_service` - This module allows for addition, deletion, or modification of services in SD
* `sd_nat_policy_info` - Obtain information about one or many SD NAT policies
* `sd_nat_rule_info` - Obtain information for all SD NAT rules for a given policy ID or a specific rule given a rule ID
* `sd_fw_policy_info` - Obtain information about one or many SD firewall policies

### Using Junos Space Ansible Collection

An example for using this collection to manage a log source with [Junos Space](https://www.juniper.net/us/en/products-services/network-management/junos-space-platform/) is as follows.

`inventory.ini` (Note the password should be managed by a [Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html) for a production environment.
```
[space]
space01 ansible_host=192.168.30.1

[space:vars]
ansible_network_os=juniper.space.space
ansible_connection=httpapi
ansible_user=super
ansible_password=SuperPassword
ansible_httpapi_port=34003
ansible_httpapi_validate_certs=False
ansible_httpapi_use_ssl=True
```

#### Define your collection search path at the Play level

Below we specify our collection at the Play level which allows us to use the
`space_device_info` module without specifying the need for the
Ansible Collection Namespace.

`space_with_collections_example.yml`
```
---
- name: Space API Example
  hosts: all
  connection: httpapi
  gather_facts: no
  collections:
    - juniper.space

  tasks:
    - name: All devices
      space_device_info:
```

#### Define your collection search path at the Block level

Below we use the [`block`](https://docs.ansible.com/ansible/latest/user_guide/playbooks_blocks.html) level keyword, we are able to use the `space_device_info` module without the need for the Ansible Collection Namespace.

`space_with_collections_block_example.yml`
```
---
- name: Space API Example
  hosts: all
  connection: httpapi
  gather_facts: no

  tasks:
    - name: Space Block Example
      block:
        - name: All devices
          space_device_info:

      collections:
        - juniper.space
```

### Directory Structure

* `docs/`: local documentation for the collection
* `license.txt`: optional copy of license(s) for this collection
* `galaxy.yml`: source data for the MANIFEST.json that will be part of the collection package
* `playbooks/`: playbooks reside here
  * `tasks/`: this holds 'task list files' for `include_tasks`/`import_tasks` usage
* `plugins/`: all ansible plugins and modules go here, each in its own subdir
  * `modules/`: ansible modules
  * `lookups/`: lookup plugins
  * `filters/`: Jinja2 filter plugins
  * ... rest of plugins
* `README.md`: information file (this file)
* `roles/`: directory for ansible roles
* `tests/`: tests for the collection's content

### Planned Modules

* `sd_nat_policy`
* `sd_nat_rule`
* `sd_fw_policy`
* `sd_fw_rule`
* `space_keys*`