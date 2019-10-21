# Juniper Junos Space Ansible Collection

## Tech Preview

This is the [Ansible
Collection](https://www.ansible.com/resources/webinars-training/collections-future-of-how-ansible-content-is-handled)
provided by the [Juniper Network Automation
Team](https://github.com/juniper) for automating actions in [Junos Space](https://www.juniper.net/us/en/products-services/network-management/junos-space-platform/).

This Collection is meant for distribution via
[Ansible Galaxy](https://galaxy.ansible.com/) as is available for all
[Ansible](https://github.com/ansible/ansible) users to utilize, contribute to,
and provide feedback about.

### Using Junos Space Ansible Collection

An example for using this collection to manage a log source with [Junos Space](https://www.juniper.net/us/en/products-services/network-management/junos-space-platform/) is as follows.

`inventory.ini` (Note the password should be managed by a [Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html) for a production environment.
```
[space]
space01 ansible_host=66.129.235.5

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

* `space_device`: managing device state (discovering, removing)
* `address_object`: managing shared address objects including variable, groups
* `nat_policy`
* `nat_rule`