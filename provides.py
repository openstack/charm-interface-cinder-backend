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

    def configure_principal(self, backend_name, configuration):
        """Send principle cinder-backend information"""
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

        conv.set_remote(backend_name=backend_name
                        subordinate_configuration=configuration)
