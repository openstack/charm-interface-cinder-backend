#!/usr/bin/python

import json

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class CinderBackendProvides(RelationBase):

    scope = scopes.GLOBAL

    @hook('{provides:cinder-backend}-relation-joined')
    def cinder_backend_joined(self):
        conv = self.conversation()
        conv.set_state('{relation_name}.joined')
        self.set_state('{relation_name}.connected')
        self.set_state('{relation_name}.available')

    @hook('{provides:cinder-backend}-relation-{broken, departed}')
    def cinder_backend_departed(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.joined')
        self.remove_state('{relation_name}.available')
        self.remove_state('{relation_name}.connected')
        conv.set_state('{relation_name}.departing')

    def configure_principal(self, backend_name, configuration, stateless=None):
        """Send principle cinder-backend information.

        :param backend_name: Name of storage backend.
        :type backend_name: str
        :param configuration: List of pairs of key value tuples to be used in
                              backend section of config.
        :type configuration: [(k1,v1), (k2,v2),...]
        :param stateless: Whether backend is stateless.
        :type stateless: bool
        """
        conv = self.conversation()

        subordinate_configuration = {
            "cinder": {
                "/etc/cinder/cinder.conf": {
                    "sections": {
                        backend_name: configuration
                    }
                }
            }
        }
        conv.set_remote(
            backend_name=backend_name,
            stateless=stateless,
            subordinate_configuration=json.dumps(subordinate_configuration))
