#!/usr/bin/python

import json

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes

import charmhelpers.core.hookenv as hookenv


class CinderBackendProvides(RelationBase):

    scope = scopes.GLOBAL

    @hook('{provides:cinder-backend}-relation-joined')
    def cinder_backend_joined(self):
        conv = self.conversation()
        conv.set_state('{relation_name}.joined')
        conv.set_state('{relation_name}.connected')
        conv.set_state('{relation_name}.available')

    @hook('{provides:cinder-backend}-relation-{broken, departed}')
    def cinder_backend_departed(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.joined')
        conv.remove_state('{relation_name}.available')
        conv.remove_state('{relation_name}.connected')
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

    def publish_releases_packages_map(self, releases_packages_map):
        """Publish releases_packages_map.

        :param releases_packages_map: Map of releases and packages
        :type releases_packages_map: Dict[str,Dict[str,List[str]]]
        """
        # NOTE: To allow relation updates outside of relation hook execution,
        # e.g. upgrade-charm hook, we need to revert to classic hookenv tools.
        for rid in hookenv.relation_ids(self.relation_name):
            relation_info = {
                'releases-packages-map': json.dumps(
                    releases_packages_map, sort_keys=True)
            }
            hookenv.relation_set(rid, relation_info)
