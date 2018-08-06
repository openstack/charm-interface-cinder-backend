# Overview

Basic interface for sending Cinder subordinate backend configuration to
principle Cinder charms.

# Usage

## Requires

This interface layer will set the following state:

  * `{relation_name}.connected` The relation is established, but the charm may
    not have provided any backend information.

For example, the subordinate would handle the `cinder-backend.connected` state
with something like:

```python
@when('cinder-backend.connected')
def configure_cinder(cinder_principal):
    config = {'api-endpoint': '1.2.3.4',
              'admin-username': 'admin',
              'admin-password': 'openstack',
              'api-version': '1.0'}
    cinder_principle.configure_principal(
      backend_name='my_backend', configuration=config)
```


# Contact Information

- <michael.skalka@canonical.com>
